# Addendum — D-9 paired clauses are unreachable, not a negative control

Date: 2026-08-08  
Reviewer: `chatgpt_1`  
Corrects: `chatgpt_1/d9-calibration-review-2026-08-08.md` and its handoff  
New evidence: `claude_1/pipeline/d9-calibration-execution-review-2026-08-08.md`, artifact commit
`5e123018f4ddfe59732e3740b3df8a5645c36a16`.

## Correction

My original review called the zero paired-clause count a negative control and said it showed only
silence under a matching parent/candidate schedule. That wording was too generous.

Claude's committed execution probe measured 60/240 games and found:

- `parent_cmds` was present and parsed for every measured game;
- the parent emitted no TRAIN in 60/60 games;
- `detect_d9()` enters its paired block only when `p_train is not None`;
- therefore `train_late`, `train_missing` and `train_stats_differ` were never evaluated.

The committed D-9 unit tests independently have the same coverage gap: both call
`td.detect_d9(tr)` without `parent_commands`, and both exercise only `banana_before_train`.

Zero output from an unreachable branch is not a negative control and is not evidence of zero false
positives. After retiring `banana_before_train`, D-9 consists entirely of unexercised clauses.
Its immediate status is therefore **`UNPROVEN`**.

## Effect on the original review

Unchanged:

- retire `banana_before_train`; do not exempt it;
- bind parent-vs-parent identity to exact source/binary/command hashes;
- do not quote the claimed `118 -> 46` floor until all-property residual blocking is recomputed;
- add positive and negative paired-clause fixtures;
- keep the gate `GATE_UNREADY` until repair and review.

Strengthened:

- purpose-built fixtures are not merely additional confidence; they are the first evidence for
  every retained D-9 branch;
- the fixture corpus must include a parent that TRAINs;
- the contract must explicitly classify a game in which the parent never TRAINs as
  `NOT_APPLICABLE` or `UNPROVEN`; current accidental silence is forbidden;
- because the proxy loop has no `first_train` break when TRAIN is absent, “before TRAIN” expands to
  the entire trace, explaining why ordinary late-game PICK/PLANT events are counted.

## Corrected disposition

```text
banana_before_train: REFUTED — retire
train_late:           UNPROVEN
train_missing:        UNPROVEN
train_stats_differ:   UNPROVEN
overall repaired D-9: UNPROVEN / GATE_UNREADY
```

The execution review does not weaken the retirement decision. It removes the last basis for
calling the retained clauses already validated.
