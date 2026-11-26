import os
import sys
import unittest
from unittest.mock import patch, Mock
import requests
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.evidence_service import verify_claim

class TestEvidenceService(unittest.TestCase):
    def setUp(self):
        # Save original env
        self.original_env = os.environ.get("GNEWS_API_KEY")
        os.environ["GNEWS_API_KEY"] = "test_api_key"

    def tearDown(self):
        # Restore original env
        if self.original_env is None:
            if "GNEWS_API_KEY" in os.environ:
                del os.environ["GNEWS_API_KEY"]
        else:
            os.environ["GNEWS_API_KEY"] = self.original_env

    @patch('services.evidence_service.requests.get')
    def test_successful_evidence_retrieval(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "NASA discovers water on Moon",
                    "url": "http://example.com/nasa-moon",
                    "publishedAt": "2023-10-09T00:00:00Z",
                    "description": "NASA confirms water ice on the moon."
                }
            ]
        }
        mock_get.return_value = mock_response

        result = verify_claim("NASA confirms water ice on Moon poles")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["evidence"]), 1)
        self.assertEqual(result["evidence"][0]["title"], "NASA discovers water on Moon")

    @patch('services.evidence_service.requests.get')
    def test_missing_api_key(self, mock_get):
        del os.environ["GNEWS_API_KEY"]
        result = verify_claim("NASA confirms water")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Verification unavailable: API key not configured.")
        mock_get.assert_not_called()

    @patch('services.evidence_service.requests.get')
    def test_provider_error_401(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 401
        # requests.get should return the mock response, and raise_for_status will be called
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error", response=mock_response)
        mock_get.return_value = mock_response

        result = verify_claim("NASA confirms water")
        self.assertEqual(result["status"], "error")
        self.assertIn("Authentication or permission problem", result["message"])

    @patch('services.evidence_service.requests.get')
    def test_provider_error_429(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        result = verify_claim("NASA confirms water")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Verification unavailable: Rate limit exceeded.")

    @patch('services.evidence_service.requests.get')
    def test_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Read timeout")
        result = verify_claim("NASA confirms water")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Verification unavailable: Request timed out.")

    @patch('services.evidence_service.requests.get')
    def test_malformed_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        # Return an object that lacks the 'articles' list completely
        mock_response.json.return_value = {"error": "something went wrong"}
        mock_get.return_value = mock_response

        result = verify_claim("NASA confirms water")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "No related news reports found.")

    def test_empty_query(self):
        result = verify_claim("")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Empty claim text.")

if __name__ == '__main__':
    unittest.main()
