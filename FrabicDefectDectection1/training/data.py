
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16


def load_dataset(dataset_name):

    dataset_path = f"datasets/{dataset_name}"

    train_path = f"{dataset_path}/train"
    val_path = f"{dataset_path}/val"

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_path,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=True,
        seed=42
    )

    class_names = train_ds.class_names

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_path,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        class_names=class_names,
        shuffle=False
    )

    # Apply MobileNetV2 preprocessing
    def preprocess(images, labels):
        images = preprocess_input(images)
        return images, labels

    train_ds = train_ds.map(
        preprocess,
        num_parallel_calls=tf.data.AUTOTUNE
    )

    val_ds = val_ds.map(
        preprocess,
        num_parallel_calls=tf.data.AUTOTUNE
    )

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, class_names
