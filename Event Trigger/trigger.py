import asyncio
from kafka import KafkaProducer
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# Kafka broker address
bootstrap_servers = 'localhost:9092'

# Kafka topic to produce messages to
kafka_topic = 'post_process_topic'

# PostgreSQL connection parameters
db_url = 'postgresql://postgres:password@localhost:5432/SIH'

# Create a KafkaProducer instance
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# Function to send a message to Kafka
def send_message(message):
    producer.send(kafka_topic, message.encode('utf-8'))
    producer.flush()

# SQLAlchemy setup
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)

# Function to handle PostgreSQL notifications
def handle_pg_notification(notify):
    payload = notify.payload
    send_message(payload)
    print(f"Received notification: {payload}")

if __name__ == "__main__":
    # Create an asyncio event loop
    loop = asyncio.get_event_loop()

    # Listen to the PostgreSQL channel using SQLAlchemy
    connection = engine.connect()
    listen_command = "LISTEN kafka_channel;"
    connection.execute(text(listen_command))
    
    # Register the event handler for PostgreSQL notifications
    @event.listens_for(engine, "after_begin")
    def receive_pg_notifications(conn, transaction, connection_record):
        conn.execute("LISTEN kafka_channel;")
        loop = asyncio.get_event_loop()
        while True:
            notifications = conn.connection.notifies
            for notify in notifications:
                handle_pg_notification(notify)
    
    try:
        # Run the asyncio event loop
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
