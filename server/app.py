import os
from flask import Flask, request, jsonify, send_file
import uuid
import cv2
import numpy as np
import tensorflow as tf

app = Flask(__name__)
model = tf.keras.models.load_model('sar.keras')

SIZE = 256
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/colorize', methods=['POST'])
def colorize():
    # Validation
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save original image
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], str(uuid.uuid4()) + '-' + image.filename)
    image.save(image_path)

    # Preprocessing: Read and resize the image
    img = cv2.imread(image_path).astype('float32')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Ensure RGB format
    img = cv2.resize(img, (SIZE, SIZE))  # Resize to model's expected size
    img = img / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # Prediction
    prediction = model.predict(img)

    # Post-processing: Convert back to an image format
    output_img = (prediction[0] * 255).astype("uint8")

    # Save processed image
    output_filename = os.path.join(app.config["OUTPUT_FOLDER"], "colorized_" + image.filename)
    cv2.imwrite(output_filename, cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR))

    return send_file(output_filename, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
