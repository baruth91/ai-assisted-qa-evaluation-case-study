# Engineering decisions

## Engineering with an existing model

The project integrates an existing local Llama model; it does not train one. Python
owns request construction, a fixed schema, evaluation, provenance and reporting.
The model proposes content within that boundary. There are no autonomous tools,
agent loops, code execution, RAG index or unnecessary orchestration dependencies.

## Local Ollama adapter

The developer environment already had Ollama and the selected model available.
Using that installation enables real inference evidence without a paid API key.
Requests are restricted to loopback in this adapter and machine HTTP proxies are
disabled. The application sends only the synthetic requirements and criteria,
never the evaluator labels, CV, client material or environment secrets.

The expected model digest is checked before inference. Runtime version and
sampling options are recorded. A stable seed and zero temperature aid comparison
but do not guarantee identical cross-platform results. Runtime installation and
model download remain separate prerequisites for new live runs.

## Version prompts, inputs and evidence

The initial dataset, prompt versions, schema and model configuration were committed
before generation. Records contain their hashes and the raw output hash. Replay
refuses drift. Hashes detect accidental mismatch; they are not signatures proving
that a trusted third party generated the text.

Outputs are saved after each request to preserve progress if a later request
fails. A transport failure is not an evaluation pass. Existing evidence files are
not overwritten by collection. Model-generated text is always data, never shell
commands or instructions to this application.

## Keep code tests separate from model evaluations

Pytest uses hand-authored positive and negative controls for the checker. Those
controls are explicitly labelled and are not model output. Offline replay uses
separate captured real outputs. Hosted CI can test the system without requiring
GPU resources or exposing provider credentials.

The report-only default is explicit in workflow names and documentation. A model
failure remains a model failure in the report; a green harness badge means code
and replay infrastructure worked. Enabling the candidate gate adds an automated
acceptance decision for the recorded candidate samples only, with the stated
semantic blind spots.

## Preserve honest scope

The phrase checks are deliberately narrow and the development set is tiny. No
general hallucination, security, accuracy or professional-expertise claim follows
from a pass. Promptfoo and provider alternatives can be added later when they solve
a concrete evaluation need. Independent semantic oracles and human review are a
higher priority than increasing the number of tools in this first repository.
