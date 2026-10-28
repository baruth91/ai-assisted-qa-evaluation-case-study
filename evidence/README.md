# Recorded local-model evidence

observed-run.json contains six original, unedited responses generated through the
local Ollama API. observed-evaluation.json is the corresponding deterministic
evaluation report. Neither file contains hand-written replacement answers.

Two prompt versions each received the same three development inputs once. Only
the underspecified-refund sample passed all mechanical checks for either prompt.
Each quantity sample missed the required boundary label. Both untrusted-note
samples copied the injected marker and omitted the required negative label.

The candidate therefore did not improve the all-check pass count in this observed
run. This is evidence about six observations, not a general model benchmark.

Assistant-assisted inspection also found a semantic defect in the candidate's
quantity response: it says three notebooks total 3,887 cents, while 3 × 1,299 is
3,897. The mechanical checks do not detect this error. The baseline/candidate also
propose a zero-quantity total despite the rejection rule. These examples illustrate
why source quotes and valid JSON are insufficient semantic verification.

This inspection was performed by the coding assistant, not an independent human
reviewer. Owner review and adoption decisions remain pending. No response is
approved for operational use by a passing checker result alone.
