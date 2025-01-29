from flask import Flask, request, send_file
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import io

# Initialize Flask app
app = Flask(__name__)

# Load the trained model
model = load_model("colorized.keras")

# Define the image size (should match the model input size)
image_size = (128, 128)  # Replace with your model's input size


def preprocess_image(image):
    """Preprocess the input grayscale image."""
    image = image.resize(image_size).convert("L")  # Resize and convert to grayscale
    image = np.array(image).astype("float32") / 255.0  # Normalize to [0, 1]
    image = np.expand_dims(image, axis=-1)  # Add channel dimension (H, W, 1)
    image = np.expand_dims(image, axis=0)  # Add batch dimension (1, H, W, 1)
    return image


def postprocess_image(image):
    """Convert the model's RGB output to a displayable format."""
    image = np.squeeze(image, axis=0)  # Remove batch dimension
    image = (image * 255).astype("uint8")  # Convert to [0, 255]
    return Image.fromarray(image)  # Convert to PIL Image


@app.route("/colorize", methods=["POST"])
def colorize():
    """API endpoint to colorize a grayscale image."""
    if "image" not in request.files:
        return "No image file provided", 400

    # Get the uploaded image
    file = request.files["image"]
    try:
        # Open and preprocess the image
        image = Image.open(file)
        input_data = preprocess_image(image)

        # Predict the colorized image
        output_data = model.predict(input_data)

        # Postprocess the output to convert it to RGB image
        output_image = postprocess_image(output_data)

        # Save image to a bytes buffer
        img_io = io.BytesIO()
        output_image.save(img_io, format="PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return str(e), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
