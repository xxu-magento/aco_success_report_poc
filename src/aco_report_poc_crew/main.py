#!/usr/bin/env python
"""
Run the ACO Success Metrics Report crew locally.

Usage:
    python -m aco_report_poc_crew.main
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from .jsonparser import process_payload


# Ensure .env variables (Azure key, endpoint) are available
load_dotenv()

from aco_report_poc_crew.crew import AcoReportPocCrew


def run() -> None:
    """Load fixture JSON, run the crew, and save the resulting report."""
    fixture_path = Path(__file__).parent / "data" / "test_data2.json"
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")  

    payload = json.loads(fixture_path.read_text())
    processed_payload = process_payload(payload)

    print(processed_payload)

    result = AcoReportPocCrew().crew().kickoff(
        inputs={"payload": processed_payload, "fixture_name": fixture_path.stem}
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = Path(f"final_report_{fixture_path.stem}_{timestamp}.txt")
    out_file.write_text(result.raw)
    print(f"Report saved to {out_file}")

    # Optional: preview part of the JSON
    print("=== Final Report JSON (truncated) ===")
    print(json.dumps(str(result.raw), indent=2)[:1000], "...\n")


if __name__ == "__main__":
    run()
