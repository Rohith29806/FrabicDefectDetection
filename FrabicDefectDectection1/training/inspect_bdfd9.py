
from pathlib import Path
from collections import Counter

ROOT = Path("datasets/BDFD9_original")
SPLITS = ["train", "valid", "test"]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
NUM_CLASSES = 9

for split in SPLITS:
    split_dir = ROOT / split

    images = [
        p for p in split_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    label_counts = Counter()
    missing_labels = []
    empty_labels = []
    invalid_labels = []
    invalid_boxes = []
    matched = 0

    for image in images:
        # Finds the labels folder next to the images folder
        if image.parent.name.lower() == "images":
            label_path = image.parent.parent / "labels" / (
                image.stem + ".txt"
            )
        else:
            label_path = image.parent / (image.stem + ".txt")

        if not label_path.exists():
            missing_labels.append(image.name)
            continue

        matched += 1
        content = label_path.read_text().strip()

        if not content:
            empty_labels.append(image.name)
            continue

        for line_no, line in enumerate(content.splitlines(), 1):
            try:
                values = line.split()

                if len(values) != 5:
                    raise ValueError("Expected 5 values")

                class_id = int(values[0])
                x, y, w, h = map(float, values[1:])

                if not 0 <= class_id < NUM_CLASSES:
                    raise ValueError("Invalid class ID")

                label_counts[class_id] += 1

                if not (
                    0 <= x <= 1 and 0 <= y <= 1
                    and 0 < w <= 1 and 0 < h <= 1
                    and x - w / 2 >= 0
                    and y - h / 2 >= 0
                    and x + w / 2 <= 1
                    and y + h / 2 <= 1
                ):
                    invalid_boxes.append(image.name)

            except (ValueError, IndexError):
                invalid_labels.append(
                    f"{image.name}, line {line_no}"
                )

    print(f"\n===== {split.upper()} =====")
    print("Images:", len(images))
    print("Matched labels:", matched)
    print("Missing labels:", len(missing_labels))
    print("Empty labels:", len(empty_labels))
    print("Invalid labels:", len(invalid_labels))
    print("Invalid boxes:", len(invalid_boxes))
    print("Class distribution:", dict(label_counts))
