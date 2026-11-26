import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
from app import app
from services.evidence_service import verify_claim

client = app.test_client()

ex_a = "Most adults with normal kidney function do well drinking about 1.5 to 3 liters of plain water daily, adjusting for climate, exercise, and sweat."
ex_b = "Violent student protests and campus vandalism erupted at Lovely Professional University in Phagwara, Punjab, in late September 2026, triggered by unverified social media rumors regarding an alleged sexual assault."

print("=== EXAMPLE A ===")
resp_a = client.post('/api/detect/fake-news', json={"text": ex_a})
print("ML response:", resp_a.json)
ev_a = verify_claim(ex_a)
print("Evidence response:", ev_a)

print("\n=== EXAMPLE B ===")
resp_b = client.post('/api/detect/fake-news', json={"text": ex_b})
print("ML response:", resp_b.json)
ev_b = verify_claim(ex_b)
print("Evidence response:", ev_b)
