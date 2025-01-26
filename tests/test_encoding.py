import sys
import os
import json
import unittest
from datetime import datetime

# Add paths to import custom functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "Project.extension", "lib"))
from custom_functions import clean_response_string, clean_code_snippet

class TestEncoding(unittest.TestCase):
    def setUp(self):
        self.log_file = f"encoding_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.test_results = []
        
    def tearDown(self):
        # Save test results
        with open(os.path.join("tests", "logs", self.log_file), "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

    def log_test_result(self, test_name, input_data, expected, actual, success, error=None):
        result = {
            "test_name": test_name,
            "input": str(input_data),  # Convert bytes to string for JSON serialization
            "expected": expected,
            "actual": actual,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            result["error"] = str(error)
        self.test_results.append(result)

    def test_clean_response_string(self):
        test_cases = [
            {
                "name": "String_Input",
                "input": "Normal string response",
                "expected": "Normal string response"
            },
            {
                "name": "Bytes_Input",
                "input": b"Bytes string response",
                "expected": "Bytes string response"
            },
            {
                "name": "Turkish_String",
                "input": "Türkçe karakterler: çğıöşü",
                "expected": "Turkce karakterler cgiosu"
            },
            {
                "name": "Mixed_Content",
                "input": "Mix of bytes & Türkçe".encode('utf-8'),
                "expected": "Mix of bytes  Turkce"
            }
        ]

        for case in test_cases:
            try:
                result = clean_response_string(case["input"])
                success = result == case["expected"]
                self.log_test_result(
                    case["name"],
                    case["input"],
                    case["expected"],
                    result,
                    success
                )
                self.assertEqual(result, case["expected"])
            except Exception as e:
                self.log_test_result(
                    case["name"],
                    case["input"],
                    case["expected"],
                    "Error occurred",
                    False,
                    error=e
                )
                raise

    def test_clean_code_snippet(self):
        test_cases = [
            {
                "name": "Simple_Python_Code",
                "input": """
                def test_function():
                    print("Hello")
                """,
                "expected_type": tuple
            },
            {
                "name": "Code_With_Turkish",
                "input": """
                # Türkçe yorum satırı
                def hesapla():
                    return "çıktı"
                """,
                "expected_type": tuple
            },
            {
                "name": "Bytes_Code",
                "input": b"""
                def bytes_func():
                    return b"test"
                """,
                "expected_type": tuple
            },
            {
                "name": "Code_With_Markdown",
                "input": """```python
                def markdown_func():
                    print("test")
                ```""",
                "expected_type": tuple
            }
        ]

        for case in test_cases:
            try:
                result = clean_code_snippet(case["input"])
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

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join("tests", "logs"), exist_ok=True)
    unittest.main()
