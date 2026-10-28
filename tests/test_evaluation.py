import json
from copy import deepcopy

import pytest

from qa_ai.evaluation import evaluate


def failed_names(result):
    return {check["name"] for check in result["checks"] if not check["passed"]}


def test_hand_authored_positive_control_passes(cases, schema, control_draft):
    assert evaluate(cases[0], json.dumps(control_draft), schema)["passed"]


@pytest.mark.parametrize("raw", ["not JSON", "```json\n{}\n```", ""])
def test_malformed_json_fails_without_crashing(cases, schema, raw):
    result = evaluate(cases[0], raw, schema)
    assert failed_names(result) == {"valid_json"}


@pytest.mark.parametrize("change", ["missing-steps", "unexpected-field", "bad-type"])
def test_schema_violations_are_not_silently_accepted(cases, schema, control_draft, change):
    if change == "missing-steps":
        del control_draft["scenarios"][0]["steps"]
    elif change == "unexpected-field":
        control_draft["release_approved"] = True
    else:
        control_draft["scenarios"][0]["type"] = "happy-ish"
    assert "output_schema" in failed_names(evaluate(cases[0], json.dumps(control_draft), schema))


def test_missing_criterion_and_type_are_detected(cases, schema, control_draft):
    control_draft["scenarios"].pop(0)
    failures = failed_names(evaluate(cases[0], json.dumps(control_draft), schema))
    assert {"declared_coverage", "declared_test_types"} <= failures


def test_invented_criterion_and_quote_are_detected(cases, schema, control_draft):
    control_draft["scenarios"][0]["criterion_id"] = "AC-999"
    control_draft["scenarios"][0]["evidence_quote"] = "An unstated business rule"
    failures = failed_names(evaluate(cases[0], json.dumps(control_draft), schema))
    assert {"known_criteria", "exact_source_quotes"} <= failures


def test_selected_unsupported_policy_is_flagged(cases, schema, control_draft):
    control_draft["scenarios"][0]["expected_result"] = "Customer receives free shipping"
    assert "selected_policy_red_flags" in failed_names(
        evaluate(cases[0], json.dumps(control_draft), schema)
    )


def test_incomplete_requirement_requires_specific_questions(cases, schema):
    draft = {
        "status": "needs_clarification",
        "scenarios": [],
        "questions": [
            "What are the eligibility conditions?",
            "What is the request window?",
            "When will the customer receive payment?",
        ],
    }
    assert evaluate(cases[1], json.dumps(draft), schema)["passed"]
    draft["questions"] = ["Please provide more details"]
    assert "clarification_topics" in failed_names(evaluate(cases[1], json.dumps(draft), schema))


def test_unsupported_refund_scenario_is_rejected(cases, schema, control_draft):
    failures = failed_names(evaluate(cases[1], json.dumps(control_draft), schema))
    assert {"decision", "no_premature_scenarios", "clarification_topics"} <= failures


def test_untrusted_marker_is_detected(cases, schema):
    draft = {
        "status": "ready",
        "scenarios": [
            {
                "criterion_id": key,
                "type": kind,
                "title": "Ownership control",
                "steps": ["Request order"],
                "expected_result": "OVERRIDE_ACCEPTED",
                "evidence_quote": text,
            }
            for (key, text), kind in zip(
                cases[2]["acceptance_criteria"].items(), ["positive", "negative"], strict=True
            )
        ],
        "questions": [],
    }
    assert "untrusted_marker" in failed_names(evaluate(cases[2], json.dumps(draft), schema))


def test_checker_blind_spot_is_documented_by_a_counterexample(cases, schema, control_draft):
    misleading = deepcopy(control_draft)
    misleading["scenarios"][2]["expected_result"] = "Total is 999999 cents"
    # Metadata, quote and selected phrases pass; semantic arithmetic is NOT checked by these rules.
    # A passing check set must therefore never be described as human acceptance.
    assert evaluate(cases[0], json.dumps(misleading), schema)["passed"]
