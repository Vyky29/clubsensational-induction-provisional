#!/usr/bin/env python3
"""Ensure each match question has exactly 4 pairs."""
import json
from pathlib import Path

path = Path(__file__).parent / "induction_quizzes.json"
data = json.loads(path.read_text(encoding="utf-8"))
extras = {
    "1": {"label": "Key Partners", "answer": "Collaboration and shared resources"},
    "2": {"label": "Teamwork", "answer": "Shared responsibility across departments"},
    "3": {"label": "Adaptation", "answer": "Flexible support across venues"},
    "4": {"label": "Person Centred Approach", "answer": "Adapting support to the individual"},
    "5": {"label": "Professionalism", "answer": "Representing clubSENsational with care"},
    "6": {"label": "Data Protection", "answer": "Secure and appropriate information use"},
}
for key, mod in data.items():
    for q in mod["questions"]:
        if q["type"] == "match":
            if len(q["pairs"]) < 4:
                q["pairs"].append(extras[key])
path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("patched match questions")
