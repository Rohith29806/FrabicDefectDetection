
from pathlib import Path

ROOT = Path("datasets/BDFD9_detection")

removed = 0

for split in ["train", "valid", "test"]:
    labels_dir = ROOT / split / "labels"
    images_dir = ROOT / split / "images"

    for label in labels_dir.glob("*Unlabeled_NoAnnotation*.txt"):
        if label.read_text(encoding="utf-8-sig").strip():
            print("Not empty, preserving:", label.name)
            continue

        image_found = False

        for image in images_dir.glob(label.stem + ".*"):
            if image.suffix.lower() in {
                ".jpg", ".jpeg", ".png", ".webp"
            }:
                image.unlink()
                image_found = True

        label.unlink()
        removed += 1

        print("Removed unlabelled sample:", label.name)
        if not image_found:
            print("WARNING: Matching image not found!")

print("\nTotal unlabelled samples removed:", removed)
