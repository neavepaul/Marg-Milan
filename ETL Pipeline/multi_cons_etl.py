import kafka
import json
import os
import pathlib
import concurrent.futures
import urllib.request
import pdfplumber
import pandas as pd
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from db_models import Road, Surveyor, Test, Subtest, QCR1, QCR2, QMR
from multiprocessing import Process


# Define your Kafka configuration
kafka_config = {
    "bootstrap_servers": "localhost:9092",
    "group_id": "pdf_upload_consumer_group",
    "auto_offset_reset": "earliest",
    "enable_auto_commit": True,
    "auto_commit_interval_ms": 1000
}

local_path = ""

# Define your database connection URL
db_url = 'postgresql://postgres:password@localhost:5432/SIH'

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
            metadata_df = metadata_df._append(pd.DataFrame.from_dict([page_metadata]), ignore_index=True)

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
        print("Before delete XXXXXXXXXXXXXXX")

        # Close the PDF file explicitly
        pdf.close()

        os.remove(pdf_path)
        print(local_path)
        print("File deleted")
        # pathlib.Path.unlink(local_path)
        return test_results_df

# Define a function for transformation and loading
def transform_and_load_data(pdf_path, db_url, report_type, pdf_url, roadid):
    print("Path: "+str(pdf_path))
    try:
        test_results = process_pdf(pdf_path, report_type)

        # engine = create_engine(db_url)
        engine = create_engine(db_url, poolclass=pool.QueuePool, pool_size=5, max_overflow=10)
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as connection:
            for index, row in test_results.iterrows():
                road = session.query(Road).filter_by(
                    road_name=row["Road Name"]).first()
                surveyor = session.query(Surveyor).filter_by(
                    surveyor_name=row['Surveyor Name']).first()
                test = session.query(Test).filter_by(
                    test_name=row['Test Name']).first()
                subtest = session.query(Subtest).filter_by(
                    subtest_name=row['Subtest Name']).first()

                report_type = row['Report Type']

                # Check if any of the objects is None, and if so, insert a new record
                if road is None:
                    road = Road(road_name=row["Road Name"])
                    session.add(road)
                    session.commit()  # Commit the new road record
                if surveyor is None:
                    print("ALWAYS TRIES TO ADD SURVEYOR AGAIN FSR...  THE TABLE HAS TWO ABHISHEKHS NOW")
                    surveyor = Surveyor(surveyor_name=row['Surveyor Name'])
                    session.add(surveyor)
                    session.commit()  # Commit the new surveyor record


                # Create a new row in the appropriate table with the transformed values
                if report_type == 'qcr1':
                    values = float(row['Value'])
                    report = QCR1(
                        road_id=road.road_id,
                        surveyor_id=surveyor.surveyor_id,
                        test_id=test.test_id,
                        subtest_id=subtest.subtest_id,
                        values_qcr1=values,   # Remove qmr_id assignment
                        # timestamp='2023-09-13 12:34:56.789012',
                        url=pdf_url
                    )
                elif report_type == 'qcr2':
                    values = float(row['Value'])
                    report = QCR2(
                        road_id=road.road_id,
                        surveyor_id=surveyor.surveyor_id,
                        test_id=test.test_id,
                        subtest_id=subtest.subtest_id,
                        values_qcr2=values,   # Remove qmr_id assignment
                        # timestamp='2023-09-13 12:34:56.789012',
                        url=pdf_url
                    )
                elif report_type == 'qmr':

                    values = float(row['Value'])
                    report = QMR(
                        road_id=road.road_id,
                        surveyor_id=surveyor.surveyor_id,
                        test_id=test.test_id,
                        subtest_id=subtest.subtest_id,
                        values_qmr=values,   # Remove qmr_id assignment
                        # timestamp='2023-09-13 12:34:56.789012',
                        url=pdf_url
                    )
                else:
                    print("Bro! what is this file now?")
                    continue
                session.add(report)

            session.commit()
            session.close()
            engine.dispose()
            print("Report added")

        # Send availability notification message to the respective topic
        availability_message = {
            "pdf_url": pdf_url,
            "report_type": report_type,
            "road_id": roadid,
            "status": "available"  # Indicate that the PDF is available and preprocessing is complete
        }

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


# Create a ThreadPoolExecutor with the desired number of workers
def start_consumer():
    # Create a Kafka consumer for the PDF upload topic
    consumer = kafka.KafkaConsumer("PDFUploadTopic", **kafka_config)
    for message in consumer:
        message_data = json.loads(message.value)
        pdf_url = message_data.get("pdf_url")
        report_type = message_data.get("report_type")
        road_id = message_data.get("road_id")
        file_name = str(road_id)+"_"+report_type.upper()+".pdf"

        # Download the PDF using the Firestore URL
        local_path = download_pdf_from_firestore(pdf_url, file_name)
        print("File Downloaded")
        

        # Submit PDF processing tasks to the ThreadPoolExecutor
        transform_and_load_data(local_path, db_url, report_type, pdf_url, road_id)


if __name__ == '__main__':
    # Number of parallel workers (adjust as needed)
    num_consumers = 1
    # Create multiple Kafka consumer processes
    processes = []
    for i in range(num_consumers):
        process = Process(target=start_consumer)
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()