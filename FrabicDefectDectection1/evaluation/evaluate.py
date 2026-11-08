
import numpy as np
import tensorflow as tf

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

from training.data import load_dataset

DATASETS = ["FDD", "TILDA", "ZD001"]

for name in DATASETS:

    print("\n" + "=" * 45)
    print("Evaluating:", name)
    print("=" * 45)

    # Load validation dataset
    _, val_ds, class_names = load_dataset(name)

    # Load trained model
    model_path = f"models/{name}_model.keras"
    model = tf.keras.models.load_model(model_path)

    # Generate predictions
    predictions = model.predict(val_ds)
    predicted_labels = np.argmax(predictions, axis=1)

    # Get actual labels
    actual_labels = np.concatenate([
        labels.numpy() for _, labels in val_ds
    ])

    # Calculate accuracy
    accuracy = accuracy_score(actual_labels, predicted_labels)

    print("Accuracy:", round(accuracy * 100, 2), "%")

    print("\nClassification Report:")
    print(classification_report(
        actual_labels,
        predicted_labels,
        labels=range(len(class_names)),
        target_names=class_names,
        zero_division=0
    ))

    print("Confusion Matrix:")
    print(confusion_matrix(
        actual_labels,
        predicted_labels,
        labels=range(len(class_names))
    ))

print("\nAll evaluations completed!")
