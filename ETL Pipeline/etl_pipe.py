import kafka
import json
import os
import concurrent.futures
import urllib.request
import pdfplumber
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Road, Surveyor, Test, Subtest, QCR1Report, QCR2Report, QMRReport

# Define your Kafka configuration
kafka_config = {
    "bootstrap_servers": "kafka_broker_url",
    "group_id": "pdf_upload_consumer_group",
    "auto_offset_reset": "earliest"
}

# Create a Kafka consumer for the PDF upload topic
consumer = kafka.KafkaConsumer("pdf_upload_topic", **kafka_config)

# Define a Kafka producer for the availability notification topics
producer = kafka.KafkaProducer(bootstrap_servers="kafka_broker_url")

local_path = ""

# Define your database connection URL
db_url = "postgresql://username:password@localhost/SIH"

def extract_metadata(page_text):
    metadata = {
        "Date": "",
        "Surveyor's Name": "",
        "Road Name": ""
    }

    for line in page_text:
        key, value = map(str.strip, line.split(':'))
        if key in metadata:
            metadata[key] = value

    return metadata

# Define a function to process a single PDF
def process_pdf(pdf_path, report_type):
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize dataframes for metadata and test results
        metadata_df = pd.DataFrame()
        test_results_df = pd.DataFrame(columns=["Test Name", "Subtest Name", "Value"])

        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "intersection_x_tolerance": 15
        }

        for page in pdf.pages:
            page_text = page.extract_text().split('\n')[:3]  # Assuming 3 lines at the top

            # Extract and update metadata from each page
            page_metadata = extract_metadata(page_text)
            metadata_df = metadata_df.append(pd.DataFrame.from_dict([page_metadata]), ignore_index=True)

            tables = page.find_tables(table_settings)
            if tables:
                for table_number, table in enumerate(tables, start=1):
                    tb = table.extract()
                    df = pd.DataFrame(tb[1:], columns=tb[0])
                    test_results_df = pd.concat([test_results_df, df], ignore_index=True)
            
        # Add metadata columns to test_results
        test_results_df["Date"] = metadata_df["Date"][0]
        test_results_df["Surveyor Name"] = metadata_df["Surveyor's Name"][0]
        test_results_df["Road Name"] = metadata_df["Road Name"][0]
        test_results_df["Report Type"] = str(report_type)
        os.remove(local_path)
        return test_results_df

# Define a function for transformation and loading
def transform_and_load_data(pdf_path, db_url, report_type, url):
    try:
        test_results = process_pdf(pdf_path, report_type)

        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        for index, row in test_results.iterrows():
            road = session.query(Road).filter_by(name=row['Road Name']).first()
            surveyor = session.query(Surveyor).filter_by(name=row['Surveyor Name']).first()
            test = session.query(Test).filter_by(name=row['Test Name']).first()
            subtest = session.query(Subtest).filter_by(name=row['Subtest Name']).first()

            report_type = row['Report Type']

            # Create a new row in the appropriate table with the transformed values
            if report_type == 'qcr1':
                report = QCR1Report(
                    # set Column(Integer, primary_key=True, autoincrement=True) in the model
                    road_id=road.id,
                    surveyor_id=surveyor.id,
                    test_id=test.id,
                    subtest_id=subtest.id,
                    value=row['values'],
                    iteration=1,
                    timestamp=row['timestamp'],
                    url=url
                )
            elif report_type == 'qcr2':
                report = QCR2Report(
                    # set Column(Integer, primary_key=True, autoincrement=True) in the model
                    road_id=road.id,
                    surveyor_id=surveyor.id,
                    test_id=test.id,
                    subtest_id=subtest.id,
                    value=row['values'],
                    iteration=1,
                    timestamp=row['timestamp'],
                    url=url
                )
            elif report_type == 'qmr':
                report = QMRReport(
                    # set Column(Integer, primary_key=True, autoincrement=True) in the model
                    road_id=road.id,
                    surveyor_id=surveyor.id,
                    test_id=test.id,
                    subtest_id=subtest.id,
                    value=row['values'],
                    timestamp=row['timestamp'],
                    url=url
                )
            else:
                print("Bro! what is this file now?")
                continue

            session.add(report)

        session.commit()
        session.close()
        engine.dispose()

        # Send availability notification message to the respective topic
        availability_message = {
            "pdf_url": pdf_url,
            "report_type": report_type,
            "road_id": road_id,
            "status": "available"  # Indicate that the PDF is available and preprocessing is complete
        }
        producer.send(f"{report_type}_availability_topic", json.dumps(availability_message).encode("utf-8"))

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise

def download_pdf_from_firestore(url, name):
    response = urllib.request.urlopen(url)
    file = open(name, 'wb')
    file.write(response.read())
    file.close()
    path = os.path.join(os.getcwd(), name)
    return path


# Number of parallel workers (adjust as needed)
num_workers = 4

# Create a ThreadPoolExecutor with the desired number of workers
with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    for message in consumer:
        message_data = json.loads(message.value)
        pdf_url = message_data.get("pdf_url")
        report_type = message_data.get("report_type")
        road_id = message_data.get("road_id")
        file_name = road_id+"_"+report_type+".pdf"

        # Download the PDF using the Firestore URL
        local_path = download_pdf_from_firestore(pdf_url, file_name)

        # Submit PDF processing tasks to the ThreadPoolExecutor
        executor.submit(transform_and_load_data, local_path, report_type, pdf_url)
