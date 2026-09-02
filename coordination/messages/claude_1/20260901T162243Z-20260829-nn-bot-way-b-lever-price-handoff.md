---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: claude_1
to: ["local_claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260901T162243Z-20260829-nn-bot-way-b-lever-price-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 8c04fe08054e842f86d28c14459c0e02982cdff8
artifact_paths: ["claude_1/results/nn-bot-lever-price/LEVER-PRICE-2026-09-01.md", "claude_1/results/nn-bot-lever-price/lever-price-2026-09-01.json", "claude_1/nn-bot/lever_price.py", "tests/test_lever_price.py"]
created_utc: 2026-09-01T16:22:43Z
---

- To: local_claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — evidence for step 5's pending decision

# HANDOFF — the first two levers priced offline, before either costs a cluster arm

The fix menu is with the owner and nothing is launched. What the record did not have is **how
much** levers 1 and 2 actually move the credit composition they both aim at. This measures both,
from one collection, with no training, no cluster and no platform action.

## Method, in one paragraph

One rollout collected with the clone itself (`970097ed…`, the clone both entropy arms started
from); the **same recorded action sequence** replayed in a fresh environment under each other
reward split; the **same buffer** re-cut into 32- and 128-mini-step windows. So one set of games
carries every number and only the levers move. The soundness condition — that the reward split is
an output of the simulator, not an input — is checked rather than assumed: every replay reproduces
the collection's state hashes, turn boundaries and endings exactly. The decomposition is not
re-implemented: the instrument loads `train_ppo_full.py` and calls its own `compute_gae` and
`rollout_credit_telemetry`, with `--reward-credit executing` applied as the trainer applies it.
Sample: 64 environments × 1,024 mini-steps after an 896-step burn-in = 65,536 rows, 21,630 turns,
88 endings, `champion_exact`, `plan-critic`, γ 0.999, λ 0.95.

## Lever 1 — the wood split: reward on 20× more rows

| split | rows carrying observed reward | share of rows |
|---|---|---|
| **0 + 4** (every run of record) | **88** | **0.13 %** |
| 0.5 + 3.5 (the environment's default) | 1,782 | 2.72 % |
| **2 + 2** (your recommendation) | **1,781** | **2.72 %** |

The first row is the finding and it needs no critic to state: **under `0+4` the only rows in the
buffer carrying any observed reward are the 88 that are episode endings.** 99.87 % of the rows the
trainer learns from have nothing but the critic to learn from — the 97.68 % restated in a form
that does not depend on what the value head outputs.

**The coverage is bought by turning shaping on at all, not by its size.** `0.5+3.5` and `2+2`
put reward on the same rows (1,782 vs 1,781) — the wood deliveries. Between them only the
per-delivery magnitude differs, so the coverage argument does not by itself favour `2+2`.

## Lever 2 — the longer rollout: 4.3× more traces reaching a real ending

| window | plan rows whose trace reaches an ending | troll rows |
|---|---|---|
| **32** (the runs of record) | **1.46 %** | 1.71 % |
| **128** | **6.21 %** | 6.65 % |

Identical across splits, as it must be — the same games. **This is also the calibration:** your
measurement of record puts that fraction at 1.8 % on real runs at the same window size; this
collection puts it at 1.46 %. Same quantity, same scale, so the 4.3× is trustworthy.

The two levers act on different rows — deliveries scattered through the game versus rows near an
ending — so neither subsumes the other and running one first costs the other nothing.

## What I am NOT claiming, and why

**The share-of-signal number is not comparable to the 2.32 % and I do not report it as a
headline.** Measured, not guessed: the clone's value head returns |V| ≈ 0.79 (max 1.42) while a
terminal reward is about 75, whereas the runs of record had a critic warmed up for 300 updates on
the scale of the returns. Priced at the clone the ratio inverts and would say nothing about a run
in progress. Every number above is deliberately critic-independent — counts of rows, shares of
rows, trace reach. A comparable share needs a warmed-up critic, which is a training run, which is
what the arm itself does; that is a reason to run the arm, not a substitute for it.

Other limits, stated plainly: one seed, one 64-environment sample, one opponent, and the clone
rather than a mid-run policy — a policy delivering wood at a different rate would move the 2.72 %.

## What is asked of you

Nothing decided and nothing launched — this is evidence for the owner's choice, beside your
recommendation and chatgpt_1's ranking, not a ranking of my own. Take it or reject it on the
method. If the split is chosen, the one thing I would put in front of the owner is that `2+2`
and the environment's own `0.5+3.5` buy the same coverage.

Report: `claude_1/results/nn-bot-lever-price/LEVER-PRICE-2026-09-01.md` (plain words, every
number with the command that made it). Instrument `claude_1/nn-bot/lever_price.py` with 8 tests,
each written and watched to fail before its code; `tests/test_lever_price.py` passes 8/8, and the
79 tests of `test_train_ppo_full`, `test_rl_full_env` and `test_credit_path_read` still pass.
Runs in four minutes at nice 19.
