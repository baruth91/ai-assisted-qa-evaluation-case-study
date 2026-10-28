import json
import subprocess
import sys

import pytest

from qa_ai.__main__ import ROOT, digest, load_inputs, report


def records():
    return json.loads((ROOT / "evidence/observed-run.json").read_text(encoding="utf-8"))


def test_real_capture_has_the_expected_inputs_and_provenance():
    cases, _schema, cases_hash, schema_hash = load_inputs()
    captured = records()
    assert {(r["prompt"], r["case_id"]) for r in captured} == {
        (prompt, case["id"]) for prompt in ("baseline-v1", "grounded-v2") for case in cases
    }
    assert len(captured) == 6
    config = json.loads((ROOT / "config/ollama.json").read_text(encoding="utf-8"))
    for record in captured:
        prompt = (ROOT / f"prompts/{record['prompt']}.txt").read_text(encoding="utf-8")
        assert record["dataset_sha256"] == cases_hash
        assert record["schema_sha256"] == schema_hash
        assert record["prompt_sha256"] == digest(prompt)
        assert record["raw_output_sha256"] == digest(record["raw_output"])
        assert record["model_digest"] == config["expected_digest"]
        assert record["options"] == config["options"]
        assert record["provider"] == "ollama"
        assert record["runtime_version"] == "0.40.5"
        assert record["done_reason"] == "stop"
        assert record["completion_tokens"] > 0


def test_recorded_outcomes_remain_visible_in_replay():
    cases, schema, _cases_hash, _schema_hash = load_inputs()
    replayed = report(records(), cases, schema)
    observed = json.loads((ROOT / "evidence/observed-evaluation.json").read_text(encoding="utf-8"))
    assert replayed == observed
    assert replayed["passed_samples"] == 2
    assert replayed["human_approval"] == "not_established"
    for sample in replayed["samples"]:
        assert sample["evaluation"]["passed"] == (sample["case_id"] == "underspecified-refund")


@pytest.mark.parametrize(
    "options, expected_exit",
    [
        ([], 1),
        (["--report-only"], 0),
        (["--prompt", "grounded-v2"], 1),
    ],
)
def test_cli_distinguishes_reporting_from_candidate_acceptance(tmp_path, options, expected_exit):
    output = tmp_path / "evaluation.json"
    result = subprocess.run(
        [sys.executable, "-m", "qa_ai", "replay", "--output", str(output), *options],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == expected_exit, result.stderr
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["passed_samples"] < saved["sample_count"]
    assert saved["human_approval"] == "not_established"


def test_modified_capture_is_refused_before_reporting(tmp_path):
    captured = records()
    captured[0]["raw_output"] = "{}"
    source = tmp_path / "modified.json"
    source.write_text(json.dumps(captured), encoding="utf-8")
    output = tmp_path / "must-not-exist.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "qa_ai",
            "replay",
            "--input",
            str(source),
            "--output",
            str(output),
            "--report-only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "does not match" in result.stderr
    assert not output.exists()
