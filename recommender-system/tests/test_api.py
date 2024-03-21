import unittest
import requests
import time
import os

from dotenv import load_dotenv
load_dotenv()

API_PATH = os.getenv('API_PATH')
API_TOKEN = os.getenv('API_TOKEN')

class TestAPI(unittest.TestCase):
    def test_api_call_with_retry(self):
        url = f'{API_PATH}/recommend'
        myobj = {'username': 'oxlade8'}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': API_TOKEN
        }
        
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            response = requests.post(url, json=myobj, headers=headers)
            if response.status_code == 200:
                # Successful response
                break
            elif response.json().get('message') == 'Service Unavailable':
                if attempt < max_retries - 1:
                    print("Service Unavailable. Retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
                    self.fail("API still unavailable after {} attempts.".format(max_retries))
            else:
                self.fail("Unexpected response: {}".format(response.text))

        # Assertions
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on your API response structure

if __name__ == '__main__':
    unittest.main()
