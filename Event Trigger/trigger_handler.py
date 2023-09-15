import select
import psycopg2
import psycopg2.extensions
from kafka import KafkaProducer
import json

# Kafka broker address
bootstrap_servers = 'localhost:9092'

# Kafka topic to produce messages to
kafka_topic = 'PostProcessTopic'

# Create a KafkaProducer instance
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

DSN = "dbname=SIH user=postgres password=password host=localhost port=5432"

conn = psycopg2.connect(DSN)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

curs = conn.cursor()
curs.execute("LISTEN kafka_channel;")

def send_message(message):
    producer.send(kafka_topic, json.dumps(message).encode("utf-8"))


def handle_pg_notification(notify):
    payload = notify
    print(f"Received notification: {payload}")
    rid = int(str(payload[0]).split(":")[1].strip(" ")[0])
    message_data = {
        "road_id": rid,
        "no of files": 3,
        "Message": "All reports received"
    }
    send_message(message_data)


print("Waiting for notifications on channel 'test'")
while 1:
    if select.select([conn], [], [], 5) == ([], [], []):
        print("Timeout")
    else:
        conn.poll()
        if conn.notifies:
            notify = conn.notifies
            print("Element added into dummy")
            handle_pg_notification(notify)
