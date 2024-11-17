from flask import Flask, jsonify
from confluent_kafka import Producer
import requests
import csv
import io
import schedule
import time
import logging
from threading import Thread

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'raw-weather-reports'

producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def fetch_and_publish_storm_reports():
    url = 'https://www.spc.noaa.gov/climo/reports/today.csv'
    try:
        logging.info('Fetching data from NOAA...')
        response = requests.get(url)
        response.raise_for_status()

        if not response.content:
            logging.warning('No data fetched from NOAA.')
            return

        # Parse CSV data
        csv_file = io.StringIO(response.text)
        csv_reader = csv.DictReader(csv_file)

        records_published = 0
        for row in csv_reader:
            # Check if row has expected fields
            if 'Time' in row and 'Location' in row and 'Comments' in row:
                # Publish each row to Kafka
                producer.produce(KAFKA_TOPIC, value=str(row), callback=delivery_report)
                records_published += 1
            else:
                logging.warning(f'Skipping row due to missing fields: {row}')

            producer.poll(0)

        producer.flush()
        logging.info(f'Data fetched and published successfully. Total records published: {records_published}')

    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching data from NOAA: {e}')
    except Exception as e:
        logging.error(f'Unexpected error: {e}')

def start_scheduler():
    schedule.every(24).hours.do(fetch_and_publish_storm_reports)

    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/start', methods=['GET'])
def start_service():
    fetch_and_publish_storm_reports()
    return jsonify({'status': 'Data collection initiated'}), 200

if __name__ == '__main__':
    scheduler_thread = Thread(target=start_scheduler)
    scheduler_thread.start()

    app.run(host='0.0.0.0', port=5000)
