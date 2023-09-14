CREATE OR REPLACE FUNCTION add_to_records_qcr1()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if a record for this report already exists
    UPDATE records
    SET road_id = NEW.road_id,
        report_type = 'QCR1',
        url = NEW.url
    WHERE road_id = NEW.road_id and report_type = 'QCR1';

    -- If no record exists, insert a new one
    IF NOT FOUND THEN
        INSERT INTO records (report_id, road_id, report_type, url)
        VALUES (NEW.qcr1_id, NEW.road_id, 'QCR1', NEW.url);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_into_records_qcr1
AFTER INSERT ON qcr1
FOR EACH ROW
EXECUTE FUNCTION add_to_records_qcr1();


CREATE OR REPLACE FUNCTION add_to_records_qcr2()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if a record for this report already exists
    UPDATE records
    SET road_id = NEW.road_id,
        report_type = 'QCR2',
        url = NEW.url
    WHERE road_id = NEW.road_id and report_type = 'QCR2';

    -- If no record exists, insert a new one
    IF NOT FOUND THEN
        INSERT INTO records (report_id, road_id, report_type, url)
        VALUES (NEW.qcr2_id, NEW.road_id, 'QCR2', NEW.url);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_into_records_qcr2
AFTER INSERT ON qcr2
FOR EACH ROW
EXECUTE FUNCTION add_to_records_qcr2();



CREATE OR REPLACE FUNCTION add_to_records_qmr()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if a record for this report already exists
    UPDATE records
    SET road_id = NEW.road_id,
        report_type = 'QMR',
        url = NEW.url
    WHERE road_id = NEW.road_id and report_type = 'QMR';

    -- If no record exists, insert a new one
    IF NOT FOUND THEN
        INSERT INTO records (report_id, road_id, report_type, url)
        VALUES (NEW.qmr_id, NEW.road_id, 'QMR', NEW.url);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_into_records_qmr
AFTER INSERT ON qmr
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


CREATE OR REPLACE FUNCTION update_countoffiles()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if a record for this report already exists
    UPDATE summary
    SET countoffiles = countoffiles + 1
    WHERE road_id = NEW.road_id;

    -- If no record exists, insert a new one
    IF NOT FOUND THEN
        INSERT INTO summary (road_id, countoffiles)
        VALUES (NEW.road_id, 1);
    END IF;

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
        SET flag = 1
        WHERE road_id = NEW.road_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_flag_to_3
AFTER UPDATE OF countoffiles ON summary
FOR EACH ROW
EXECUTE FUNCTION set_flag_to_3();
