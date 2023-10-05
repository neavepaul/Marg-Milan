@echo off
echo Creating PDFUploadTopic...
cd /d C:\Users\neave\kafka_2.12-3.5.1
./bin/windows/kafka-topics.bat --bootstrap-server localhost:9092 --topic PDFUploadTopic --create --partitions 10 --replication-factor 1 --config retention.ms=120000
echo Kafka PDFUploadTopic created.