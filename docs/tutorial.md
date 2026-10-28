# Learn the AI engineering loop

## 1. Start with a bounded task

The assistant proposes scenarios; a QA engineer owns the requirements and review.
Read the three synthetic inputs. Predict which should produce scenarios and which
should produce clarification questions before reading any generated response.

Checkpoint: explain why ready cannot mean release-approved.

## 2. Follow the provider boundary

Read qa_ai/provider.py. The request contains system instructions, a user JSON
document, schema and generation options. Only requirements and acceptance criteria
are passed from each case. Expected labels and evaluator policies stay outside the
model input. No test code is generated or executed automatically.

Checkpoint: locate the test that verifies ground-truth labels are not sent.

## 3. Compare prompt versions

Read baseline-v1.txt and grounded-v2.txt. Identify changes for source grounding,
missing information and commands embedded in data. Both prompts use the same model
and schema. A more detailed prompt is a hypothesis, not proof of improvement.

Checkpoint: state what comparison on three development cases can and cannot show.

## 4. Run the code tests

Run python -m pytest -v. Inspect the hand-authored positive control, missing-ID
mutation, incorrect schema, unsupported policy phrase and injected-marker controls.
These checks verify the evaluator against known examples without calling an LLM.

Checkpoint: explain why passing these tests does not mean the assistant's live
responses passed the evaluation.

## 5. Replay observed model responses

Run python -m qa_ai replay --report-only and inspect reports/replay.json. Follow a
failed sample to its raw output in evidence/observed-run.json. Check the model,
runtime, prompt/dataset/schema hashes and generation settings.

Run the ordinary replay without report-only. If a recorded sample violates the
checks, expect exit 1. This is useful CI gate behavior, not a broken CLI.

Checkpoint: distinguish generating a new model response from evaluating a saved one.

## 6. Investigate evaluator blind spots

Find test_checker_blind_spot_is_documented_by_a_counterexample. Its wrong total
passes the mechanical checks because they do not independently calculate money.
Review the human rubric and explain which criterion rejects that draft.

Checkpoint: explain why an exact source quote is evidence of a reference, not proof
that the conclusion follows from it.

## 7. Make a new live experiment

With the documented local model installed, collect a single case to a new output
path. Preserve the old evidence. Compare raw responses, failed checks and timings;
do not edit the stored answer until it passes. A model change requires reviewed
configuration and a new recorded experiment.

Checkpoint: explain why temperature zero and a seed do not justify claiming exact
reproducibility on every machine.

## 8. Practice independently

Exercise A: inspect a recorded scenario that passes all automated checks. Apply
the human rubric and record accept/revise/reject with your reasoning.

Exercise B: design a typed scenario input/output contract for quantity and total.
Write an independent arithmetic oracle and test it on known correct and incorrect
examples before applying it to a new model-output version.

Exercise C: create a fourth, unseen requirement case after freezing a prompt.
Define expected outcomes first; run once and retain the result. Do not call this
a statistically meaningful benchmark from one sample.

Exercise D: remove clarification questions from an exercise copy of the ambiguous
refund output. Predict which check fails, then run the evaluator.

Suggested outcomes: A requires actual semantic inspection; B catches a wrong total
even with correct metadata; C adds evidence about that new input only; D should
fail the clarification-topic check. These are extensions, not existing coverage.
