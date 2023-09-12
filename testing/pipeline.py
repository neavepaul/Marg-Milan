import concurrent.futures
import pdfplumber
import random
import os
import pandas as pd
from retrying import retry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Road, Surveyor, Test, Subtest, QCR1Report, QCR2Report, QMRReport

# Define your database connection URL
db_url = "postgresql://username:password@localhost:5432/SIH"

# Define a function to extract metadata
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
@retry(wait_fixed=1000, stop_max_attempt_number=3)
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
        # Add "Report Type" column and fill with "qcr1"
        test_results_df["Report Type"] = str(report_type)

        return test_results_df

# Define a function to transform and load data
def transform_and_load_data(pdf_path, db_url):
    try:
        # PDF processing and data transformation code here
        test_results = process_pdf(pdf_path)

        # Create a connection to the PostgreSQL database
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Iterate through the DataFrame and perform transformations
        for index, row in test_results.iterrows():
            # Lookup or insert Road, Surveyor, Test, Subtest
            road = session.query(Road).filter_by(name=row['road_name']).first()
            surveyor = session.query(Surveyor).filter_by(name=row['surveyor_name']).first()
            test = session.query(Test).filter_by(name=row['test_name']).first()
            subtest = session.query(Subtest).filter_by(name=row['subtest_name']).first()

            # we'll get this from the kafka message
            report_type = random.choice(['qcr1', 'qcr2', 'qmr'])

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
                    url="https://firebasestorage.googleapis.com/v0/b/auction-ffe0a.appspot.com/o/test%2Ftest_report_1.pdf?alt=media&token=37776ab3-ec33-4955-8a0b-3c6cd35fbae3"
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
                    url="https://firebasestorage.googleapis.com/v0/b/auction-ffe0a.appspot.com/o/test%2Ftest_report_1.pdf?alt=media&token=37776ab3-ec33-4955-8a0b-3c6cd35fbae3"
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
                    url="https://firebasestorage.googleapis.com/v0/b/auction-ffe0a.appspot.com/o/test%2Ftest_report_1.pdf?alt=media&token=37776ab3-ec33-4955-8a0b-3c6cd35fbae3"
                )
            else:
                print("Bro! what is this file now?")
                continue

            session.add(report)

        # Commit the changes to the database
        session.commit()

        # Close the session and database connection
        session.close()
        engine.dispose()

    except Exception as e:
        # Handle exceptions, log errors, or retry if needed
        print(f"Error processing PDF: {str(e)}")
        raise

# List of PDF paths to process
pipeline_folder = 'buffer'
pdf_paths = [os.path.join(pipeline_folder, filename) for filename in os.listdir(pipeline_folder) if filename.endswith('.pdf')]

# Number of parallel workers (adjust as needed)
num_workers = 4

# Create a ThreadPoolExecutor with the desired number of workers
with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Submit PDF processing tasks
    futures = [executor.submit(transform_and_load_data, pdf_path, db_url) for pdf_path in pdf_paths]

    # Wait for all tasks to complete
    concurrent.futures.wait(futures)
