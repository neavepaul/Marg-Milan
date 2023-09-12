import kafka
from flask import Flask, request, jsonify
import json
import concurrent.futures

# Initialize Flask app
app = Flask(__name__)

# Initialize Kafka producer
kafka_producer = kafka.KafkaProducer(bootstrap_servers="kafka_broker_url")

# Define a route to accept PDF upload data
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        # Extract Firestore PDF URL, report type, and file name from the request
        data = request.json
        pdf_url = data.get('pdf_url')
        report_type = data.get('report_type')
        road_id = data.get('road_id')

        if not (pdf_url and report_type and road_id):
            return jsonify({"error": "Invalid data format"}), 400

        # Create a message with the data
        message_data = {
            "pdf_url": pdf_url,
            "report_type": report_type,
            "road_id": road_id
        }

        # Publish the message to the Kafka PDF upload topic using concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(publish_to_kafka, message_data)

        return jsonify({"message": "Data published to Kafka!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def publish_to_kafka(message_data):
    try:
        # Publish the message to the Kafka PDF upload topic
        kafka_producer.send("pdf_upload_topic", json.dumps(message_data).encode("utf-8"))
    except Exception as e:
        print(f"Error publishing to Kafka: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
