DROP TABLE reports,qcr1,qcr2,qmr,roads,subtest,surveyors,test, records, summary;

CREATE TABLE roads (
    road_id serial PRIMARY KEY,
    road_name varchar(255) NOT NULL,
    district varchar(255),
    city varchar(255),
    state varchar(255),
    pincode varchar(10)
);

CREATE TABLE subtest (
    subtest_id integer PRIMARY KEY,
--     test_name varchar(255),
    subtest_name varchar(255)
);

CREATE TABLE surveyors (
    surveyor_id serial PRIMARY KEY,
    surveyor_name varchar(255) NOT NULL
);

CREATE TABLE test (
    test_id serial PRIMARY KEY,
    test_name varchar(255) NOT NULL
);

CREATE TABLE qcr1 (
	qcr1_id serial PRIMARY KEY,
    road_id serial REFERENCES roads(road_id),
    surveyor_id integer  REFERENCES surveyors(surveyor_id),
    test_id integer  REFERENCES test(test_id),
    subtest_id integer  REFERENCES subtest(subtest_id),
    values_qcr1 float,
--     iteration integer,
--     timestp timestamp,
	url varchar(255)
);

CREATE TABLE qcr2 (
	qcr2_id serial PRIMARY KEY,
    road_id serial REFERENCES roads(road_id),
    surveyor_id integer  REFERENCES surveyors(surveyor_id),
    test_id integer  REFERENCES test(test_id),
    subtest_id integer  REFERENCES subtest(subtest_id),
    values_qcr2 float,
--     iteration integer,
--     timestp timestamp,
	url varchar(255)
);

CREATE TABLE qmr (
	qmr_id serial PRIMARY KEY,
    road_id serial REFERENCES roads(road_id),
    surveyor_id integer  REFERENCES surveyors(surveyor_id),
    test_id integer  REFERENCES test(test_id),
    subtest_id integer  REFERENCES subtest(subtest_id),
    values_qmr float,
	url varchar(255)
--     iteration integer,
--     timestp timestamp
);

CREATE TABLE reports (
    report_id integer PRIMARY KEY,
	road_id integer,
    surveyor_id integer,
    test_id integer,
    subtest_qcri integer,
    values_qcr1 integer,
    subtest_qcr2 integer,
    values_qcr2 integer,
    subtest_qmr integer,
    values_qmr float,
	url varchar(255)
);

-- Create the records table
CREATE TABLE records (
    serial_no serial PRIMARY KEY,
    report_id integer,
    road_id integer REFERENCES roads(road_id),
    report_type varchar(255),
    url varchar(255)
    -- timestamp timestamp
);

-- Create the summary table with serial_no as the primary key
CREATE TABLE summary (
    serial_no serial PRIMARY KEY,
    road_id integer REFERENCES roads(road_id),
    flag integer DEFAULT 0,
    countoffiles integer DEFAULT 0,
    is_processed integer DEFAULT 0
);

INSERT INTO roads(road_id,
    road_name,
    district,
    city,
    state,
    pincode) values(1,'Hill road','Mumbai','Mumbai','Maharashtra',400050);


INSERT INTO surveyors(surveyor_id,surveyor_name) values(1,'Mr. Abhisekh');


INSERT INTO test (
    test_id,
    test_name) values(1,'Soil Gradation (mm)'),(2,'Atterberg Limits (%)'),(3,'Natural Moisture Content (%)'),(4,'Proctor Density (g/cm³)'),
	(5,'Proctor Density (%)'),(6,'CBR (%)'),(7,'Swelling Index (%)'),(8,'Moisture content at time of compaction (%)'),
	(9,'Thickness (inches)'),(10,'Field Density (%)'),(11,'Horizontal alignment (m)'),(12,'Horizontal alignment (%)');

INSERT INTO subtest(subtest_id,subtest_name) values(1,'Soil Gradation'),(2,'Liquid limit (LL)'),(3,'Plastic Limit (PL)'),(4,'Plasticity Index (PI)'),(5,'Subgrade material'),(6,'Base and Sub-base Materials'),(7,'Maximum Dry Density (MDD)'),(8,'Optimum Moisture Content (OMC)'),(9,'Subgrade'),(10,'Base Course'),(11,'Sub-base'),
	(12,'Swelling Index'),(13,'Moisture Content at the time of Compaction'),(14,'Thickness'),(15,'Field density'),(16,'Radius of Curvature (R)'),(17,'Superelevation (Banking)'),(18,'Transition Curve Length (L)'),(19,'Horizontal Curve Length (Lc)'),(20,'Grade (Slope)');

SELECT * FROM roads where road_name='Hill road';

SELECT * FROM qcr1;