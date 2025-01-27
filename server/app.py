import os
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_file
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Path to the trained model
MODEL_PATH = "colorization_model.keras"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained model
model = load_model(MODEL_PATH, custom_objects={"mean_squared_error": MeanSquaredError})

# Allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocessing function
def preprocess_image(image_path, image_size=(128, 128)):
    # Load and resize the image
    bw_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    bw_image = cv2.resize(bw_image, image_size)
    bw_image = bw_image / 255.0  # Normalize
    bw_image = np.expand_dims(bw_image, axis=-1)  # Add channel dimension
    bw_image = np.expand_dims(bw_image, axis=0)  # Add batch dimension
    return bw_image

# Postprocessing function
def postprocess_prediction(l_channel, ab_channels, image_size=(128, 128)):
    l_channel = (l_channel[0, :, :, 0] * 255.0).astype(np.uint8)  # Convert back to 0-255 scale
    ab_channels = (ab_channels[0] * 128.0).astype(np.float32)

    # Combine L and AB channels into a LAB image
    lab_image = np.zeros((image_size[0], image_size[1], 3), dtype=np.float32)
    lab_image[:, :, 0] = l_channel
    lab_image[:, :, 1:] = ab_channels

    # Convert LAB to RGB
    rgb_image = cv2.cvtColor(lab_image.astype(np.uint8), cv2.COLOR_LAB2RGB)
    return rgb_image

# Route to upload and colorize images
@app.route("/colorize", methods=["POST"])
def colorize_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Preprocess the image
    bw_image = preprocess_image(filepath)

    # Run model prediction
    ab_prediction = model.predict(bw_image)

    # Postprocess to get colorized image
    l_channel = bw_image
    colorized_image = postprocess_prediction(l_channel, ab_prediction)

    # Convert the image to send as a response
    pil_image = Image.fromarray(colorized_image)
    img_io = BytesIO()
    pil_image.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
