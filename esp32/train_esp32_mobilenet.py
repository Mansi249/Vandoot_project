"""
TinyML training script for VanDoot ESP32 camera model.

Model:
MobileNetV1 (alpha=0.25) – lightweight CNN for embedded inference.

Input:
96x96 RGB images

Classes:
0_fire
1_human
2_animal
3_empty

Output:
INT8 quantized TFLite model for ESP32 deployment.
"""

import tensorflow as tf
import numpy as np
import os
import pathlib

# ==========================================
# BASIC SETTINGS
# ==========================================

# Dataset folder created after resizing images
DATASET_PATH = "VanDoot_Ready_96x96"

# Image size used for training
IMG_SIZE = 96

# Batch size for training
BATCH_SIZE = 32

# Number of training epochs
EPOCHS = 20   # increase later if accuracy needs improvement

# MobileNet width multiplier
# Smaller value = lighter model for ESP32
MODEL_ALPHA = 0.25

print(f"TensorFlow Version: {tf.__version__}")
print(f"Checking for GPU: {tf.config.list_physical_devices('GPU')}")

# ==========================================
# 1. LOAD DATASET
# ==========================================

print("\n[1] Loading Dataset...")

# Convert dataset path to pathlib object
data_dir = pathlib.Path(DATASET_PATH)

# Load training dataset (80%)
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE
)

# Load validation dataset (20%)
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE
)

# Get class names from folder structure
class_names = train_ds.class_names
print(f"Classes found: {class_names}")

# Improve dataset loading speed
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ==========================================
# 2. BUILD MODEL
# ==========================================

print("\n[2] Building MobileNetV1 (Alpha 0.25)...")

# Simple augmentation to make training data more varied
data_augmentation = tf.keras.Sequential([
  tf.keras.layers.RandomFlip("horizontal"),
  tf.keras.layers.RandomRotation(0.1),
  tf.keras.layers.RandomZoom(0.1),
])

# Rescale image pixels from 0–255 to 0–1
rescale = tf.keras.layers.Rescaling(1./255, input_shape=(IMG_SIZE, IMG_SIZE, 3))

# Load MobileNet base model
# Using ImageNet weights so model already understands general features
base_model = tf.keras.applications.MobileNet(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    alpha=MODEL_ALPHA,
    include_top=False,
    weights='imagenet'
)

# Freeze base layers for first training phase
base_model.trainable = False

# Final classification model
model = tf.keras.Sequential([
    rescale,
    data_augmentation,
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

# Compile model
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
    metrics=['accuracy']
)

# Print model summary
model.summary()

# ==========================================
# 3. TRAIN MODEL
# ==========================================

print("\n[3] Starting Training...")

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# ==========================================
# 4. CONVERT MODEL TO TFLITE
# ==========================================

print("\n[4] Converting to TFLite for ESP32...")

# Representative dataset used during quantization
def representative_data_gen():
    for input_value, _ in train_ds.take(100):
        yield [tf.cast(input_value, tf.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_data_gen

# Force INT8 operations (needed for microcontrollers)
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

# Input images are uint8
converter.inference_input_type = tf.uint8

# Output probabilities
converter.inference_output_type = tf.int8

# Convert model
tflite_model = converter.convert()

# Save tflite model
with open('vandoot_model.tflite', 'wb') as f:
    f.write(tflite_model)

print(f"\n[SUCCESS] Model saved: vandoot_model.tflite")
print(f"Size: {len(tflite_model) / 1024:.2f} KB")

# ==========================================
# 5. GENERATE C ARRAY FOR ESP32
# ==========================================

print("\n[5] Generating C Header file...")

# Convert model bytes to C array
def hex_to_c_array(model_data, model_name="vandoot_model"):

    c_str = ""
    c_str += "#include <cstdint>\n\n"
    c_str += f"unsigned int {model_name}_len = {len(model_data)};\n"
    c_str += f"unsigned char {model_name}[] = {{\n"

    hex_array = []

    for i, val in enumerate(model_data):
        hex_array.append(f"0x{val:02x}")

        if (i + 1) % 12 == 0:
            c_str += "  " + ", ".join(hex_array) + ",\n"
            hex_array = []

    if hex_array:
        c_str += "  " + ", ".join(hex_array) + "\n"

    c_str += "};\n"

    return c_str

# Save C file used in Arduino project
with open('model_data.cc', 'w') as f:
    f.write(hex_to_c_array(tflite_model))

print("[DONE] Saved 'model_data.cc'. This file goes into your ESP32 Arduino sketch.")
