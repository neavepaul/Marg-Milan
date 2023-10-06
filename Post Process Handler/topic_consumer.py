from kafka import KafkaConsumer
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Discp_report
import json

# Kafka consumer configuration
consumer = KafkaConsumer('PostProcessTopic', bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

# SQLAlchemy database configuration
engine = create_engine('postgresql://postgres:password@localhost:5432/SIH')
Session = sessionmaker(bind=engine)

# Kafka message processing loop
for message in consumer:
    road_id = message.value['road_id']

    # Make a request to the specified URL with the road_id
    response = requests.post('http://127.0.0.1:5002/disc', json={"road_id": road_id})

    # Parse the response JSON
    response_data = response.json()

    # Extract required data from the response
    qmr_id = response_data.get('qmr_id')
    discrepancies = response_data.get('discrepancies')
    mail1 = response_data.get('mail_1')
    mail2 = response_data.get('mail_2')
    mailm = response_data.get('mail_m')

    # Create a new record in the database
    new_record = Discp_report(road_id=road_id, qmr_id=qmr_id, report_text=discrepancies)

    # Save the record in the database
    session = Session()
    session.add(new_record)

    # Make a request to the specified URL with the road_id and receiver_email
    request_body = {
        "message_type": "Discrepancy Report Created",
        "road_id": road_id,
        "payload_message": f"This email is to notify you that the Discrepancy Report for Road ID {road_id} has been created.",
        "receiver_emails": [mail1, mail2, mailm]
    }

    session.commit()
    session.close()
    response = requests.post('https://ommas-mailer.onrender.com/send_mail', json=request_body)
