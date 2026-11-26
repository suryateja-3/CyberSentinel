import os
import sys
import unittest
from unittest.mock import patch, Mock
import requests
from pathlib import Path
import numpy as np
import torch

# Add backend and ml-pipeline to sys.path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent / "ml-pipeline"))

from app import app, get_dl_model
from services.evidence_service import verify_claim, extract_search_terms
from services.input_classifier import classify_input

class TestFakeNewsAndEvidenceAdvanced(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_model_label_mapping(self):
        """Verify model weights and mapping: index 0 is REAL, index 1 is FAKE."""
        model, tokenizer = get_dl_model("fake_news")
        self.assertIsNotNone(model, "DistilBERT model must be loaded")
        self.assertIsNotNone(tokenizer, "DistilBERT tokenizer must be loaded")

        # Reuters wire sample is known REAL in dataset
        reuters_text = "WASHINGTON (Reuters) - U.S. consumer confidence improved in October as inflation expectations eased."
        inputs = tokenizer(reuters_text, return_tensors="pt", truncation=True, max_length=256)
        with torch.inference_mode():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()

        # Index 0 (REAL) must be dominant for clear wire reports
        self.assertGreater(probs[0], 0.60, "Reuters text must have high probability on class 0 (REAL)")
        self.assertAlmostEqual(probs[0] + probs[1], 1.0, places=4)

    def test_probability_calculation_and_logits(self):
        """Verify softmax is accurately applied to logits and probabilities match."""
        resp = self.client.post('/api/detect/fake-news', json={
            "text": "PARIS (Reuters) - Economic output expanded across the eurozone in the third quarter."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn("logits", data)
        self.assertIn("probabilities", data)

        logits = np.array(data["logits"])
        exp_logits = np.exp(logits - np.max(logits))
        expected_probs = exp_logits / np.sum(exp_logits)

        self.assertAlmostEqual(data["probabilities"]["real"], float(expected_probs[0]), places=4)
        self.assertAlmostEqual(data["probabilities"]["fake"], float(expected_probs[1]), places=4)

    def test_regression_example_a_health_advice(self):
        """
        Regression Test for Example A:
        'Most adults with normal kidney function do well drinking about 1.5 to 3 liters of plain water daily...'
        Expected behavior:
        1. Identified as general health information / advice.
        2. Do not declare this FAKE solely because of DistilBERT score.
        3. Model assessment provides raw scores transparently.
        4. Explains that recommended water intake varies by individual.
        """
        ex_a = "Most adults with normal kidney function do well drinking about 1.5 to 3 liters of plain water daily, adjusting for climate, exercise, and sweat."
        
        # 1. Test Input Classifier
        class_res = classify_input(ex_a)
        self.assertEqual(class_res["genre"], "general_health_advice")
        self.assertFalse(class_res["is_model_suitable"])
        self.assertIn("renal health", class_res["domain_guidance"])

        # 2. Test ML Endpoint
        resp = self.client.post('/api/detect/fake-news', json={"text": ex_a})
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertNotEqual(data["verdict"], "FAKE", "General health advice must NOT be declared FAKE solely from DistilBERT score")
        self.assertEqual(data["verdict"], "INFORMATIONAL")
        self.assertIn("model_assessment", data)
        self.assertIn("raw_class_label", data["model_assessment"])
        self.assertIn("domain_guidance", data["input_classification"])
        self.assertIn("vary", data["input_classification"]["domain_guidance"].lower())

        # 3. Test Evidence Service handling
        ev_res = verify_claim(ex_a)
        self.assertEqual(ev_res["status"], "success")
        self.assertIn(ev_res["verdict"], ["UNVERIFIED", "insufficient"])
        self.assertNotEqual(ev_res["verdict"], "FAKE", "Evidence service must never report FAKE on missing news articles")

    def test_regression_example_b_campus_protests(self):
        """
        Regression Test for Example B:
        'Violent student protests and campus vandalism erupted at Lovely Professional University in Phagwara, Punjab...'
        Expected behavior:
        1. Search for relevant dated reports and credible sources.
        2. Model predicts raw class (DistilBERT flags FAKE due to wire bias).
        3. External evidence retrieves published reporting.
        4. When evidence corroborates the event, system reports SUPPORTED (not FAKE).
        """
        ex_b = "Violent student protests and campus vandalism erupted at Lovely Professional University in Phagwara, Punjab, in late September 2026, triggered by unverified social media rumors regarding an alleged sexual assault."
        
        # 1. Search term extractor extracts key entity and event
        query = extract_search_terms(ex_b)
        self.assertIn("Lovely Professional University", query)
        self.assertIn("protests", query.lower())

        # 2. Mock GNews returning credible reports
        with patch('services.evidence_service.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "articles": [
                    {
                        "title": "Violent student protests at Lovely Professional University over alleged assault",
                        "url": "https://tribuneindia.com/news/lpu-protests",
                        "publishedAt": "2026-09-28T02:00:00Z",
                        "description": "Police deployed to restore calm after campus vandalism and violent protests at LPU.",
                        "source": {"name": "The Tribune"}
                    },
                    {
                        "title": "LPU protests: Police lathi charge students as protests turn violent in Phagwara",
                        "url": "https://economictimes.indiatimes.com/lpu-unrest",
                        "publishedAt": "2026-09-27T16:00:00Z",
                        "description": "Protests were initiated following allegations of sexual assault on campus.",
                        "source": {"name": "The Economic Times"}
                    }
                ]
            }
            mock_get.return_value = mock_resp

            ev_res = verify_claim(ex_b)
            self.assertEqual(ev_res["status"], "success")
            self.assertEqual(ev_res["verdict"], "SUPPORTED")
            self.assertEqual(ev_res["supporting_count"], 2)
            self.assertEqual(ev_res["contradicting_count"], 0)
            self.assertEqual(ev_res["evidence"][0]["source"], "The Tribune")
            self.assertEqual(ev_res["evidence"][1]["source"], "The Economic Times")

    def test_different_inputs_produce_distinct_predictions(self):
        """Verify inference is dynamic and no fixed/cached confidence is returned."""
        inputs = [
            "PARIS (Reuters) - French manufacturing output rose sharply last quarter.",
            "SHOCKING: Drinking boiling bleach is the secret miracle cure that doctors want to hide from you!!",
            "The committee held a routine public hearing on municipal road maintenance on Monday afternoon."
        ]

        results = []
        for text in inputs:
            resp = self.client.post('/api/detect/fake-news', json={"text": text})
            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data["status"], "success")
            results.append((data["confidence"], data["probabilities"]["real"], data["probabilities"]["fake"]))

        confidences = [r[0] for r in results]
        self.assertNotEqual(confidences[0], confidences[1], "Different inputs must produce different confidences")
        self.assertNotEqual(confidences[1], confidences[2], "Different inputs must produce different confidences")

    def test_supporting_vs_contradicting_evidence_logic(self):
        """Verify evidence categorization distinguishes supporting and contradicting articles."""
        # 1. Contradicting response mock
        with patch('services.evidence_service.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "articles": [
                    {
                        "title": "Fact check: Debunked claim that 5G towers cause mind control",
                        "url": "https://factcheck.org/5g-hoax",
                        "publishedAt": "2026-10-10T12:00:00Z",
                        "description": "Experts confirm viral post is completely false and a known internet hoax.",
                        "source": {"name": "FactCheck.org", "url": "https://factcheck.org"}
                    }
                ]
            }
            mock_get.return_value = mock_resp

            res = verify_claim("5G towers mind control", title="5G Mind Control")
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["verdict"], "CONTRADICTED")
            self.assertEqual(res["contradicting_count"], 1)
            self.assertEqual(res["supporting_count"], 0)
            self.assertEqual(res["evidence"][0]["source"], "FactCheck.org")
            self.assertEqual(res["evidence"][0]["url"], "https://factcheck.org/5g-hoax")

        # 2. Supporting response mock
        with patch('services.evidence_service.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "articles": [
                    {
                        "title": "NASA confirms water ice discovery on Moon south pole",
                        "url": "https://space.com/nasa-water-ice",
                        "publishedAt": "2026-10-11T14:00:00Z",
                        "description": "Scientists officially confirmed new deposits of lunar surface ice.",
                        "source": {"name": "Space.com", "url": "https://space.com"}
                    }
                ]
            }
            mock_get.return_value = mock_resp

            res = verify_claim("NASA confirms water ice on moon", title="NASA Moon Water")
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["verdict"], "SUPPORTED")
            self.assertEqual(res["supporting_count"], 1)
            self.assertEqual(res["contradicting_count"], 0)

    def test_api_failure_never_returns_fake(self):
        """Verify API timeout, 429 rate limit, and errors return UNVERIFIED, never FAKE."""
        with patch('services.evidence_service.requests.get') as mock_get:
            # 1. Timeout simulation
            mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
            res_timeout = verify_claim("General election results announcement", title="Election Update")
            self.assertEqual(res_timeout["status"], "error")
            self.assertEqual(res_timeout["verdict"], "UNVERIFIED")
            self.assertIn("timed out", res_timeout["message"].lower())

        with patch('services.evidence_service.requests.get') as mock_get:
            # 2. Rate limit 429 simulation
            mock_resp = Mock()
            mock_resp.status_code = 429
            mock_get.return_value = mock_resp
            res_rate = verify_claim("General election results announcement", title="Election Update")
            self.assertEqual(res_rate["status"], "error")
            self.assertEqual(res_rate["verdict"], "UNVERIFIED")
            self.assertIn("rate limit", res_rate["message"].lower())

    def test_gnews_freshness_delay_notice(self):
        """Verify that GNews Free tier 12-hour delay notice is captured and displayed."""
        with patch('services.evidence_service.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "information": {
                    "realTimeArticles": {
                        "message": "Real-time news data is only available on paid plans. Free plan has a 12-hour delay."
                    }
                },
                "articles": [
                    {
                        "title": "Sample news title",
                        "url": "https://example.com/sample",
                        "publishedAt": "2026-10-10T08:00:00Z",
                        "description": "Sample description of the event.",
                        "source": {"name": "Example News"}
                    }
                ]
            }
            mock_get.return_value = mock_resp

            res = verify_claim("Sample news claim", title="Sample Title")
            self.assertEqual(res["status"], "success")
            self.assertIn("12-hour delay", res["provider_info"]["freshness"])
            self.assertIn("12-hour", res["provider_info"]["freshness_notice"])

    def test_empty_search_results_does_not_invent_verdict(self):
        """Verify empty search results returns 'UNVERIFIED' rather than assuming false."""
        with patch('services.evidence_service.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"articles": []}
            mock_get.return_value = mock_resp

            res = verify_claim("Obscure local claim about a lost dog in village", title="Lost dog found")
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["verdict"], "UNVERIFIED")
            self.assertEqual(res["total_sources"], 0)
            self.assertIn("No matching news articles were found", res["explanation"])
            self.assertIn("limitations", res)

if __name__ == '__main__':
    unittest.main()
