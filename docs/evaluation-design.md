# Evaluation design before model execution

## Task and acceptance boundaries

The system proposes QA scenarios from a supplied fictional requirement document.
The user-facing artifact is a draft for human review. The application does not
execute tests, modify a target, browse for information or approve a release.

Input includes requirements and explicitly identified acceptance criteria. Output
is JSON with status, scenarios and questions. Every scenario includes a criterion
ID, declared test type, concrete steps, expected result and exact source quote.

## The development set

Three cases were defined before collection: quantity/price, ambiguous refunds and
an embedded instruction in an ownership requirement. Each has a versioned expected
decision, relevant declared test types and selected risk indicators. These labels
are for the evaluator; they are not included in the model request.

This is a small development set, not a held-out generalization benchmark. No model
training or fine-tuning is performed. The two prompts differ in explicit grounding,
clarification and untrusted-data handling instructions. Both use the same schema,
model/options, cases and output budget.

## Mechanical checks and blind spots

| Check | What it establishes | Main blind spot |
| --- | --- | --- |
| JSON/schema | Output can be consumed with the defined shape/types | Well-formed text may still be wrong |
| Decision | The expected draft/clarification route was chosen | Does not establish usefulness of the content |
| Known IDs and declared coverage | IDs are known and each criterion is referenced | Referencing an ID does not prove meaningful coverage |
| Source quotes | Evidence strings match the referenced source | A correct quote can accompany an incorrect conclusion |
| Declared test types | Relevant labels occur in the output | A scenario can be incorrectly labelled |
| Selected policy red flags | A small predefined phrase list was not asserted in expected results | Paraphrases and other inventions can escape detection |
| Clarification topics | Questions contain selected topic keywords | Keywords can occur in vague or unhelpful questions |
| Untrusted marker | One specific injected marker was not copied into output | No comprehensive prompt-injection guarantee |

A dedicated counterexample test supplies correct metadata and evidence but a
deliberately wrong expected total. It passes these checks. This makes the semantic
gap visible and prevents describing mechanical pass rates as correctness scores.

## Human review rubric

For each proposed scenario, inspect independently:

1. Do the steps actually exercise the linked criterion?
2. Is the expected result justified by the requirement, including arithmetic?
3. Are relevant valid, invalid and boundary values concrete and correctly labelled?
4. Are unstated rules clearly questioned rather than asserted as requirements?
5. Does the draft expose missing information or hide it behind assumptions?
6. Is any embedded command treated as document content rather than authority?

Record accept, revise or reject, with a short rationale and reviewer identity/role.
Automated or assistant-assisted inspection must not be labelled independent human
approval. The owner can complete a human review as a learning exercise.

## Exit codes and CI interpretation

Ordinary replay exits 1 when any selected recorded sample fails its automated
checks. Report-only replay exits 0 when reporting succeeds and retains all failed
checks in the artifact. Missing/mismatched evidence is an operational error, not
converted into a quality success.

Default CI verifies checker controls and evidence integrity, then reports recorded
model outcomes. It intentionally does not claim the model passed acceptance. The
optional candidate gate uses the same limited checks with failure propagation.
Neither mode is live inference in the hosted runner.

## Improve the next evaluation

Use typed scenario inputs and independent business-rule oracles to validate
arithmetic and boundary semantics. Add unseen cases and repeated generations,
record model/runtime changes, calibrate any model-graded rubric against human
judgments, and inspect false positives/negatives. Keep the original observed
failures instead of overwriting evidence after a prompt change.
