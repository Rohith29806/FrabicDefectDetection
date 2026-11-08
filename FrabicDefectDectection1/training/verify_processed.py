
from pathlib import Path
from collections import Counter

ROOT = Path("datasets/BDFD9_detection")
splits = ["train", "valid", "test"]

total_images = 0
total_labels = 0
errors = []

for split in splits:
    images_dir = ROOT / split / "images"
    labels_dir = ROOT / split / "labels"

    images = list(images_dir.glob("*"))
    images = [p for p in images if p.suffix.lower() in
              {".jpg", ".jpeg", ".png", ".webp"}]

    counts = Counter()

    for image in images:
        label = labels_dir / f"{image.stem}.txt"

        if not label.exists():
            errors.append(f"Missing: {label}")
            continue

        for line in label.read_text().splitlines():
            values = line.split()

            if len(values) != 5:
                errors.append(f"Invalid format: {label}")
                continue

            try:
                cls = int(values[0])
                x, y, w, h = map(float, values[1:])

                if not 0 <= cls < 9:
                    raise ValueError("Invalid class")

                if not (
                    0 <= x <= 1 and 0 <= y <= 1
                    and 0 < w <= 1 and 0 < h <= 1
                    and x - w/2 >= -1e-7
                    and y - h/2 >= -1e-7
                    and x + w/2 <= 1 + 1e-7
                    and y + h/2 <= 1 + 1e-7
                ):
                    raise ValueError("Invalid coordinates")

                counts[cls] += 1
                total_labels += 1

            except ValueError as error:
                errors.append(f"{label}: {error}")

    total_images += len(images)

    print(f"\n{split.upper()}")
    print("Images:", len(images))
    print("Annotations:", sum(counts.values()))
    print("Class counts:", dict(sorted(counts.items())))

print("\nTOTAL IMAGES:", total_images)
print("TOTAL ANNOTATIONS:", total_labels)
print("ERRORS:", len(errors))

for error in errors[:20]:
    print(error)

