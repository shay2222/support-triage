"""
Runs the triage function on labeled sample tickets and reports accuracy.
Usage: python eval.py
"""
import csv
import os
import time
from pathlib import Path

from triage import build_client, triage_ticket

DATA_PATH = Path("data/sample_tickets.csv")
RESULTS_PATH = Path("results/eval_results.csv")
DELAY_SECONDS = 4  # Pause between calls to stay within free-tier rate limits.


def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set. See the README setup steps.")

    client = build_client(api_key)
    RESULTS_PATH.parent.mkdir(exist_ok=True)

    with DATA_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    category_hits = urgency_hits = errors = 0
    results = []

    for i, row in enumerate(rows, start=1):
        try:
            pred = triage_ticket(client, row["text"])
        except Exception as err:
            errors += 1
            pred = {"category": "ERROR", "urgency": "ERROR", "summary": str(err)}

        cat_ok = pred["category"] == row["category"]
        urg_ok = pred["urgency"] == row["urgency"]
        category_hits += cat_ok
        urgency_hits += urg_ok

        results.append({
            "text": row["text"],
            "expected_category": row["category"],
            "predicted_category": pred["category"],
            "expected_urgency": row["urgency"],
            "predicted_urgency": pred["urgency"],
            "category_correct": cat_ok,
            "urgency_correct": urg_ok,
        })
        print(f"[{i}/{len(rows)}] category {'ok' if cat_ok else 'MISS'} | urgency {'ok' if urg_ok else 'MISS'}")
        time.sleep(DELAY_SECONDS)

    total = len(rows)
    print(f"\nCategory accuracy: {category_hits}/{total} ({category_hits / total:.0%})")
    print(f"Urgency accuracy:  {urgency_hits}/{total} ({urgency_hits / total:.0%})")
    print(f"API errors: {errors}")

    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Detailed results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()