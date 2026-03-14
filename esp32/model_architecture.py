"""
Model architecture used for VanDoot ESP32 vision detection.

Backbone:
MobileNetV1 (alpha = 0.25)

Input:
96x96 RGB image

Output classes:
0_fire
1_human
2_animal
3_empty

The trained model is later quantized to INT8 and exported
to TensorFlow Lite for deployment on ESP32.
"""

import tensorflow as tf

# Image input size used during training
IMG_SIZE = 96

# Number of output classes
NUM_CLASSES = 4

# MobileNet width multiplier (smaller = lighter model)
ALPHA = 0.25


def build_model():

    # Base MobileNet model
    base_model = tf.keras.applications.MobileNet(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        alpha=ALPHA,
        include_top=False,
        weights="imagenet"
    )

    # Freeze backbone layers for transfer learning
    base_model.trainable = False

    # Classification head
    model = tf.keras.Sequential([
        tf.keras.layers.Rescaling(1./255, input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(NUM_CLASSES, activation="softmax")
    ])

    return model


if __name__ == "__main__":
    model = build_model()
    model.summary()
