from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:password@localhost:5432/SIH')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Road(Base):
    __tablename__ = 'roads'
    road_id = Column(Integer, primary_key=True)
    road_name = Column(String(255), nullable=False)
    district = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    pincode = Column(String(10))


class Subtest(Base):
    __tablename__ = 'subtest'
    subtest_id = Column(Integer, primary_key=True)
    test_name = Column(String(255))
    subtest_name = Column(String(255))


class Surveyor(Base):
    __tablename__ = 'surveyors'
    surveyor_id = Column(Integer, primary_key=True)
    surveyor_name = Column(String(255), nullable=False)


class Test(Base):
    __tablename__ = 'test'
    test_id = Column(Integer, primary_key=True)
    test_name = Column(String(255), nullable=False)


class QCR1(Base):
    __tablename__ = 'qcr1'
    qcr1_id = Column(Integer, primary_key=True)
    road_id = Column(Integer, ForeignKey('roads.road_id'))
    surveyor_id = Column(Integer, ForeignKey('surveyors.surveyor_id'))
    test_id = Column(Integer, ForeignKey('test.test_id'))
    subtest_id = Column(Integer, ForeignKey('subtest.subtest_id'))
    values_qcr1 = Column(Integer)
    iteration = Column(Integer)
    timestp = Column(TIMESTAMP)


class QCR2(Base):
    __tablename__ = 'qcr2'
    qcr2_id = Column(Integer, primary_key=True)
    road_id = Column(Integer, ForeignKey('roads.road_id'))
    surveyor_id = Column(Integer, ForeignKey('surveyors.surveyor_id'))
    test_id = Column(Integer, ForeignKey('test.test_id'))
    subtest_id = Column(Integer, ForeignKey('subtest.subtest_id'))
    values_qcr1 = Column(Integer)
    iteration = Column(Integer)
    timestp = Column(TIMESTAMP)


class QMR(Base):
    __tablename__ = 'qmr'
    qmr_id = Column(Integer, primary_key=True)
    road_id = Column(Integer, ForeignKey('roads.road_id'))
    surveyor_id = Column(Integer, ForeignKey('surveyors.surveyor_id'))
    test_id = Column(Integer, ForeignKey('test.test_id'))
    subtest_id = Column(Integer, ForeignKey('subtest.subtest_id'))
    values_qcr1 = Column(Integer)
    iteration = Column(Integer)
    timestp = Column(TIMESTAMP)


# class Report(Base):
#     __tablename__ = 'reports'
#     report_id = Column(Integer, primary_key=True)
#     road_id = Column(Integer)
#     surveyor_id = Column(Integer)
#     test_id = Column(Integer)
#     subtest_qcr1 = Column(Integer, ForeignKey('subtest.subtest_id'))
#     values_qcr1 = Column(Integer)
#     subtest_qcr2 = Column(Integer)
#     values_qcr2 = Column(Integer)
#     subtest_qmr = Column(Integer)
#     values_qmr = Column(Integer)


Base.metadata.create_all(engine)


users = session.query(Road).all()
for user in users:
    print(user.road_id, user.road_name, user.district, user.city)
if len(users) == 0:
    print("No values")