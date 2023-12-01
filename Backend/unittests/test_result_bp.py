import unittest, sys
from flask import Flask, json
sys.path.insert(0, '../')
from result import results_bp

class TestSubmitResult(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(results_bp)
        self.client = self.app.test_client()

    def test_submit_result_valid_input(self):
        # Define a sample valid request body
        data = {
            'patientId': '123',
            'testCode': 'TC1',
            'orderId': 'O1',
            'interpretation': 'Positive',
            'reportingPathologist': 'Dr. Smith'
        }

        # Send a POST request to the '/api/results' route
        response = self.client.post('/api/results', data=json.dumps(data), content_type='application/json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_submit_result_invalid_input(self):
        # Define a sample invalid request body
        data = {
            'patientId': '123',
            'testCode': 'TC1',
            'orderId': 'O1',
            'interpretation': 'Positive',
            'reportingPathologist': ''  # Missing reportingPathologist
        }

        # Send a POST request to the '/api/results' route
        response = self.client.post('/api/results', data=json.dumps(data), content_type='application/json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()