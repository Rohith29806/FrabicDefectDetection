
from pathlib import Path
import shutil
import math

SOURCE = Path("datasets/BDFD9_original")
DEST = Path("datasets/BDFD9_detection")

SPLITS = ["train", "valid", "test"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

CLASS_NAMES = [
    "DropStitch",
    "Hole",
    "Horizontal Mark",
    "Knot",
    "Oil Spot",
    "Setup",
    "Slub",
    "Vertical LineMark",
    "Yurn Dust"
]

EPSILON = 1e-4

def convert_annotation(line):
    values = line.split()
    if len(values) < 5:
        raise ValueError("Too few annotation values")

    class_id = int(values[0])
    coords = [float(v) for v in values[1:]]

    if not 0 <= class_id < len(CLASS_NAMES):
        raise ValueError("Invalid class ID")

    if not all(math.isfinite(v) for v in coords):
        raise ValueError("Non-finite coordinate")

    # Existing YOLO bounding box
    if len(coords) == 4:
        x, y, w, h = coords

        if w <= 0 or h <= 0:
            raise ValueError("Non-positive box size")

        x1, y1 = x - w / 2, y - h / 2
        x2, y2 = x + w / 2, y + h / 2

    # YOLO segmentation polygon -> enclosing box
    elif len(coords) >= 6 and len(coords) % 2 == 0:
        xs = coords[0::2]
        ys = coords[1::2]

        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)

    else:
        raise ValueError("Unsupported annotation format")

    # Reject substantial coordinate errors.
    if min(x1, y1) < -EPSILON:
        raise ValueError("Box extends significantly beyond left/top")

    if max(x2, y2) > 1 + EPSILON:
        raise ValueError("Box extends significantly beyond right/bottom")

    # Clip tiny numerical overflows.
    x1 = max(0.0, min(1.0, x1))
    y1 = max(0.0, min(1.0, y1))
    x2 = max(0.0, min(1.0, x2))
    y2 = max(0.0, min(1.0, y2))

    if x2 <= x1 or y2 <= y1:
        raise ValueError("Empty bounding box")

    new_x = (x1 + x2) / 2
    new_y = (y1 + y2) / 2
    new_w = x2 - x1
    new_h = y2 - y1

    return (
        f"{class_id} {new_x:.8f} {new_y:.8f} "
        f"{new_w:.8f} {new_h:.8f}"
    )


DEST.mkdir(parents=True, exist_ok=True)

total_images = 0
total_annotations = 0
converted_polygons = 0
skipped = []

for split in SPLITS:
    source_split = SOURCE / split

    output_images = DEST / split / "images"
    output_labels = DEST / split / "labels"

    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    for image in source_split.rglob("*"):
        if not image.is_file():
            continue

        if image.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        # Locate matching labels folder.
        if image.parent.name.lower() != "images":
            continue

        class_folder = image.parent.parent
        label_file = class_folder / "labels" / (image.stem + ".txt")

        if not label_file.exists():
            skipped.append(f"Missing label: {image}")
            continue

        output_name = (
            f"{class_folder.parent.name}_{class_folder.name}_{image.name}"
        )

        try:
            lines = label_file.read_text(
                encoding="utf-8-sig"
            ).splitlines()

            converted = []

            for line in lines:
                if not line.strip():
                    continue

                values = line.split()
                if len(values) > 5:
                    converted_polygons += 1

                converted.append(convert_annotation(line))
                total_annotations += 1

            shutil.copy2(image, output_images / output_name)

            output_label = (
                output_labels / (Path(output_name).stem + ".txt")
            )
            output_label.write_text(
                "\n".join(converted) + "\n",
                encoding="utf-8"
            )

            total_images += 1

        except Exception as error:
            skipped.append(f"{image}: {error}")

# Create YOLO configuration.
yaml_content = (
    f"path: {DEST.resolve().as_posix()}\n"
    "train: train/images\n"
    "val: valid/images\n"
    "test: test/images\n"
    f"nc: {len(CLASS_NAMES)}\n"
    "names:\n"
)

for index, name in enumerate(CLASS_NAMES):
    yaml_content += f"  {index}: '{name}'\n"

(DEST / "data.yaml").write_text(yaml_content, encoding="utf-8")

print("\n===== DATASET PREPARATION =====")
print("Images copied:", total_images)
print("Annotations converted:", total_annotations)
print("Polygon annotations converted:", converted_polygons)
print("Skipped files:", len(skipped))

for item in skipped[:20]:
    print(item)

print("\nOutput:", DEST.resolve())
