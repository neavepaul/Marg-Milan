from flask import Flask, request, jsonify
import cv2
import numpy as np
import pickle
import fitz
import tempfile
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_models import QCR1, QCR2, QMR, Subtest, Test, Surveyor, Road
from discrepancy_checker import DiscrepancyChecker
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# PostgreSQL database configuration
db_url = 'postgresql://postgres:password@localhost:5432/SIH'



###################################################################
#    GET ROAD INFO     #
###################################################################
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        engine = create_engine(db_url, poolclass=pool.QueuePool, pool_size=5, max_overflow=10)
        Session = sessionmaker(bind=engine)
        session = Session()
        # Query the database to retrieve data from the specified columns
        data = session(Road.road_id, Road.road_name).all()

        # Convert the data to a list of dictionaries
        result = [{'road_id': row[0], 'road_name': row[1]} for row in data]
        session.close()
        engine.dispose()
        return jsonify(result)
    except Exception as e:
        return str(e)


################################################################
#    DOCUMENT QUALITY    #
###############################################################

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


################################################################
#   DISCREPANCY FINDER    #
################################################################

# Define your database connection URL
db_url = 'postgresql://postgres:password@localhost:5432/SIH'

@app.route('/disc', methods=['POST'])
def index():
    data = request.get_json()
    road = data['road_id']

    # Create a new session
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Define the road_id you want to retrieve data for
    road_id = road
    qmr=0
    qcr1_mail=''
    qcr2_mail=''
    qmr_mail=''


    # Retrieve rows from QCR1, QCR2, and QMR tables for the specified road_id
    qcr1_results = session.query(QCR1).filter_by(road_id=road_id).all()
    qcr2_results = session.query(QCR2).filter_by(road_id=road_id).all()
    qmr_results = session.query(QMR).filter_by(road_id=road_id).all()

    # Close the session when you're done
    session.close()

    # Convert the query results to a dictionary
    qcr1_data = [result.__dict__ for result in qcr1_results]
    qcr2_data = [result.__dict__ for result in qcr2_results]
    qmr_data = [result.__dict__ for result in qmr_results]

    # Remove any unwanted attributes (e.g., internal SQLAlchemy attributes)
    def clean_dict(d):
        return {key: value for key, value in d.items() if not key.startswith('_')}

    qcr1_data = [clean_dict(data) for data in qcr1_data]
    qcr2_data = [clean_dict(data) for data in qcr2_data]
    qmr_data = [clean_dict(data) for data in qmr_data]

    # Instantiate the DiscrepancyChecker class
    checker = DiscrepancyChecker()

    # Create dictionaries for test reports
    test_report_1 = {}
    test_report_2 = {}
    test_report_3 = {}
    
    # test_name = session.query(Test.test_name).filter_by(test_id=test_id).scalar()
    # subtest_name = session.query(Subtest.subtest_name).filter_by(subtest_id=subtest_id).scalar()

    # Populate the test report dictionaries with the retrieved data
    for qcr1_entry in qcr1_data:
        # print(qcr1_entry['values_qcr1'])
        qcr1_mail = session.query(Surveyor.surveyor_email).filter_by(surveyor_id=qcr1_entry['surveyor_id']).scalar()
        test_name = session.query(Test.test_name).filter_by(test_id=qcr1_entry['test_id']).scalar()
        if test_name in test_report_1:
            test_report_1[test_name].append(qcr1_entry['values_qcr1'])
        else:
            test_report_1[test_name] = [qcr1_entry['values_qcr1']]

    for qcr2_entry in qcr2_data:
        qcr2_mail = session.query(Surveyor.surveyor_email).filter_by(surveyor_id=qcr2_entry['surveyor_id']).scalar()
        test_name = session.query(Test.test_name).filter_by(test_id=qcr2_entry['test_id']).scalar()
        if test_name in test_report_2:
            test_report_2[test_name].append(qcr2_entry['values_qcr2'])
        else:
            test_report_2[test_name] = [qcr2_entry['values_qcr2']]

    for qmr_entry in qmr_data:
        qmr=qmr_entry['qmr_id']
        qmr_mail = session.query(Surveyor.surveyor_email).filter_by(surveyor_id=qmr_entry['surveyor_id']).scalar()
        test_name = session.query(Test.test_name).filter_by(test_id=qmr_entry['test_id']).scalar()
        if test_name in test_report_3:
            test_report_3[test_name].append(qmr_entry['values_qmr'])
        else:
            test_report_3[test_name] = [qmr_entry['values_qmr']]

    # Check for discrepancies in each test report
    discrepancies_report_1 = checker.check_parameters("QCR 1", test_report_1)
    discrepancies_report_2 = checker.check_parameters("QCR 2", test_report_2)
    discrepancies_report_3 = checker.check_parameters("QMR", test_report_3)

    # Combine all discrepancies from different test reports
    all_discrepancies = {**discrepancies_report_1, **discrepancies_report_2, **discrepancies_report_3}

    # Prepare the response JSON object
    response_data = {
        'discrepancies': all_discrepancies,
        'road_id': road_id,
        'qmr_id': qmr,
        'mail_1': qcr1_mail,
        'mail_2': qcr2_mail,
        'mail_m': qmr_mail
    }

    # Return the response as JSON
    return jsonify(response_data)


################################################################
#    PDF UPLOAD TOPIC PUBLISHER (upload_producer.py)    #
###############################################################

if __name__ == '__main__':
    app.run()
