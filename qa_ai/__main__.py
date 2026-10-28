"""Generate, evaluate and replay QA drafts, with provenance and explicit exit behavior."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from qa_ai.evaluation import evaluate
from qa_ai.provider import client, generate, model_metadata

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_inputs():
    cases_text = (ROOT / "data/development-cases.json").read_text(encoding="utf-8")
    schema_text = (ROOT / "data/draft.schema.json").read_text(encoding="utf-8")
    return json.loads(cases_text), json.loads(schema_text), digest(cases_text), digest(schema_text)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def report(records, cases, schema):
    indexed = {case["id"]: case for case in cases}
    samples = [
        {
            "case_id": record["case_id"],
            "prompt": record["prompt"],
            "evaluation": evaluate(indexed[record["case_id"]], record["raw_output"], schema),
        }
        for record in records
    ]
    return {
        "sample_count": len(samples),
        "passed_samples": sum(sample["evaluation"]["passed"] for sample in samples),
        "human_approval": "not_established",
        "samples": samples,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="Generate real local-model responses")
    collect.add_argument("--base-url", default="http://127.0.0.1:11434")
    collect.add_argument("--output", type=Path, default=ROOT / "reports/live-records.json")
    collect.add_argument("--prompt", choices=["baseline-v1", "grounded-v2", "both"], default="both")
    collect.add_argument(
        "--case", choices=["quantity-and-price", "underspecified-refund", "untrusted-note"]
    )
    replay = subparsers.add_parser("replay", help="Evaluate saved responses; makes no model call")
    replay.add_argument("--input", type=Path, default=ROOT / "evidence/observed-run.json")
    replay.add_argument("--output", type=Path, default=ROOT / "reports/replay.json")
    replay.add_argument("--prompt", choices=["baseline-v1", "grounded-v2"])
    replay.add_argument(
        "--report-only",
        action="store_true",
        help="Exit 0 after successful reporting, even if model checks fail",
    )
    args = parser.parse_args()
    cases, schema, cases_hash, schema_hash = load_inputs()

    if args.command == "collect":
        if args.output.exists():
            parser.error("Output exists; choose a new path to preserve prior evidence")
        config = json.loads((ROOT / "config/ollama.json").read_text(encoding="utf-8"))
        records = []
        names = ["baseline-v1", "grounded-v2"] if args.prompt == "both" else [args.prompt]
        selected = [case for case in cases if args.case is None or case["id"] == args.case]
        with client(args.base_url) as session:
            metadata = model_metadata(session, args.base_url, config)
            for name in names:
                prompt = (ROOT / f"prompts/{name}.txt").read_text(encoding="utf-8")
                for case in selected:
                    print(f"Generating {name} / {case['id']}...", flush=True)
                    generated = generate(session, args.base_url, config, prompt, case, schema)
                    record = {
                        "case_id": case["id"],
                        "prompt": name,
                        "prompt_sha256": digest(prompt),
                        "dataset_sha256": cases_hash,
                        "schema_sha256": schema_hash,
                        "options": config["options"],
                        "generated_at": datetime.now(UTC).isoformat(),
                        **metadata,
                        **generated,
                        "raw_output_sha256": digest(generated["raw_output"]),
                    }
                    records.append(record)
                    write_json(args.output, records)
                    result = evaluate(case, generated["raw_output"], schema)
                    failed = [c["name"] for c in result["checks"] if not c["passed"]]
                    print(f"Recorded. Failed checks: {failed}", flush=True)
        result = report(records, selected, schema)
        write_json(args.output.with_suffix(".evaluation.json"), result)
    else:
        records = json.loads(args.input.read_text(encoding="utf-8"))
        if not records:
            parser.error("No recorded samples to evaluate")
        for record in records:
            if record["prompt"] not in {"baseline-v1", "grounded-v2"}:
                parser.error("Unknown recorded prompt version")
            prompt = (ROOT / f"prompts/{record['prompt']}.txt").read_text(encoding="utf-8")
            if (
                record["dataset_sha256"] != cases_hash
                or record["schema_sha256"] != schema_hash
                or record["prompt_sha256"] != digest(prompt)
                or record["raw_output_sha256"] != digest(record["raw_output"])
            ):
                parser.error("Evidence does not match the current prompt/dataset/schema")
        if args.prompt:
            records = [record for record in records if record["prompt"] == args.prompt]
        if not records:
            parser.error("No samples match the selected prompt")
        result = report(records, cases, schema)
        write_json(args.output, result)
    print(
        f"Checks passed for {result['passed_samples']}/{result['sample_count']} recorded samples."
    )
    print("Human semantic review remains required; see the documented rubric.")
    failed = result["passed_samples"] != result["sample_count"]
    return 1 if failed and not getattr(args, "report_only", False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
