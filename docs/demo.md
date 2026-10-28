# An 8–10 minute demonstration

1. **The problem.** Show fictional requirements and ask whether an AI draft should
   be trusted just because it is readable. Explain that the QA retains ownership.
2. **The contract.** Show schema, prompt versions and the three cases. Distinguish
   acceptance criteria given to the model from evaluation labels kept outside it.
3. **The code.** Follow the local provider request, model digest check, evaluation
   function and saved metadata. Explain what structured output guarantees.
4. **The experiment.** Open the observed results and one raw failure. Compare the
   two prompt versions without claiming broad accuracy from the small dataset.
5. **The checker.** Run pytest and replay. Explain why the harness can be green
   while a model sample has failed checks. Demonstrate ordinary replay exit 1 when
   appropriate; report-only is for inspection, not acceptance.
6. **The blind spot.** Show the wrong-total counterexample and human-review rubric.
   Explain why ID coverage, quotes and keyword matching are incomplete proxies.
7. **The engineering lesson.** Describe the next step: stronger independent oracles,
   held-out cases, repeated runs and human calibration. Keep client examples private.

Prepare dependencies before presenting. Offline replay is sufficient for a short
video; explicitly call it recorded evidence. A live model demo needs Ollama and
the verified weights and may take longer than the presentation slot.

Practice questions: Is this model training? What changes when the prompt changes?
Why version the dataset? Why preserve failed answers? What does a schema miss?
Which failures are code, transport, model behavior or evaluator limitations?
What is the difference between assisted inspection and independent human approval?
