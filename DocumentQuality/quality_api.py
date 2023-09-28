from flask import Flask, request, jsonify
import cv2
import numpy as np
import pickle
import fitz
import tempfile

model_filename = 'xgboost_best_model.pkl'

label_mapping = {0: 'Bad', 1: 'Good', 2: 'Very Bad', 3: 'Very Good'}

with open(model_filename, 'rb') as model_file:
    loaded_model = pickle.load(model_file)


app = Flask(__name__)


def extract_features(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([image],[0],None,[256],[0,256])
    threshold_val, threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    brightness_val = cv2.mean(image)[0]
    contrast_val = cv2.Laplacian(gray, cv2.CV_64F).var()
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpness_val = cv2.filter2D(gray, -1, kernel)
    median = cv2.medianBlur(gray, 5)
    noise_val = np.mean((gray - median) ** 2)
    height, width = gray.shape[:2]
    resolution_val = height * width
    blurriness_val = cv2.Laplacian(gray, cv2.CV_64F).var()
    return [brightness_val, threshold_val, contrast_val, np.mean(sharpness_val), noise_val, resolution_val, blurriness_val]


def predict_image_class(image_path):
    image_features = extract_features(image_path)
    image_features = np.array(image_features).reshape(1, -1)
    predicted_label = loaded_model.predict(image_features)[0]
    return predicted_label


@app.route("/qualitycheck", methods=["POST"])
def quality_check_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['file']

    if pdf_file.filename.endswith('.pdf'):
        # Create a temporary directory to store page images
        with tempfile.TemporaryDirectory() as temp_dir:
            overall_quality = "Good"
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

            quality_results = []

            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                image_bytes = page.get_pixmap().tobytes()

                # Create a temporary image file for processing
                image_path = f"{temp_dir}/page_{page_number}.png"
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                numeric_label = predict_image_class(image_path=image_path)
                predicted_label = label_mapping.get(numeric_label, 'IDK Man')


                quality_results.append({"page_number": page_number, "quality": predicted_label})

                # If a "bad" or "very bad" page is detected, stop processing
                if predicted_label in ["Bad", "Very Bad"]:
                    overall_quality = predicted_label
                    break

            pdf_document.close()

            return jsonify({'overall_quality': overall_quality, "page_results": quality_results})

    return jsonify({"error": "Invalid PDF file"}), 400

if __name__ == "__main__":
    app.run(debug=True)
