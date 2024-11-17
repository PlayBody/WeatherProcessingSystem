from flask import Flask, jsonify
from confluent_kafka import Producer
import requests
import csv
import io
import schedule
import time
import logging
from threading import Thread
import yaml
import os

def load_config(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)

    for key, value in config.items():
        if isinstance(value, str):
            config[key] = os.path.expandvars(value)

    return config

config = load_config('config.yaml')


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = config["kafka"]["boot"] if config["kafka"]["boot"] is not None else 'localhost:9092'
KAFKA_TOPIC = config["kafka"]["topic"] if config["kafka"]["topic"] is not None else 'raw-weather-reports'

producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

# Toggle for using local test data
USE_LOCAL_TEST = config["test"]["flag"]
LOCAL_FILE_PATH = config["test"]["csv"]

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def fetch_and_publish_storm_reports():
    records_published = 0
    try:
        if USE_LOCAL_TEST:
            logging.info('Using local test data...')
            with open(LOCAL_FILE_PATH, 'r') as csvfile:
                csv_data = csvfile.read()
        else:
            logging.info('Fetching data from NOAA...')
            url = 'https://www.spc.noaa.gov/climo/reports/today.csv'
            response = requests.get(url)
            response.raise_for_status()
            csv_data = response.text

        # Parse CSV data
        csv_file = io.StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        field_map = {}
        for field in csv_reader.fieldnames:
            field_map[field] = field

        for row in csv_reader:
            # Check if row has expected fields
            if 'Time' in row and 'Location' in row and 'Comments' in row:
                # Check changed fields.
                if row["Time"] == "Time":
                    new_field_map = {}
                    for key, value in field_map.items():
                        new_field_map[value] = row[key]
                    field_map = new_field_map
                    continue
                data = {}
                for key, value in row.items():
                    data[field_map[key]] = value
                producer.produce(KAFKA_TOPIC, value=str(data), callback=delivery_report)
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
    finally:
        if USE_LOCAL_TEST:
            csv_file.close()
    return records_published

def start_scheduler():
    schedule.every(config["app"]["schedule"]).hours.do(fetch_and_publish_storm_reports)

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

    app.run(host='0.0.0.0', port=config["app"]["port"])
