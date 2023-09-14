from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.event import listens_for
from sqlalchemy import update

# Define the SQLAlchemy models
Base = declarative_base()

class Record(Base):
    __tablename__ = 'records'
    serial_no = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer)
    road_id = Column(Integer, ForeignKey('roads.road_id'))
    report_type = Column(String)
    url = Column(String)
    # timestamp = Column(TIMESTAMP)

class Summary(Base):
    __tablename__ = 'summary'
    serial_no = Column(Integer, primary_key=True, autoincrement=True)
    road_id = Column(Integer, ForeignKey('roads.road_id'))
    flag = Column(Integer, default=0)
    countoffiles = Column(Integer, default=0)
    is_processed = Column(Integer, default=0)

# i want to add these triggers to my postgresql database
# 1) on add to one of the three tables (QCR1, QCR2, QMR) add to records table
# 2) on add to record table. update the summary table countoffiles value by 1
# 3) when the countoffiles becomes three then set the flag to 3