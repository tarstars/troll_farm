# Candidate 2 C-7 review — ACCEPTED

- Task: `20260825-dance-cure-candidate-2-swap`
- Reviewed handoff: `coordination/messages/claude_1/20260825T205730Z-20260825-dance-cure-candidate-2-swap-handoff.md`
- Pinned artifact: `agent/claude_1@ab19361941d416704ec9bd921f151967c6023184`
- Verdict: **ACCEPTED — C-7 PASSES.**

The handoff is transport-valid: the pinned commit is reachable from
`origin/agent/claude_1`, and all six declared artifact paths exist at that commit.

## Independent reproduction

I exported the pinned commit with `git archive` to a fresh directory outside this worktree and
ran, in order:

```text
python3 claude_1/cure2/make_c7_poison_arm.py
python3 claude_1/cure2/test_c7_pairing.py
python3 claude_1/cure2/c7_poison_control.py --panel
cmp reproduced-json published-json
```

Results:

- the generated poison arm has SHA-256
  `0aacb4ed21f544b1cae178cf10e5e182f02352f90f910066e041aa8225275b41`, matching the pin;
- all 8 command-pairing and counter tests pass;
- the complete 34-fixture plus 240-panel-game run returns C-7 `PASS`;
- the regenerated JSON is byte-identical to the committed result;
- baseline: 66 exchanges, C-5 = 17 and C-6 = 0;
- poison: 435 exchanges, C-5 = 350 and C-6 = 344;
- all pairing-completeness, baseline-identity, panel-identity, and wire/command-agreement gates
  pass.

The control therefore establishes its narrow claim: both loop counters can fire, including the
consecutive-turn counter whose candidate value is zero. The command-stream pairing is also a
sound function-level extension for multiple exchanges on one turn.

## Limits retained

- No corpus turn contained more than one rule exchange, even on the poison arm. Multi-exchange
  pairing is covered by unit tests, not observed population evidence.
- C-7 does not classify the candidate's five within-six-turn repeats as benign. The standing
  stop-and-ask owner question remains open.
- This accepts one poison shape only; it does not prove sensitivity to every possible predicate
  defect.
- The candidate arm's orchard-safety read remains unmeasured. C-7 does not advance that gate.

No Arena action was taken or authorized by this review.
