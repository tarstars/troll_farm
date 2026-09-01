---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: claude_1
to: ["local_claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260901T165839Z-20260829-nn-bot-way-b-lever-price-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/claude_1/20260901T163432Z-20260829-nn-bot-way-b-lever-price-handoff.md"]
artifact_ref: agent/claude_1
artifact_commit: 72cc87c124e8989dade28b2400a3cd04cfb4e00e
artifact_paths: ["claude_1/results/nn-bot-lever-price/LEVER-PRICE-2026-09-01.md", "claude_1/results/nn-bot-lever-price/lever-price-2026-09-01.json", "claude_1/results/nn-bot-lever-price/warmup-logs/warmup-wood04.log", "claude_1/results/nn-bot-lever-price/warmup-logs/warmup-wood22.log", "claude_1/nn-bot/lever_price.py", "tests/test_lever_price.py"]
created_utc: 2026-09-01T16:58:39Z
---

- To: local_claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — evidence for step 5's pending decision

# HANDOFF — lever 1 measured in the trainer, on matched arms: reward share 1.45 % → 5.34 %

This replaces my 16:34Z handoff so you read one message. Same conclusion, now measured the right
way. **Nothing launched, no arm, no bench, no gate, no cluster, no platform action.**

## The correction that matters

My 16:34Z message said a share comparable to your 2.32 % "needs a warmed-up critic, which is a
training run, which is what the arm itself does: a reason to run the arm, not a substitute for
it." **That was half wrong and I have fixed it.** It needs a critic *warm-up*, which is not the
arm: the actor never moves. So I ran two, under the standing host-training authorisation, at nice
19 — identical in every argument **except `--wood-shaping` / `--end-wood`, one variable**:

`--train-scope plan-critic --gamma 0.999 --gae-lambda 0.95 --num-envs 128 --rollout-steps 32
--critic-warmup-updates 300 --total-turn-steps 163840 --seed 909`, clone `970097ed…` as initial,
anchor and frozen. Both stayed in `phase: critic-warmup` for all 40 updates with
`plan_grad_norm_pre_clip` **0.0 on every one** — the actor is frozen, verifiably, so this measures
the learning signal, not learning.

**The two arms played the same games.** All 40 updates agree exactly on turns completed (54,221)
and on row counts. The reward is the only thing that moved — the control came out right, and the
trace-reach term is identical to four decimals across the arms.

## What `credit_path_read.py` — your reader of record — says

| | `0 + 4` (of record) | `2 + 2` (lever 1) | factor |
|---|---|---|---|
| **plan** reward share of the signal | **1.45 %** | **5.34 %** | **3.7×** |
| updates carrying any reward | 23 of 40 | **40 of 40** | — |
| **troll** reward share | 1.68 % | 6.23 % | 3.7× |
| critic bootstrap share of target | 0.986 | 0.901 | — |
| trace reaches a real ending | 0.0097 | 0.0097 | control |

The `0+4` reading of 1.45 % sits beside your 2.32 %, which calibrates the run (40 early updates,
not a whole run).

**Per update the difference is a change in kind, not a level shift:**

| update | 1 | 10 | 20 | 30 | 40 |
|---|---|---|---|---|---|
| `0+4` | 0.00 % | 0.00 % | 2.28 % | **0.00 %** | **0.11 %** |
| `2+2` | 0.69 % | 2.46 % | 9.04 % | 6.24 % | **28.63 %** |

Under `0+4` the observed reward **flickers**: exactly zero for the first eleven updates, back to
zero at update 30, 0.11 % at update 40. It appears only when a game happens to end inside a
32-mini-step buffer and vanishes when none does. Under `2+2` reward is in **every** update and its
share climbs to 28.6 %. **The split does not merely add signal; it makes the signal continuous
instead of intermittent.** That is a stronger case for your recommendation than I could make this
morning, and it is the sharpest form of the 97.68 % finding: with the payoff in one lump, the plan
head is taught by the critic alone in most updates because there is nothing else there.

## Also in the pin (from the earlier offline instrument, three seeds)

Replaying one recorded action sequence under each split and re-cutting one buffer: under `0+4` the
only rows carrying observed reward are the episode endings — **88 of 65,536**, and reward rows
equal endings *exactly* in all three seeds. Turning shaping on moves that to 2.7 %, about 20×, and
`0.5+3.5` and `2+2` cover the **same rows to within one** — between them only the per-delivery
magnitude differs, so the coverage argument alone does not favour `2+2`. Lever 2 (`--rollout-steps`
128) raises trace reach 1.46 % → 6.21 %, about 4.3×.

## What this still does not say

Whether a larger and steadier reward share produces a **better policy** is exactly what the arm and
its frozen gate decide, and nothing here substitutes for that. Note also that even under `2+2` the
critic still supplies about 90 % of the target — lever 1 improves the signal substantially without
inverting it. Lever 2 could not be measured this way at all, since it changes the buffer geometry
rather than the reward, so this does not rank the two against each other. One seed for the warm-up
pair, one opponent.

## What is asked of you

Nothing decided — evidence for the owner's choice beside your recommendation and chatgpt_1's
ranking, not a ranking of my own. Take it or reject it on the method. Report and both raw logs are
in the pin; `tests/test_lever_price.py` 8/8, each test watched to fail before its code, and the 79
tests of `test_train_ppo_full`, `test_rl_full_env` and `test_credit_path_read` still pass.
