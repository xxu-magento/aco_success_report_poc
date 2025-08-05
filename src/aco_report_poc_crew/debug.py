#!/usr/bin/env python
"""
Developer helpers for the ACO Success-Metrics crew.

Commands
--------
run              – Normal execution with fixture JSON (same as main.py).
train <N> <file> – CrewAI “train” utility; reruns the crew N times and
                   stores trajectories in <file>.
replay <task_id> – Replays a previous run, starting at task_id, so you
                   can inspect intermediate LLM calls step-by-step.
test  <N> <llm>  – CrewAI “test” utility; executes N runs and evaluates
                   them with the given evaluation LLM name.

These helpers should **not** be used in production—only for local
prompt-tuning or debugging sessions.
"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from aco_report_poc_crew.crew import AcoReportPocCrew


# ---------- shared fixture loader ------------------------------------
def _load_fixture() -> dict:
    fixture_path = Path(__file__).parent / "data" / "test_data1.json"
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
    return {"payload": json.loads(fixture_path.read_text())}


# ---------- CLI helpers ----------------------------------------------
def run() -> None:
    """Regular crew kickoff (identical to main.py)."""
    result = AcoReportPocCrew().crew().kickoff(inputs=_load_fixture())
    print(json.dumps(result, indent=2))


def train(n_iterations: int, filename: str) -> None:
    """
    CrewAI's training loop:
        • Executes the crew n_iterations times.
        • Saves each trajectory (inputs, LLM calls, outputs) to <filename>.
    Useful for batch-tuning prompts or measuring latency.
    """
    AcoReportPocCrew().crew().train(
        n_iterations=n_iterations,
        filename=filename,
        inputs=_load_fixture(),
    )


def replay(task_id: str) -> None:
    """
    Re-executes a stored trajectory from a given task_id.
    Lets you step through agent reasoning and tool calls interactively.
    """
    AcoReportPocCrew().crew().replay(task_id=task_id)


def test(n_iterations: int, eval_llm: str) -> None:
    """
    CrewAI's testing mode:
        • Runs the crew n_iterations times.
        • Uses <eval_llm> (e.g., 'gpt-4o-mini') to auto-score outputs.
    Handy for regression tests or A/B prompt experiments.
    """
    AcoReportPocCrew().crew().test(
        n_iterations=n_iterations,
        eval_llm=eval_llm,
        inputs=_load_fixture(),
    )


# ---------- rudimentary CLI ------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "run":
        run()

    elif sys.argv[1] == "train" and len(sys.argv) == 4:
        train(int(sys.argv[2]), sys.argv[3])

    elif sys.argv[1] == "replay" and len(sys.argv) == 3:
        replay(sys.argv[2])

    elif sys.argv[1] == "test" and len(sys.argv) == 4:
        test(int(sys.argv[2]), sys.argv[3])

    else:
        print(
            "Usage:\n"
            "  python -m aco_report_poc_crew.debug run\n"
            "  python -m aco_report_poc_crew.debug train <N> <file>\n"
            "  python -m aco_report_poc_crew.debug replay <task_id>\n"
            "  python -m aco_report_poc_crew.debug test <N> <eval_llm>\n"
        )