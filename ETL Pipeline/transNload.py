import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from clubhouse_sqlalchemy_models import Road, Surveyor, Test, Subtest, QCR1Report, QCR2Report, QMRReport #like mongoose
from uuid import uuid4

# Create a connection to your PostgreSQL database
engine = create_engine('postgresql://username:password@localhost:5432/SIH')
Session = sessionmaker(bind=engine)
session = Session()

# Load your DataFrame 
df = # dataframe we'll get from the ocr module

# Iterate through the DataFrame and perform transformations
for index, row in df.iterrows():

    report_type = row["Report Type"]
    # Lookup or insert Road
    road = session.query(Road).filter_by(name=row['road_name']).first()

    # Lookup or insert Surveyor
    surveyor = session.query(Surveyor).filter_by(name=row['surveyor_name']).first()

    # Lookup or insert Test
    test = session.query(Test).filter_by(name=row['test_name']).first()

    # Lookup or insert Subtest
    subtest = session.query(Subtest).filter_by(name=row['subtest_name']).first()


    # Create a new row in the appropriate table with the transformed values
    if report_type == 'qcr1':
        report = QCR1Report(
            qcr1_id=str(uuid4()),    #see if this can be made better
            road_id=road.id,
            surveyor_id=surveyor.id,
            test_id=test.id,
            subtest_id=subtest.id,
            iteration=1,
            value=row['values'],
            timestamp=row['timestamp']
        )
    elif report_type == 'qcr2':
        report = QCR2Report(
            qcr2_id=str(uuid4()),
            road_id=road.id,
            surveyor_id=surveyor.id,
            test_id=test.id,
            subtest_id=subtest.id,
            iteration=1,
            value=row['values'],
            timestamp=row['timestamp']
        )
    elif report_type == 'qmr':
        report = QMRReport(
            qmr_id=str(uuid4()),
            road_id=road.id,
            surveyor_id=surveyor.id,
            test_id=test.id,
            subtest_id=subtest.id,
            iteration=1,
            value=row['values'],
            timestamp=row['timestamp']
        )
    else:
        print("Bro! what is this file now?")
        continue

    session.add(test_report)

# Commit the changes to the database
session.commit()

# Close the session and database connection
session.close()
engine.dispose()
