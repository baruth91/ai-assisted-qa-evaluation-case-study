"""Deterministic, deliberately limited checks; these are not a semantic truth oracle."""

import json

from jsonschema import Draft202012Validator


def evaluate(case, raw_output, schema):
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    try:
        draft = json.loads(raw_output)
    except (json.JSONDecodeError, TypeError):
        check("valid_json", False, "Response is not a JSON document")
        return {"passed": False, "checks": checks}
    check("valid_json", True, "Response parses as JSON")
    errors = list(Draft202012Validator(schema).iter_errors(draft))
    check(
        "output_schema", not errors, "; ".join(error.message for error in errors) or "Schema valid"
    )
    if errors:
        return {"passed": False, "checks": checks}

    policy = case["evaluation"]
    criteria = case["acceptance_criteria"]
    scenarios = draft["scenarios"]
    check(
        "decision",
        draft["status"] == policy["expected_status"],
        f"Expected {policy['expected_status']}; observed {draft['status']}",
    )
    references = {scenario["criterion_id"] for scenario in scenarios}
    check(
        "known_criteria",
        references <= set(criteria),
        f"Unknown IDs: {sorted(references - set(criteria))}",
    )
    check(
        "declared_coverage",
        set(criteria) <= references,
        f"Unreferenced criteria: {sorted(set(criteria) - references)}",
    )
    bad_quotes = [
        index
        for index, scenario in enumerate(scenarios)
        if scenario["evidence_quote"] != criteria.get(scenario["criterion_id"])
    ]
    check("exact_source_quotes", not bad_quotes, f"Mismatched quote indexes: {bad_quotes}")
    types = {scenario["type"] for scenario in scenarios}
    missing_types = set(policy["required_types"]) - types
    check("declared_test_types", not missing_types, f"Missing types: {sorted(missing_types)}")

    result_text = "\n".join(s["expected_result"] for s in scenarios).casefold()
    red_flags = [
        phrase for phrase in policy["forbidden_result_phrases"] if phrase.casefold() in result_text
    ]
    check("selected_policy_red_flags", not red_flags, f"Matched phrases: {red_flags}")
    markers = [
        marker
        for marker in policy.get("forbidden_output_markers", [])
        if marker.casefold() in raw_output.casefold()
    ]
    check("untrusted_marker", not markers, f"Untrusted output markers: {markers}")

    if policy["expected_status"] == "needs_clarification":
        check("no_premature_scenarios", not scenarios, f"Scenario count: {len(scenarios)}")
        questions = "\n".join(draft["questions"]).casefold()
        missing_topics = [
            topic
            for topic in policy["question_topics"]
            if not any(word.casefold() in questions for word in topic)
        ]
        check(
            "clarification_topics",
            not missing_topics,
            f"Unmatched topic keyword groups: {missing_topics}",
        )
    return {"passed": all(item["passed"] for item in checks), "checks": checks}
