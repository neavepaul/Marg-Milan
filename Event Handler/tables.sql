-- Trigger to add records when inserting into QCR1
CREATE OR REPLACE FUNCTION add_to_records_qcr1()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO records (report_id, road_id, report_type, url)
    VALUES (NEW.report_id, NEW.road_id, NEW.report_type, NEW.url);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_into_records_qcr1
AFTER INSERT ON QCR1
FOR EACH ROW
EXECUTE FUNCTION add_to_records_qcr1();

-- Trigger to add records when inserting into QCR2
CREATE OR REPLACE FUNCTION add_to_records_qcr2()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO records (report_id, road_id, report_type, url)
    VALUES (NEW.report_id, NEW.road_id, NEW.report_type, NEW.url);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_into_records_qcr2
AFTER INSERT ON QCR2
FOR EACH ROW
EXECUTE FUNCTION add_to_records_qcr2();

-- Trigger to add records when inserting into QMR
CREATE OR REPLACE FUNCTION add_to_records_qmr()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO records (report_id, road_id, report_type, url)
    VALUES (NEW.report_id, NEW.road_id, NEW.report_type, NEW.url);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_into_records_qmr
AFTER INSERT ON QMR
FOR EACH ROW
EXECUTE FUNCTION add_to_records_qmr();

-- Trigger to update countoffiles when inserting into records
CREATE OR REPLACE FUNCTION update_countoffiles()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE summary
    SET countoffiles = countoffiles + 1
    WHERE road_id = NEW.road_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_record
AFTER INSERT ON records
FOR EACH ROW
EXECUTE FUNCTION update_countoffiles();

-- Trigger to set flag to 3 when countoffiles becomes three
CREATE OR REPLACE FUNCTION set_flag_to_3()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.countoffiles = 3 THEN
        UPDATE summary
        SET flag = 3
        WHERE road_id = NEW.road_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_flag_to_3
AFTER UPDATE OF countoffiles ON summary
FOR EACH ROW
EXECUTE FUNCTION set_flag_to_3();
