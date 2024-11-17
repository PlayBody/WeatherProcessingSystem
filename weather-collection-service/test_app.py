import unittest
from unittest.mock import patch, mock_open, MagicMock
from app import fetch_and_publish_storm_reports, load_config, app

class TestWeatherDataService(unittest.TestCase):

    @patch('app.requests.get')
    @patch('app.Producer')
    def test_fetch_and_publish_storm_reports(self, mock_producer, mock_get):
        # Call the function to test
        records_published = fetch_and_publish_storm_reports()

        # Check if the records_published is incremented
        self.assertEqual(records_published, 2)

    def test_load_config(self):
        # Mock the yaml.safe_load to return a test config
        with patch('yaml.safe_load', return_value={'key': 'value'}):
            config = load_config('config.yaml')
            self.assertEqual(config['key'], 'value')

    def test_start_service(self):
        # Test the Flask route
        tester = app.test_client(self)
        response = tester.get('/start')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data collection initiated', response.data)

if __name__ == '__main__':
    unittest.main()
