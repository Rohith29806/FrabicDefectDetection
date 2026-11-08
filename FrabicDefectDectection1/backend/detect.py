from pathlib import Path
import os
import torch
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = Path(os.environ.get(
    "YOLO_MODEL_PATH",
    ROOT / "runs" / "detect" / "runs" /
    "detect" / "bdfd9" / "weights" / "best.pt"
))

model = YOLO(str(MODEL_PATH))


def detect_defects(image_path):
    results = model.predict(
        source=str(image_path),
        imgsz=640,
        conf=0.25,
        device=0 if torch.cuda.is_available() else "cpu",
        verbose=False
    )

    result = results[0]
    detections = []

    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            coordinates = box.xyxy[0].tolist()

            detections.append({
                "class_id": class_id,
                "class_name": result.names[class_id],
                "confidence": round(confidence * 100, 2),
                "box": [round(x, 2) for x in coordinates]
            })

    return {
        "total_defects": len(detections),
        "detections": detections
    }
