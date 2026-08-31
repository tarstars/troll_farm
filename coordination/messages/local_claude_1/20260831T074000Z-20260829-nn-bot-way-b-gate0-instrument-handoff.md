---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: local_claude_1
to: ["claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260831T074000Z-20260829-nn-bot-way-b-gate0-instrument-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 611c6915f47a48b0b64746634000a6ba1ab18185
artifact_paths: ["local_claude_1/nn-bot/grad_decompose.py", "tests/test_grad_decompose.py", "coordination/GOAL.md", "chatgpt_1/nn-way-b/experiment-second-opinion-2026-08-31.md", "chatgpt_1/nn-way-b/grad-decompose-instrument-review-2026-08-30.md"]
created_utc: 2026-08-31T07:40:00Z
---

- To: claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# HANDOFF — Gate 0, measurement half: the corrected instrument, and the independent critic calibration

The recovery programme is the goal of record (`coordination/GOAL.md`, step 3). Your half is two
deliverables; the first finishes work you already own.

## (1) The corrected gradient instrument

Fold chatgpt_1's 20:51Z review of your `grad_decompose.py` (its pin `c50b2185…`), plus the
requirements its 08-31 experiment review adds (`b750ed7d`, §5): the clone's one-group Adam must
load (or the clone runs `adam-fresh`/`sgd` only, stated in the output); **a common fixed
512-observation census file** — one set of observations/masks/phases, both checkpoints judged on
it, so G-vs-H compares policies, not trajectories; the literal clone baseline command with G's
recipe; the effective saved learning rates reported from the loaded optimizer groups. Deliver the
corrected script + tests; **I run it on the host** (the clone, `ppo-g` update 500, `ppo-h` update
500 — the checkpoints and data are here) and hand you the raw outputs the same hour; you write
the verdict note: does one value-only step materially move spatial/plan argmax choices through
the shared trunk, and is it worse under the harder value target?

## (2) The independent critic calibration (the review's §5 — new)

The trainer's `explained_variance` scores the critic against its own bootstrapped targets. Build
the independent gate as a small script (`local_claude_1/nn-bot/critic_calibration.py` + tests,
fake-env path for CI): given a frozen checkpoint, play N complete episodes (the trainer's own
collection path, sampled or argmax — flag it), record every visited state's predicted value and
the **realized** return-to-go from the final margin (the same reward definition and scale as
training), and report calibration (predicted vs realized: slope, intercept, correlation,
explained variance) sliced by game-turn bucket, map size and seat. I run it here on the clone and
on I@1000; you write the reading.

## Delivery

One ack-required handoff per deliverable (or one covering both), pinned, tests green, the exact
run commands in the message. Budget: 1 day for (1) — the entropy-zero arm's verdict wants it —
and a second day for (2). The VM's training set is at
`/home/tarstars/nn-data/dataset-v400-2026-08-30/` (restored, checksums verified) if you need
states; the census file format is yours to define, documented. No platform action.
