from flask import Flask, render_template, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_models import QCR1, QCR2, QMR
import json

app = Flask(__name__)

# Define your database connection URL
db_url = 'postgresql://postgres:password@localhost:5432/SIH'


@app.route('/', methods=['GET'])
def index():
    # Create a new session
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Define the road_id you want to retrieve data for
    road_id = 1

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
    # Create a JSON object containing the cleaned data
    data = {
        'qcr1_data': qcr1_data,
        'qcr2_data': qcr2_data,
        'qmr_data': qmr_data
    }
    print(qcr1_data)

    # Render the HTML template and pass the JSON data to it
    return jsonify(data)
    # print()


if __name__ == '__main__':
    app.run()
