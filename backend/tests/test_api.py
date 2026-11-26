import sys
import os
import unittest
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')

    def test_fake_news_endpoint_real(self):
        # Known real news text from Reuters wire in WELFake dataset
        response = self.client.post('/api/detect/fake-news', json={
            "title": "French inflation falls more than expected in September",
            "text": "PARIS (Reuters) - French inflation fell more than expected in September, preliminary EU-harmonised data showed on Friday, supporting bets on further European Central Bank rate cuts."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['verdict'], 'REAL')
        self.assertIn('probabilities', data)
        self.assertIn('real', data['probabilities'])
        self.assertIn('fake', data['probabilities'])
        self.assertGreater(data['probabilities']['real'], 0.60)
        self.assertIn('logits', data)
        self.assertIn('calibration_note', data)

    def test_fake_news_endpoint_fake(self):
        # Known fake news text with conspiratorial / sensational claims
        response = self.client.post('/api/detect/fake-news', json={
            "title": "Secret 5G mind control frequencies activated by nano-particles in water",
            "text": "SHOCKING: 5G cell towers are transmitting mind-control radio frequencies activated by nano-particles in tap water. The government does not want you to know this truth! Share immediately before it gets taken down!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['verdict'], 'FAKE')
        self.assertIn('probabilities', data)
        self.assertGreater(data['probabilities']['fake'], 0.60)

    def test_fake_news_endpoint_uncertain_or_probabilities(self):
        # Neutral everyday text without wire or clickbait markers
        response = self.client.post('/api/detect/fake-news', json={
            "title": "Local Library Book Sale",
            "text": "The annual community library book sale will take place this Saturday morning from nine to two in the main parking lot."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['status'], 'success')
        self.assertIn(data['verdict'], ['REAL', 'FAKE', 'UNCERTAIN'])
        self.assertIn('probabilities', data)
        self.assertAlmostEqual(data['probabilities']['real'] + data['probabilities']['fake'], 1.0, places=4)

    def test_fake_news_short_text_validation(self):
        response = self.client.post('/api/detect/fake-news', json={
            "text": "Too short"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')

    def test_evidence_verification_endpoint(self):
        response = self.client.post('/api/verify/evidence', json={
            "title": "NASA Moon Mission",
            "text": "NASA confirms water ice detected on the south pole of the Moon."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn(data['status'], ['success', 'error'])
        if data['status'] == 'success':
            self.assertIn('verdict', data)
            self.assertIn('evidence', data)

    def test_fraud_sms_endpoint(self):
        response = self.client.post('/api/detect/fraud', json={
            "text": "Hey mom, just checking in to see how you are doing today."
        })
        self.assertIn(response.status_code, [200, 503])
        if response.status_code == 200:
            self.assertEqual(response.json['status'], 'success')
            self.assertIn('verdict', response.json)

    def test_url_safe_known_domains(self):
        safe_urls = [
            "https://www.youtube.com/watch?v=Amcm_P7viqk&list=RDnCD2hj6zJEc&index=2",
            "http://google.com/search?q=hello",
            "virtualtourist.com/travel/North_America/Canada/Province_of_Quebec/Montreal-906413/Transportation-Montreal-Train-BR-2.html",
        ]
        for url in safe_urls:
            response = self.client.post('/api/detect/url', json={"url": url})
            self.assertIn(response.status_code, [200, 503])
            if response.status_code == 200:
                self.assertEqual(response.json['status'], 'success')
                self.assertEqual(response.json['verdict'], 'SAFE', f"URL {url} incorrectly classified as MALICIOUS")

    def test_url_suspicious(self):
        malicious_urls = [
            "http://37.49.226.178/deusbins/deus.sh4",
            "http://www.sweethome.com.gr/index.php?option=com_estateagent&act=cat&task=showCE&id=9",
        ]
        for url in malicious_urls:
            response = self.client.post('/api/detect/url', json={"url": url})
            self.assertIn(response.status_code, [200, 503])
            if response.status_code == 200:
                self.assertEqual(response.json['status'], 'success')
                self.assertEqual(response.json['verdict'], 'MALICIOUS')

    def test_url_empty_and_malformed(self):
        response = self.client.post('/api/detect/url', json={"url": ""})
        self.assertIn(response.status_code, [200, 503])
        
        response = self.client.post('/api/detect/url', json={"bad_field": "test"})
        self.assertIn(response.status_code, [200, 503])

    def test_models_performance_endpoint(self):
        response = self.client.get('/api/models/performance')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('models', data)
        self.assertEqual(len(data['models']), 3)
        model_ids = [m['id'] for m in data['models']]
        self.assertIn('fake_news', model_ids)
        self.assertIn('fraud', model_ids)
        self.assertIn('url', model_ids)

    def test_dashboard_stats_endpoint(self):
        response = self.client.get('/api/dashboard/stats')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('scansToday', data)
        self.assertIn('threatsBlocked', data)
        self.assertIn('activeModels', data)
        self.assertIn('systemHealth', data)

    def test_models_status_endpoint(self):
        response = self.client.get('/api/models/status')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['status'], 'ok')
        self.assertIn('models', data)
        for name in ('fake_news', 'fraud', 'url'):
            self.assertIn(name, data['models'])
            self.assertIn('state', data['models'][name])

if __name__ == '__main__':
    unittest.main()
