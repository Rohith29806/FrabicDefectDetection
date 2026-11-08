
from pathlib import Path
from backend.predict import predict_image

# Select the dataset to test
dataset_name = "FDD"

# Find an image from the validation folder
dataset_path = Path("datasets") / dataset_name / "val"

image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

images = [
    file for file in dataset_path.rglob("*")
    if file.is_file() and file.suffix.lower() in image_extensions
]

if not images:
    print("No test images found in:", dataset_path)
else:
    image_path = images[0]

    print("Testing image:", image_path)

    result = predict_image(str(image_path), dataset_name)

    print("\nPrediction Results")
    print("------------------")
    print("Dataset:", result["dataset"])
    print("Predicted defect:", result["prediction"])
    print("Confidence:", result["confidence"], "%")

    print("\nClass probabilities:")
    for class_name, probability in result["probabilities"].items():
        print(f"{class_name}: {probability}%")
