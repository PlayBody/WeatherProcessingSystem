import unittest
from unittest.mock import patch, mock_open, MagicMock
from app import fetch_and_publish_storm_reports, load_config, app

class TestWeatherDataService(unittest.TestCase):

    @patch('confluent_kafka.Producer')
    @patch('app.requests.get')
    def test_fetch_and_publish_storm_reports_noaa(self, mock_get, mock_producer):
        # Mock the requests.get call to return a fake response
        mock_response = MagicMock()
        mock_response.iter_lines = MagicMock(return_value=[
            b'Time,F_Scale,Location,County,State,Lat,Lon,Comments',
            b'524,UNK,Rockaway Beach,Tillamook,OR,45.61,-123.94,"*** 1 INJ *** EF-0 tornado with estimated winds of 85 mph."'
        ])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock the Kafka producer
        mock_produce = MagicMock()
        mock_producer_instance = mock_producer.return_value
        mock_producer_instance.produce = mock_produce

        # Call the function to test
        fetch_and_publish_storm_reports()

        # Debug output
        print(f"NOAA Test - Produce called: {mock_produce.called}, Call count: {mock_produce.call_count}")

        # Check if the produce method was called
        self.assertTrue(mock_produce.called)
        self.assertEqual(mock_produce.call_count, 1)

    @patch('confluent_kafka.Producer')
    @patch('builtins.open', new_callable=mock_open, read_data='Time,F_Scale,Location,County,State,Lat,Lon,Comments\n524,UNK,Rockaway Beach,Tillamook,OR,45.61,-123.94,"*** 1 INJ *** EF-0 tornado with estimated winds of 85 mph."\n')
    def test_fetch_and_publish_storm_reports_local(self, mock_open, mock_producer):
        # Set the USE_LOCAL_TEST flag to True
        with patch.dict('app.config', {'test': {'flag': False, 'csv': './../today.csv'}}):
            # Mock the Kafka producer
            mock_produce = MagicMock()
            mock_producer_instance = mock_producer.return_value
            mock_producer_instance.produce = mock_produce

            # Call the function to test
            fetch_and_publish_storm_reports()

            # Debug output
            print(f"Local Test - Produce called: {mock_produce.called}, Call count: {mock_produce.call_count}")

            # Check if the produce method was called
            self.assertTrue(mock_produce.called)
            self.assertEqual(mock_produce.call_count, 1)

    def test_load_config(self):
        # Mock the yaml.safe_load to return a test config
        with patch('yaml.safe_load', return_value={'key': 'value'}):
            config = load_config('./config.yaml')
            self.assertEqual(config['key'], 'value')

    def test_start_service(self):
        # Test the Flask route
        tester = app.test_client(self)
        response = tester.get('/start')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data collection initiated', response.data)

if __name__ == '__main__':
    unittest.main()
