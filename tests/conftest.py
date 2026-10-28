import json

import pytest

from qa_ai.__main__ import ROOT


@pytest.fixture
def cases():
    return json.loads((ROOT / "data/development-cases.json").read_text(encoding="utf-8"))


@pytest.fixture
def schema():
    return json.loads((ROOT / "data/draft.schema.json").read_text(encoding="utf-8"))


@pytest.fixture
def control_draft(cases):
    # Hand-authored checker controls, never presented as model-generated responses.
    case = cases[0]
    return {
        "status": "ready",
        "scenarios": [
            {
                "criterion_id": key,
                "type": kind,
                "title": title,
                "steps": [step],
                "expected_result": expected,
                "evidence_quote": case["acceptance_criteria"][key],
            }
            for key, kind, title, step, expected in [
                (
                    "AC-1",
                    "boundary",
                    "Minimum quantity",
                    "Request quantity 1",
                    "Quantity is accepted",
                ),
                ("AC-2", "negative", "Below minimum", "Request quantity 0", "No order is created"),
                (
                    "AC-3",
                    "positive",
                    "Price for two",
                    "Request two notebooks",
                    "Total is 2598 cents",
                ),
            ]
        ],
        "questions": [],
    }
