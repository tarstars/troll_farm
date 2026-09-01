---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: claude_1
to: ["local_claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260901T163432Z-20260829-nn-bot-way-b-lever-price-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/claude_1/20260901T162243Z-20260829-nn-bot-way-b-lever-price-handoff.md"]
artifact_ref: agent/claude_1
artifact_commit: 70085373e5881220eb3a918f2a5cbc2206588066
artifact_paths: ["claude_1/results/nn-bot-lever-price/LEVER-PRICE-2026-09-01.md", "claude_1/results/nn-bot-lever-price/lever-price-2026-09-01.json", "claude_1/results/nn-bot-lever-price/lever-price-seed910.json", "claude_1/results/nn-bot-lever-price/lever-price-seed911.json", "claude_1/nn-bot/lever_price.py", "tests/test_lever_price.py"]
created_utc: 2026-09-01T16:34:32Z
---

- To: local_claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — evidence for step 5's pending decision

# HANDOFF — the first two levers priced offline, now on three seeds

This replaces my 16:22Z handoff (named in `supersedes`) so you read one message, not two. The
conclusion is unchanged; the one-seed limitation I stated in it is removed. Read this pin.

## What was measured

The fix menu is with the owner and nothing is launched, but the record did not say **how much**
levers 1 and 2 move the credit composition they both aim at, and each costs a cluster arm plus a
144-cell gate to find out. So: one rollout collected with the clone itself (`970097ed…`, the
clone both entropy arms started from), the **same recorded action sequence** replayed under each
other reward split, and the **same buffer** re-cut into 32- and 128-mini-step windows. One set of
games carries every number; only the levers move. That this is sound — the split being an output
of the simulator, not an input — is checked, not assumed: every replay reproduced its collection's
state hashes, turn boundaries and endings exactly, in all three seeds. The decomposition is not
re-implemented: the instrument loads `train_ppo_full.py` and calls its own `compute_gae` and
`rollout_credit_telemetry`, with `--reward-credit executing` applied as the trainer applies it.
Per seed: 64 environments × 1,024 mini-steps after an 896-step burn-in = 65,536 rows, ~21,500
turns, `champion_exact`, `plan-critic`, γ 0.999, λ 0.95.

## The two numbers

| seed | endings | reward rows `0+4` | `0.5+3.5` | `2+2` | **lever 1** | traced w32 | traced w128 | **lever 2** |
|---|---|---|---|---|---|---|---|---|
| 909 | 88 | 88 | 1,782 | 1,781 | **20.2×** | 1.46 % | 6.21 % | **4.3×** |
| 910 | 82 | 82 | 1,671 | 1,671 | **20.4×** | 1.46 % | 5.79 % | **4.0×** |
| 911 | 84 | 84 | 1,764 | 1,764 | **21.0×** | 1.10 % | 4.85 % | **4.4×** |

**Lever 1 — the wood split.** Under `0+4` the only rows in the buffer carrying any observed
reward are the ones that are episode endings: **88 of 65,536, 0.13 %.** That holds *exactly* in
every seed — reward rows equal endings, 88/88, 82/82, 84/84 — so it is not an estimate. 99.87 % of
the rows the trainer learns from have nothing but the critic to learn from, which is the 97.68 %
restated in a form that does not depend on what the value head outputs. Turning shaping on moves
that to 2.7 %, a factor of about 20.

**But the coverage is bought by turning shaping on at all, not by its size.** `0.5+3.5` and
`2+2` put reward on the same rows to within one, in every seed — the wood deliveries. Between
them only the per-delivery magnitude differs. If there is a reason to prefer `2+2` over the
environment's own default it is the size of the immediate signal, not how many rows stop being
blind. That is the one thing from this I would put in front of the owner.

**Lever 2 — the longer rollout.** Traces reaching a real ending go from 1.46 % to 6.21 % of plan
rows, about 4.3×. **This is also the calibration:** your measurement of record puts that fraction
at 1.8 % on real runs at the same window size, and this reads 1.46 / 1.46 / 1.10 % across seeds —
same quantity, same scale, so the factor is trustworthy.

The two levers act on different rows — deliveries scattered through the game versus rows near an
ending — so neither subsumes the other, and running one first costs the other nothing.

## What I am not claiming

**The share-of-signal number is not comparable to the 2.32 % and is not a headline here.**
Measured, not guessed: the clone's value head returns |V| ≈ 0.79 (max 1.42) while a terminal
reward is about 75, whereas the runs of record had a critic warmed up for 300 updates on the scale
of the returns. Priced at the cold clone the ratio inverts and would say nothing about a run in
progress. Every number above is deliberately critic-independent — counts of rows, shares of rows,
trace reach. A comparable share needs a warmed-up critic, which is a training run, which is what
the arm itself does: a reason to run the arm, not a substitute for it. Remaining limits: one
64-environment sample per seed, one opponent, and the clone rather than a mid-run policy.

## What is asked of you

Nothing decided, nothing launched, no platform action — this is evidence for the owner's choice
beside your recommendation and chatgpt_1's ranking, not a ranking of my own. Take it or reject it
on the method.

Report `claude_1/results/nn-bot-lever-price/LEVER-PRICE-2026-09-01.md`, every number with the
command that made it. Instrument `claude_1/nn-bot/lever_price.py`, 8 tests each written and
watched to fail before its code; `tests/test_lever_price.py` 8/8, and the 79 tests of
`test_train_ppo_full`, `test_rl_full_env` and `test_credit_path_read` still pass. Four minutes
a seed at nice 19.
