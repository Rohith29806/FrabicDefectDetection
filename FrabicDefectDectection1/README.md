# FabricAI — Local VS Code Project

This is the existing Fabric Defect Detection project, prepared to run locally with its saved models. It includes a FastAPI backend, the HTML/CSS/JavaScript dashboard, YOLOv8n weights, and three MobileNetV2 classifiers.

## Run in VS Code on Windows

1. Open this project folder in VS Code.
2. Open **Terminal → New Terminal** (PowerShell).
3. Create a Python 3.12 virtual environment if you do not already have one:

   ```powershell
   py -3.12 -m venv .venv312
   ```

4. Install the project packages:

   ```powershell
   .\.venv312\Scripts\python.exe -m pip install --upgrade pip
   .\.venv312\Scripts\python.exe -m pip install -r requirements.txt
   ```

   First installation downloads PyTorch, TensorFlow and their dependencies. It can take several minutes and several gigabytes of disk space. No model training is needed.

5. Start the website and API:

   ```powershell
   .\.venv312\Scripts\python.exe -m uvicorn backend.app:app --reload
   ```

6. Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The backend and frontend use the same local server. API documentation is at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

You can also run `run_local.ps1` from the VS Code terminal. It creates `.venv312` if needed, installs dependencies if FastAPI is missing, then launches the local app.

## Inspection modes

- **YOLOv8**: object detection with confidence values and bounding boxes. The selected checkpoint is `runs/detect/runs/detect/bdfd9/weights/best.pt`.
- **MobileNetV2**: select FDD, TILDA or ZD001 for whole-image classification.
- **PDF report**: available after a successful inspection; includes the result, inspection image, and a note that prediction confidence is not overall model accuracy.
- **History and dashboard totals**: stored in the browser's local storage for that browser profile. The dashboard shows up to the 100 most recent saved records.

## Model and data limitations

The MobileNetV2 classification subsets are synthetic and small. Their confidence values do not establish reliable performance on real factory images. YOLOv8 results are limited by the training data, image conditions, and confidence threshold; the detector is not guaranteed to identify every real-world defect. This project is an academic prototype, not an autonomous production quality-control system.

Reported YOLO metrics in `PROJECT_DOCUMENTATION.md` are project-reported results and were not independently reproduced during packaging. Do not interpret an individual prediction confidence as model accuracy.

## Included and omitted files

The runnable project archive includes the backend, dashboard, saved inference models, API requirements, and project documentation. Python virtual environments are not included; create `.venv312` using the commands above. Raw BDFD9 source/processed images are omitted from the compact runnable archive because they are not needed for inference and occupy over 1.5 GB. The original project folder remains the source for those dataset and experiment files.
