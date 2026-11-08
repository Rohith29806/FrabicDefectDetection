# Hybrid Deep Learning Frameworks for Fabric Defect Detection in Smart Garment Manufacturing

## Abstract

This project combines two image-analysis approaches for fabric inspection. A trained YOLOv8n detector localizes defects and returns class labels, confidence values, and image-coordinate bounding boxes. Separate MobileNetV2 classifiers with a dual-pooling channel-attention head classify images from the FDD, TILDA, and ZD001 subsets. A FastAPI service exposes both models to a browser dashboard, which previews images, displays results, records recent inspections in browser local storage, and generates PDF reports. The classification subsets are synthetic and small; classification outputs are experimental and do not establish reliability on factory images.

## Introduction

Visual fabric inspection is used to identify surface defects before garments are produced. Manual inspection can be time-consuming and may vary between inspectors. Computer-vision models can assist by prioritizing images and locating candidate defects. This project demonstrates a small local inspection workflow using object detection and whole-image classification. It is an academic prototype and should not be treated as an autonomous production quality-control system.

## Problem Statement

Fabric defects may differ in appearance, scale, and location. A useful inspection prototype should both locate visible defect candidates and classify an image when bounding-box annotations are unavailable. It should present results clearly while distinguishing model confidence from measured model accuracy.

## Objectives

- Run YOLOv8n inference for nine BDFD9 defect categories.
- Run MobileNetV2 image classification for three separate dataset subsets.
- Provide a local browser interface for upload, preview, result display, and inspection history.
- Display detection boxes and confidence values, and export an inspection summary to PDF.
- Document dataset provenance and evaluation limits without overstating model performance.

## Literature Survey

MobileNetV2 uses inverted residual blocks and linear bottlenecks to build a compact image model. This project uses it as a frozen feature extractor and adds a dual-pooling attention block and a dataset-specific classification head. The architectural motivation is described by Sandler et al. in [MobileNetV2: Inverted Residuals and Linear Bottlenecks](https://arxiv.org/abs/1801.04381).

YOLO-style detectors perform object localization and classification in a single inference workflow. The project uses Ultralytics YOLOv8 prediction results to obtain defect classes and box coordinates; see the [Ultralytics prediction documentation](https://docs.ultralytics.com/modes/predict) and [YOLOv8 model documentation](https://docs.ultralytics.com/models/yolov8). Ultralytics notes that YOLOv8 has no formal paper published by the maintainers, so the official documentation is cited for implementation behavior.

Fabric-defect research includes both traditional image processing and learned feature models, with dataset quality and variation remaining important concerns. Li et al. survey methods and datasets in [Fabric Defect Detection in Textile Manufacturing: A Survey of the State of the Art](https://onlinelibrary.wiley.com/doi/10.1155/2021/9948808). Results on one dataset or controlled images should not be assumed to generalize to other materials, lighting, cameras, or production conditions.

## System Architecture

```text
Browser dashboard (HTML/CSS/JavaScript)
  ├─ image upload and preview
  ├─ YOLOv8 detection ── POST /detect ── FastAPI ── best.pt
  ├─ MobileNetV2 classification ── POST /predict ── FastAPI ── dataset model
  ├─ results, confidence chart, detection canvas, localStorage history
  └─ jsPDF report generation in the browser
```

The browser sends the selected image as multipart form data to the same host that serves the dashboard. The API stores each upload temporarily, runs inference, and removes the temporary file in a `finally` block. Detection and classification models are loaded by the backend modules. PDF construction happens in the browser; the report includes the original image or the rendered detection image when available. The dashboard is served at `/`, while `/health` reports API status and `/docs` provides Swagger UI.

## Methodology

### Detection

The selected detector is YOLOv8n with 640-pixel inference size and a 0.25 confidence threshold. The backend reads the trained weights from `runs/detect/runs/detect/bdfd9/weights/best.pt`, then returns each detected class, confidence percentage, and `[x1, y1, x2, y2]` coordinates in source-image pixels. The frontend draws those coordinates over the uploaded image.

### Classification

The classifier input is resized to 224 × 224 RGB and passed through MobileNetV2 preprocessing. `training/model.py` uses ImageNet-pretrained MobileNetV2 as a frozen feature extractor, combines global average and max pooled channel descriptors through shared dense layers, multiplies the resulting attention weights into the feature map, and applies a softmax classification head. There are separate saved models and class mappings for FDD, TILDA, and ZD001.

## Dataset Description

### BDFD9 detection

The project contains 1,127 processed detector images across train, validation, and test folders (804, 215, and 108 files respectively). The nine configured classes are DropStitch, Hole, Horizontal Mark, Knot, Oil Spot, Setup, Slub, Vertical LineMark, and Yarn Dust. The dataset config now relies on its own directory, rather than a stale absolute path from a different computer.

### Classification subsets

The repository contains 180 FDD images, 192 TILDA images, and 180 ZD001 images (552 total). These project subsets are synthetic, as recorded in the project brief. FDD classes are `defect_free`, `lines`, and `stain`; TILDA classes are `hole`, `objects`, `oil_spot`, and `thread_error`; ZD001 classes are `local_defects`, `warp_direction`, and `weft_direction`. These class mappings are stored in `models/*_classes.json`. Synthetic data and small sample counts limit conclusions about performance on real production imagery.

## Model Implementation

- **Detector:** `backend/detect.py` loads the selected YOLOv8n checkpoint, predicts at image size 640, uses CUDA when available and CPU otherwise, and returns box coordinates and confidence percentages. The selected model is retained.
- **Classifiers:** `training/model.py` defines the MobileNetV2 plus dual-pooling attention architecture. `backend/predict.py` loads the corresponding `.keras` file and class mapping on first use and caches it.
- **API:** `backend/app.py` serves the dashboard at `GET /`, reports API status at `GET /health`, and provides `POST /detect` and `POST /predict`. Accepted upload types are JPG/JPEG and PNG, with a 10 MB limit. Classification requires a `dataset_name` form field with FDD, TILDA, or ZD001.
- **Frontend:** `frontend/index.html`, `frontend/style.css`, and `frontend/script.js` implement the dashboard, uploads, result views, chart, local history, and PDF report.

## Results and Evaluation

The project brief reports these YOLOv8n test metrics at 640 pixels and 40 epochs: precision 80.9%, recall 81.7%, mAP50 90.6%, and mAP50–95 47.5%. These are project-reported figures and were not independently reproduced during this integration pass. The stated 800-pixel and YOLOv8s trials were worse; the selected YOLOv8n checkpoint remains unchanged.

Local CPU-mode API checks returned HTTP 200 from both model routes. The FDD sample returned `defect_free` at 53.23% prediction confidence. One BDFD9 test image returned zero detections; a second returned one Knot detection at 51.92% confidence with box coordinates `[794.57, 331.95, 907.9, 433.05]`. These are integration samples, not evaluation metrics. Confidence is not accuracy. The local dashboard page and backend status were verified in a browser, but a browser-driven upload and PDF download were not completed in this check.

The PDF includes the inspection time, filename, method, classification prediction/confidence or detection count and per-detection class/confidence/box coordinates, an inspection image, and a note distinguishing prediction confidence from overall model accuracy.

## Limitations

- The classification subsets are synthetic, small, and not evidence of real-factory generalization.
- YOLO detections depend on the training data, confidence threshold, imaging conditions, and defect visibility; the detector cannot be assumed to find every real defect.
- A single prediction confidence is not model accuracy or calibration.
- The project uses a local API address and is intended for local demonstration, not public deployment.
- Chart.js 4.4.7 and jsPDF 2.5.2 are stored under `frontend/vendor` so the dashboard and PDF generation do not depend on a live CDN request.
- The API routes and inference functions were checked, but a complete browser-driven upload, history-refresh, and PDF-download sequence was not verified. Follow the demonstration checklist in the target VS Code/Edge setup before presenting.

## Conclusion

The repository contains a working local prototype that combines YOLOv8 defect localization with MobileNetV2 classification, serves both through FastAPI, and provides a dashboard for inspection records and PDF export. The selected detector and existing classifier models have been preserved. API route inference was verified with local samples. Results should be interpreted as a project demonstration, particularly because the classification sets are synthetic and small.

## Future Scope

- Evaluate with larger, independently collected and carefully split real-fabric datasets.
- Report per-class precision, recall, F1, confusion matrices, mAP, and confidence calibration on a held-out test set.
- Add camera, lighting, fabric-type, and production-line variation to validation.
- Validate frontend behavior and PDF layout in the target browser at desktop and mobile widths.
- Consider API upload size limits, structured errors, and deployment security before exposing the service beyond localhost.

## Run Instructions

From the project root in PowerShell:

```powershell
.\.venv312\Scripts\python.exe -m uvicorn backend.app:app --reload
```

Open `http://127.0.0.1:8000/` to use the dashboard and `http://127.0.0.1:8000/docs` to inspect the API. Use the Python environment and dependencies in `requirements.txt`.

The curated Hugging Face Docker Space bundle is in `deployment_hf/`. It contains only the application, runtime dependencies, and inference models; it omits datasets, training outputs, and virtual environments. The default CPU hardware can run the models, but inference may be slower than on the local GPU.

The no-cost public preview is [FabricAI Inspection Preview](https://huggingface.co/spaces/madrt29/fabricai-inspection-preview), with its uploadable files in `deployment_hf_free/`. It is a static site: it previews images but does not run either model or produce inspection reports. Live predictions continue to require the local API or a compute-enabled host.

## Demonstration Checklist

- [ ] Start the API and confirm the dashboard shows **Connected**.
- [ ] Select YOLOv8, upload a JPG/PNG fabric image, and run an inspection.
- [ ] Confirm the result count, defect names, confidence values, and box coordinates match the annotated image.
- [ ] Download the PDF and verify its title, time, filename, method, detections, coordinates, image, and confidence caveat.
- [ ] Select MobileNetV2, choose FDD, TILDA, or ZD001, upload a JPG/PNG, and run an inspection.
- [ ] Confirm the predicted class, confidence, and class-distribution chart are displayed.
- [ ] Refresh the page and confirm recent inspection history remains.
- [ ] Confirm the dashboard counts saved local records (up to 100) and a zero-detection inspection shows `--` for latest confidence.
- [ ] Explain that classifier subsets are synthetic and confidence is not overall accuracy.
- [ ] Present reported detector metrics as project-reported unless a reproducible evaluation run is available.
