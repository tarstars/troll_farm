# Pool #4 margin-decomposition v2 review — 2026-08-17

Verdict: **REVISION_REQUIRED** (narrow presentation cleanup; paired inference accepted).

Pinned artifact: `a6fe408d527726ce15246cd3c75b4232401aa691`.

## Reproduction

Running `local_claude_1/pool4/decompose.py` reproduces the revised primary results:

- stall vs no-stall: 17 discordant map pairs, mean delta −24.29, exact one-sided
  sign-flip p = 0.0000153;
- dance-only vs clean: 14 discordant map pairs, mean delta −7.07, exact one-sided
  sign-flip p = 0.1340.

The report now correctly withdraws the dance-marker finding, uses association
language, labels 1.41 as a conditional bring-to-par scenario, and defines episode
duration as a transition count.

## Remaining blocking inconsistencies

1. The script has two active `if __name__ == "__main__"` blocks. A normal run first
   prints the superseded row-wise permutation results — including the misleading
   dance-only `p=0.0053` — and only then prints the blocked results. “v1 retained for
   the record” does not label those runtime lines as invalid/superseded. Make the
   default executable emit only the v2 analysis, or label the old output explicitly
   enough that it cannot be consumed as current inference.
2. The report carefully defines 1.41 as “not a ceiling, not a causal estimate” in
   §2, but the verdict-session paragraph later calls it “the recoverable amount.”
   That reintroduces the causal/fixability implication the revision was meant to
   remove. Keep “bring-to-par scenario” language at the downstream use site too.

No additional statistical revision is requested. Once those two presentation
contradictions are removed, the method gate is acceptable.

