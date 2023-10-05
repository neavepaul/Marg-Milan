@echo off

echo Starting the OMMAS System. Please Do Not Touch Anything Till All Programs are Live!
timeout /t 10

echo Removing directories...

rem Remove directories
rmdir /s /q "C:\Users\neave\kafka_2.12-3.5.1\logs"
rmdir /s /q "C:\Users\neave\kafka_2.12-3.5.1\kafka-logs"
rmdir /s /q "C:\Users\neave\kafka_2.12-3.5.1\zookeeper-data"

echo Directories removed.

echo Starting Zookeeper and Kafka...

rem Start Zookeeper and Kafka
cd /d C:\Users\neave\kafka_2.12-3.5.1
start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_zookeeper.bat

start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_kafka.bat


rem Delay to allow Kafka and Zookeeper to start
timeout /t 20

echo Zookeeper and Kafka are now running.


rem Create Kafka topics
start cmd /k C:\Users\neave\Documents\project\SIH\batch\create_upload_topic.bat
start cmd /k C:\Users\neave\Documents\project\SIH\batch\create_post_topic.bat

rem Delay to allow Kafka Topic Creation
timeout /t 10

echo Starting Python scripts...

cd /d C:\Users\neave\Documents\project\SIH\apis
start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_app.bat

cd /d C:\Users\neave\Documents\project\SIH\Upload PDF Producer
start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_upload_producer.bat

cd /d C:\Users\neave\Documents\project\SIH\ETL Pipeline
start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_etl_pipe.bat

cd /d C:\Users\neave\Documents\project\SIH\Event Trigger
start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_trigger_handler.bat

cd /d C:\Users\neave\Documents\project\SIH\Post Process Handler
start cmd /k C:\Users\neave\Documents\project\SIH\batch\start_topic_consumer.bat

echo All programs are live.

pause
