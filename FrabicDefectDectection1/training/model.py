
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2


def build_model(num_classes, input_shape=(224, 224, 3)):

    inputs = layers.Input(shape=input_shape)

    # MobileNetV2 feature extractor
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet"
    )

    base_model.trainable = False

    features = base_model(inputs, training=False)

    # Dual-pooling channel attention
    channels = features.shape[-1]
    hidden_units = max(channels // 8, 1)

    avg_pool = layers.GlobalAveragePooling2D()(features)
    max_pool = layers.GlobalMaxPooling2D()(features)

    shared_dense_1 = layers.Dense(
        hidden_units, activation="relu"
    )
    shared_dense_2 = layers.Dense(
        channels, activation="sigmoid"
    )

    avg_attention = shared_dense_2(shared_dense_1(avg_pool))
    max_attention = shared_dense_2(shared_dense_1(max_pool))

    attention = layers.Add()([
        avg_attention,
        max_attention
    ])

    attention = layers.Reshape((1, 1, channels))(attention)

    features = layers.Multiply()([features, attention])

    # Classification head
    x = layers.GlobalAveragePooling2D()(features)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(
        num_classes, activation="softmax"
    )(x)

    model = Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model
