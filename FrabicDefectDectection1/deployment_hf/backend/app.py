
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid

from backend.predict import predict_image
from backend.detect import detect_defects

app = FastAPI(title="Fabric Defect Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
UPLOAD_DIR = ROOT_DIR / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

ALLOWED_DATASETS = ["FDD", "TILDA", "ZD001"]
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "message": "Fabric Defect Detection API is running",
        "classification": "/predict",
        "object_detection": "/detect"
    }


def validate_image(image):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG or PNG image"
        )

    extension = Path(image.filename or "").suffix.lower()

    if extension not in [".jpg", ".jpeg", ".png"]:
        extension = ".jpg"

    return extension


async def save_upload(image, image_path):
    contents = await image.read(MAX_UPLOAD_BYTES + 1)

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image must be 10 MB or smaller"
        )

    image_path.write_bytes(contents)


@app.post("/predict")
async def predict(
    dataset_name: str = Form(...),
    image: UploadFile = File(...)
):
    if dataset_name not in ALLOWED_DATASETS:
        raise HTTPException(
            status_code=400,
            detail="Invalid dataset name"
        )

    extension = validate_image(image)
    image_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    try:
        await save_upload(image, image_path)

        return predict_image(str(image_path), dataset_name)

    finally:
        image.file.close()
        if image_path.exists():
            image_path.unlink()


@app.post("/detect")
async def detect(image: UploadFile = File(...)):
    extension = validate_image(image)
    image_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    try:
        await save_upload(image, image_path)

        result = detect_defects(str(image_path))
        return result

    finally:
        image.file.close()
        if image_path.exists():
            image_path.unlink()


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
