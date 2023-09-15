import kafka
import json

kafka_config = {
    "bootstrap_servers": "localhost:9092",
    "group_id": "pdf_upload_consumer_group",
    "auto_offset_reset": "earliest"
}

consumer = kafka.KafkaConsumer("PostProcessTopic", **kafka_config)

for message in consumer:
    message_data = json.loads(message.value)
    pdf_url = message_data.get("road_id")
    report_type = message_data.get("no of files")
    road_id = message_data.get("Message")
    print(pdf_url, report_type, road_id)