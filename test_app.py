import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_prediction_route(self):
        response = self.client.post('/prediction', data={
            'gender': 'Male',
            'married': 'Yes',
            'dependents': '0',
            'education': 'Graduate',
            'employed': 'Yes',
            'credit': '1',
            'area': 'Urban',
            'applicantIncome': '5000',
            'coapplicantIncome': '1000',
            'loanAmount': '150',
            'loanAmountTerm': '360'
        })
        self.assertEqual(response.status_code, 200)

    def test_suggestion_route(self):
        response = self.client.post('/suggestion', data={
            'married': 'Yes',
            'education': 'Graduate',
            'employed': 'Yes',
            'area': 'Urban',
            'TotalIncome': '6000'
        })
        self.assertIn(b'Type of Loan', response.data)

if __name__ == '__main__':
    unittest.main()
