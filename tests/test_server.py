import sys
import os
import json
import unittest
import requests
from datetime import datetime

# Add parent directory to path to import server modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.chatgpt import callToOpenAI

class TestServer(unittest.TestCase):
    def setUp(self):
        self.log_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.test_results = []
        
    def tearDown(self):
        # Save test results
        with open(os.path.join("tests", "logs", self.log_file), "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

    def log_test_result(self, test_name, input_data, expected, actual, success, error=None):
        result = {
            "test_name": test_name,
            "input": input_data,
            "expected": expected,
            "actual": actual,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            result["error"] = str(error)
        self.test_results.append(result)

    def test_turkish_chars(self):
        test_cases = [
            {
                "name": "Basic_Turkish",
                "input": "havalandırma kanalı uzunluğu",
                "expected_type": str
            },
            {
                "name": "Mixed_Turkish_Numbers",
                "input": "3 metre yüksekliğinde duvar çiz",
                "expected_type": str
            },
            {
                "name": "Special_Chars",
                "input": "kapı & pencere % özellikleri",
                "expected_type": str
            }
        ]

        for case in test_cases:
            try:
                result = callToOpenAI(case["input"])
                success = isinstance(result, case["expected_type"])
                self.log_test_result(
                    case["name"],
                    case["input"],
                    f"Type: {case['expected_type']}",
                    f"Type: {type(result)}",
                    success
                )
                self.assertIsInstance(result, case["expected_type"])
            except Exception as e:
                self.log_test_result(
                    case["name"],
                    case["input"],
                    f"Type: {case['expected_type']}",
                    "Error occurred",
                    False,
                    error=e
                )
                raise

    def test_server_response(self):
        test_cases = [
            {
                "name": "Basic_Request",
                "input": {"client": "test message"},
                "expected_keys": ["response", "type"]
            }
        ]

        for case in test_cases:
            try:
                response = requests.post(
                    "http://127.0.0.1:8080/",
                    json=case["input"],
                    headers={"Content-Type": "application/json"}
                )
                response_data = response.json()
                success = all(key in response_data for key in case["expected_keys"])
                self.log_test_result(
                    case["name"],
                    case["input"],
                    f"Expected keys: {case['expected_keys']}",
                    f"Actual keys: {list(response_data.keys())}",
                    success
                )
                for key in case["expected_keys"]:
                    self.assertIn(key, response_data)
            except Exception as e:
                self.log_test_result(
                    case["name"],
                    case["input"],
                    f"Expected keys: {case['expected_keys']}",
                    "Error occurred",
                    False,
                    error=e
                )
                raise

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join("tests", "logs"), exist_ok=True)
    unittest.main()
