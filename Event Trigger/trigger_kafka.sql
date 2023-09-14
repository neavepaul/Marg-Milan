-- Create a function to send a message to Kafka
CREATE OR REPLACE FUNCTION send_to_kafka()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if the flag column is 1
  IF NEW.flag = 1 THEN
    -- Send a message to the Kafka topic
    PERFORM pg_notify('kafka_channel', 'All the files are available');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger that calls the function when the flag column is updated
CREATE TRIGGER check_flag_value
AFTER UPDATE OF flag ON summary
FOR EACH ROW
EXECUTE FUNCTION send_to_kafka();
