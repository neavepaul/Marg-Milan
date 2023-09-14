DROP TABLE reports,qcr1,qcr2,qmr,roads,subtest,surveyors,test;

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

INSERT INTO subtest(subtest_id,subtest_name) values(1,'1'),(2,'1'),(3,'2'),(4,'3'),(5,'1'),(6,'2'),(7,'1'),(8,'2'),(9,'1'),(10,'2'),(11,'3'),
	(12,'1'),(13,'1'),(14,'1'),(15,'1'),(16,'1'),(17,'2'),(18,'3'),(19,'4'),(20,'5');

SELECT * FROM roads where road_name='Hill road';

SELECT * FROM qcr1;