import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, UpSampling2D, BatchNormalization, Activation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt

# 1. Create a data generator
# def data_generator(bw_folder, color_folder, image_size=(128, 128), batch_size=32):
def data_generator(bw_folder, color_folder, image_size=(128, 128), batch_size=16):
    bw_files = sorted(os.listdir(bw_folder))
    color_files = sorted(os.listdir(color_folder))

    while True:
        for i in range(0, len(bw_files), batch_size):
            bw_batch = []
            color_batch = []

            for j in range(i, min(i + batch_size, len(bw_files))):
                # Load BW image
                bw_img = cv2.imread(os.path.join(bw_folder, bw_files[j]), cv2.IMREAD_GRAYSCALE)
                bw_img = cv2.resize(bw_img, image_size)
                bw_img = bw_img / 255.0  # Normalize
                bw_batch.append(bw_img)

                # Load corresponding color image
                color_img = cv2.imread(os.path.join(color_folder, color_files[j]))
                color_img = cv2.resize(color_img, image_size)
                color_img = color_img / 255.0  # Normalize

                # Convert to LAB and split channels
                color_lab = cv2.cvtColor((color_img * 255).astype(np.uint8), cv2.COLOR_BGR2LAB)
                l_channel = color_lab[:, :, 0] / 255.0
                ab_channels = color_lab[:, :, 1:] / 128.0

                color_batch.append((l_channel[..., np.newaxis], ab_channels))

            # Prepare batches
            x_batch = np.array([item[0] for item in color_batch])  # L channel
            y_batch = np.array([item[1] for item in color_batch])  # AB channels

            yield x_batch, y_batch

# 2. Define the CNN model (same as before)
def build_colorization_model(input_shape):
    inputs = Input(shape=input_shape)

    # Encoder (downsampling)
    x = Conv2D(64, (3, 3), strides=2, padding="same")(inputs)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = Conv2D(128, (3, 3), strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = Conv2D(256, (3, 3), strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    # Bottleneck
    x = Conv2D(512, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    # Decoder (upsampling)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(256, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = UpSampling2D((2, 2))(x)
    x = Conv2D(128, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = UpSampling2D((2, 2))(x)
    outputs = Conv2D(2, (3, 3), activation="tanh", padding="same")(x)  # Output AB channels

    return Model(inputs, outputs)

# Build the model
input_shape = (128, 128, 1)  # Grayscale input
model = build_colorization_model(input_shape)
model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mean_squared_error"])

# 3. Train with data generator
bw_folder = os.path.join('data', 'sar')
color_folder = os.path.join('data', 'opt')
# batch_size = 32
batch_size = 16
steps_per_epoch = len(os.listdir(bw_folder)) // batch_size
# epochs = 50
epochs = 1

# Save checkpoints during training
checkpoint = ModelCheckpoint("colorization_model.keras", save_best_only=True, monitor="val_loss", mode="min")

train_gen = data_generator(bw_folder, color_folder, batch_size=batch_size)
val_gen = data_generator(bw_folder, color_folder, batch_size=batch_size)

history = model.fit(
    train_gen,
    validation_data=val_gen,
    steps_per_epoch=steps_per_epoch,
    validation_steps=steps_per_epoch // 10,
    epochs=epochs,
    callbacks=[checkpoint]
)

# 4. Visualize predictions
def visualize_results(model, bw_folder, color_folder, image_size=(128, 128), n_images=5):
    bw_files = sorted(os.listdir(bw_folder))
    color_files = sorted(os.listdir(color_folder))

    for i in range(n_images):
        # Load and preprocess a test image
        bw_img = cv2.imread(os.path.join(bw_folder, bw_files[i]), cv2.IMREAD_GRAYSCALE)
        bw_img = cv2.resize(bw_img, image_size)
        bw_img = bw_img / 255.0
        bw_input = bw_img[np.newaxis, :, :, np.newaxis]

        # Predict
        ab_pred = model.predict(bw_input)[0]
        l_channel = (bw_input[0, :, :, 0] * 255.0).astype(np.uint8)
        ab_channels = (ab_pred * 128.0).astype(np.float32)

        # Combine L and AB channels
        lab_image = np.zeros((image_size[0], image_size[1], 3), dtype=np.float32)
        lab_image[:, :, 0] = l_channel
        lab_image[:, :, 1:] = ab_channels

        # Convert LAB to RGB
        rgb_image = cv2.cvtColor(lab_image.astype(np.uint8), cv2.COLOR_LAB2RGB)

        # Display
        plt.subplot(2, n_images, i + 1)
        plt.imshow(rgb_image)
        plt.axis("off")

        # Display grayscale input
        plt.subplot(2, n_images, i + 1 + n_images)
        plt.imshow(l_channel, cmap="gray")
        plt.axis("off")

    plt.show()

# Visualize the results
visualize_results(model, bw_folder, color_folder)
