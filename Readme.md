# Install environment

All terminals should be opened by gitbash
> install vscode

> install python

> install pip
```bash
python -m ensurepip --upgrade
```
or

Download https://bootstrap.pypa.io/get-pip.py
```bash
python get-pip.py
```

> install go

> install nvm

Install nvm from https://github.com/coreybutler/nvm-windows/releases

> install npm using nvm

```bash
npm install 21
npm ls
npm use 21
```

> install kafka

Install IntelliJ IDEA Community version from https://www.jetbrains.com/idea/download/?section=windows

Setup JAVA_HOME and java path

![JAVA_HOME](./res/image.png)

![Path](./res/image1.png)

Check java version
```bash
java --version
```
![check path](./res/image2.png)

Download gradle from https://gradle.org/releases/ (binary only)

Unzip gradle.zip

Setup env gradle/bin path

![Path](./res/image1.png)

Download kafka from https://kafka.apache.org/downloads (Binary download)
Unzip kafka.zip

change config file.

server.properties
![kafka config](./res/image3.png)

```bash
cd C:/kafka_2.13-3.9.0
./bin/windows/zookeeper-server-start.bat ./config/zookeeper.properties
./bin/windows/kafka-server-start.bat ./config/server.properties
```

# Project configuration

### Config kafka

Create Kafka topic
```bash
./bin/windows/kafka-topics.bat --create --topic raw-weather-reports --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Verify the topic creation
```bash
./bin/windows/kafka-topics.bat --list --bootstrap-server localhost:9092
```

Test producer and sonsumer
```bash
./bin/windows/kafka-console-producer.bat --topic raw-weather-reports --bootstrap-server localhost:9092
```
```bash
./bin/windows/kafka-console-consumer.bat --topic raw-weather-reports --from-beginning --bootstrap-server localhost:9092
```

Python

```bash
pip install flask confluent-kafka requests schedule
```

Node