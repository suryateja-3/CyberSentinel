import os
import sys
from pathlib import Path

backend_dir = Path(r"c:\Users\surya\OneDrive\Desktop\cyber-sentinel\backend")
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent / "ml-pipeline"))

from services.input_classifier import classify_input

ex_a = "Most adults with normal kidney function do well drinking about 1.5 to 3 liters of plain water daily, adjusting for climate, exercise, and sweat."
ex_b = "Violent student protests and campus vandalism erupted at Lovely Professional University in Phagwara, Punjab, in late September 2026, triggered by unverified social media rumors regarding an alleged sexual assault."

print("=== CLASSIFY A ===")
res_a = classify_input(ex_a)
print(res_a)

print("\n=== CLASSIFY B ===")
res_b = classify_input(ex_b)
print(res_b)
