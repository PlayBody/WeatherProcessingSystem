from flask import Flask, jsonify
from confluent_kafka import Producer
import requests
import csv
import io
import schedule
import time
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'raw-weather-reports'

producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def fetch_and_publish_storm_reports():
    try:
        # Fetch data from NOAA
        url = 'https://www.spc.noaa.gov/climo/reports/today.csv'
        response = requests.get(url)
        response.raise_for_status()

        # Parse CSV data
        csv_file = io.StringIO(response.text)
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            # Publish each row to Kafka
            producer.produce(KAFKA_TOPIC, value=str(row), callback=delivery_report)
            producer.poll(0)

        producer.flush()
        logging.info('Data fetched and published successfully.')

    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching data: {e}')

def start_scheduler():
    # Schedule the task every 24 hours
    schedule.every(24).hours.do(fetch_and_publish_storm_reports)

    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/start', methods=['GET'])
def start_service():
    fetch_and_publish_storm_reports()
    return jsonify({'status': 'Data collection initiated'}), 200

if __name__ == '__main__':
    # Start the scheduler in a separate thread
    from threading import Thread
    scheduler_thread = Thread(target=start_scheduler)
    scheduler_thread.start()

    # Start Flask app
    app.run(host='0.0.0.0', port=5000)
