from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_models import QCR1, QCR2, QMR

# Define your database connection URL
db_url = 'postgresql://postgres:password@localhost:5432/SIH'

# Create a new session
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Define the road_id you want to retrieve data for
road_id = 123  # Replace with the desired road_id

# Retrieve rows from QCR1, QCR2, and QMR tables for the specified road_id
qcr1_results = session.query(QCR1).filter_by(road_id=road_id).all()
qcr2_results = session.query(QCR2).filter_by(road_id=road_id).all()
qmr_results = session.query(QMR).filter_by(road_id=road_id).all()

# Close the session when you're done
session.close()