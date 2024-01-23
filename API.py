from flask import Flask, request, jsonify
from PIL import Image
import pillow_heif
from io import BytesIO

app = Flask(__name__)

def convert_heic_to_png(heic_data):
    try:
        heic_file = pillow_heif.read_heif(heic_data)
        image = Image.frombytes(
            heic_file.mode,
            heic_file.size,
            heic_file.data,
            "raw",
        )

        png_data = BytesIO()
        image.save(png_data, format='PNG')
        return png_data.getvalue()
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/convert', methods=['POST'])
def convert_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    heic_file = request.files['image']
    if heic_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if heic_file and heic_file.filename.endswith('.heic'):
        heic_data = heic_file.read()
        png_data = convert_heic_to_png(heic_data)
        if isinstance(png_data, bytes):
            return jsonify({"png_data": png_data.decode('latin-1')})
        else:
            return jsonify({"error": png_data}), 500
    else:
        return jsonify({"error": "Invalid file format. Please provide a HEIC image"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
