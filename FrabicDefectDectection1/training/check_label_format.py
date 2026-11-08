
from pathlib import Path
from collections import Counter

ROOT = Path("datasets/BDFD9_original")

issues = []
formats = Counter()
classes = Counter()

for split in ["train", "valid", "test"]:
    for file in (ROOT / split).rglob("*.txt"):
        if file.parent.name.lower() != "labels":
            continue

        for line_no, line in enumerate(
            file.read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            values = line.split()
            if not values:
                continue

            try:
                cls = int(values[0])
                coords = list(map(float, values[1:]))
                classes[cls] += 1

                if len(coords) == 4:
                    formats["Bounding box"] += 1
                    x, y, w, h = coords

                    violations = {
                        "left": max(0, -(x - w / 2)),
                        "right": max(0, x + w / 2 - 1),
                        "top": max(0, -(y - h / 2)),
                        "bottom": max(0, y + h / 2 - 1),
                        "width": max(0, -w, w - 1),
                        "height": max(0, -h, h - 1),
                    }

                    violations = {
                        k: v for k, v in violations.items() if v > 1e-9
                    }

                    if violations:
                        issues.append(
                            (split, file.name, line_no, cls, violations)
                        )

                elif len(coords) >= 6 and len(coords) % 2 == 0:
                    formats["Segmentation polygon"] += 1
                    if any(not 0 <= v <= 1 for v in coords):
                        issues.append(
                            (split, file.name, line_no, cls, "Invalid polygon")
                        )
                else:
                    issues.append(
                        (split, file.name, line_no, cls, "Unexpected format")
                    )

            except (ValueError, OverflowError):
                issues.append(
                    (split, file.name, line_no, "Invalid values")
                )

print("FORMATS:", dict(formats))
print("CLASS COUNTS:", dict(sorted(classes.items())))
print("TOTAL ISSUES:", len(issues))
print("\nFIRST 20 ISSUES:")

for issue in issues[:20]:
    print(issue)
