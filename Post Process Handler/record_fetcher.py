from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_models import QCR1, QCR2, QMR, Subtest, Test, Surveyor
from discrepancy_checker import DiscrepancyChecker

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, port=5002)
