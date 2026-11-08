
import os
import json
import numpy as np
import tensorflow as tf

from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# Project folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

IMAGE_SIZE = (224, 224)

# Cache loaded models
model_cache = {}
class_cache = {}


def load_model_and_classes(dataset_name):

    dataset_name = dataset_name.upper()

    if dataset_name not in ["FDD", "TILDA", "ZD001"]:
        raise ValueError("Invalid dataset name")

    if dataset_name not in model_cache:

        model_path = os.path.join(
            MODEL_DIR, f"{dataset_name}_model.keras"
        )

        class_path = os.path.join(
            MODEL_DIR, f"{dataset_name}_classes.json"
        )

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        if not os.path.exists(class_path):
            raise FileNotFoundError(f"Class file not found: {class_path}")

        model_cache[dataset_name] = tf.keras.models.load_model(
            model_path,
            compile=False
        )

        with open(class_path, "r") as file:
            class_cache[dataset_name] = json.load(file)

    return model_cache[dataset_name], class_cache[dataset_name]


def predict_image(image_path, dataset_name):

    model, class_names = load_model_and_classes(dataset_name)

    # Read and prepare image
    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMAGE_SIZE)

    image_array = np.array(image, dtype=np.float32)
    image_array = preprocess_input(image_array)

    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)

    # Predict
    predictions = model.predict(image_array, verbose=0)[0]

    predicted_index = int(np.argmax(predictions))

    predicted_class = class_names[predicted_index]
    confidence = float(predictions[predicted_index]) * 100

    probabilities = {
        class_names[i]: round(float(predictions[i]) * 100, 2)
        for i in range(len(class_names))
    }

    return {
        "dataset": dataset_name.upper(),
        "prediction": predicted_class,
        "confidence": round(confidence, 2),
        "probabilities": probabilities
    }
