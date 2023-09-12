from kafka import KafkaConsumer
import json

pulled_trigger = False

topics = {
    "QCR1": "qcr1_availability_topic",
    "QCR2": "qcr2_availability_topic",
    "QMR": "qmr_availability_topic"
}

consumers = {}

tracker = {}

for type, topic in topics.items():
    consumers[type] = KafkaConsumer(
        topic,
        group_id=f"event_trigger_{type}",
        bootstrap_servers='kafka_broker_url',
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

def check_trigger(road_id):
    if all(tracker[road_id].values()) and not pulled_trigger:
        pulled_trigger=True

def process_message(msg):
    report_type = msg.get("report_type")
    road_id = msg.get("road_id")
    if road_id not in tracker:
        tracker[road_id] = {
            "QCR1":False,
            "QCR2": False,
            "QMR": False
        }

    tracker[road_id][report_type] = True
    print(f"{report_type} for {road_id} received")
    check_trigger(road_id)

try:
    while True:
        for type, consumer in consumers.items():
            for message in consumer:
                message_data = json.loads(message.value)
                process_message(message_data)
except KeyboardInterrupt:
    pass

