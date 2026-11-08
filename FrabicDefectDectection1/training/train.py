
import os
import json
import argparse

from training.data import load_dataset
from training.model import build_model


def train_model(dataset_name, epochs):

    print(f"\nStarting training for {dataset_name}")

    # Load dataset
    train_ds, val_ds, class_names = load_dataset(dataset_name)

    # Create model
    model = build_model(num_classes=len(class_names))

    # Train model
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )

    # Create model output directory
    os.makedirs("models", exist_ok=True)

    # Save trained model
    model_path = f"models/{dataset_name}_model.keras"
    model.save(model_path)

    # Save class names
    class_path = f"models/{dataset_name}_classes.json"

    with open(class_path, "w") as file:
        json.dump(class_names, file)

    print(f"\nTraining completed for {dataset_name}")
    print(f"Model saved at: {model_path}")
    print(f"Classes saved at: {class_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset", required=True)
    parser.add_argument("--epochs", type=int, default=5)

    args = parser.parse_args()

    train_model(args.dataset, args.epochs)
