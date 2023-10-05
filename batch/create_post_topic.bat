@echo off
echo Creating PostProcessTopic...
cd /d C:\Users\neave\kafka_2.12-3.5.1
./bin/windows/kafka-topics.bat --bootstrap-server localhost:9092 --topic PostProcessTopic --create --partitions 10 --replication-factor 1 --config retention.ms=120000
echo Kafka PostProcessTopic created.