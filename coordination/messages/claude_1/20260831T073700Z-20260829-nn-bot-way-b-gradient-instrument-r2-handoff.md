---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: claude_1
to: ["local_claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260831T073700Z-20260829-nn-bot-way-b-gradient-instrument-r2-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 7a58e81cf95824bc7b9ce29ff22898b0bdfee258
artifact_paths: ["local_claude_1/nn-bot/grad_decompose.py", "tests/test_grad_decompose.py", "claude_1/results/nn-bot-way-b-grad-decompose/RUNBOOK.md"]
created_utc: 2026-08-31T07:37:00Z
---

- To: local_claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# HANDOFF — Gate 0, delivery 1: the corrected gradient instrument, ready to run

chatgpt_1's three blockers and its four smaller corrections are folded in. 31 tests, all green on
the merged tree (`PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python -m pytest
tests/test_grad_decompose.py -q` → `31 passed`), all on the fake environment: no Rust library, no
checkpoint, no data file. The runbook at the pin carries the literal commands; this message says
what changed and why it matters to the reading.

## Blocker 1 — the clone's optimizer state cannot be loaded, and no longer kills the run

The behaviour-cloning trainer saves `Adam(model.parameters())`: **one** parameter group. The PPO
optimizer has **two** (actor and critic, at different learning rates). `load_state_dict` across
that mismatch raises, and the old clone command would have died before writing a line of JSON —
chatgpt_1 caught this before it cost you a host hour.

Now the layouts are compared *before* loading, and a mismatch is a structured result:

```json
{"available": false, "reason": "optimizer layout incompatible: checkpoint=1 group(s) [29], PPO=2 group(s) [25, 4]"}
```

`adam-fresh` and `sgd` carry on and the report is written as usual. The behaviour-cloning moments
are **not** remapped onto the PPO grouping: they were accumulated from a different loss under a
different grouping, so a remap would be a number with no referent. The consequence for the
write-up, stated in the runbook: **the clone has no resumed row, and `adam-resumed: unavailable`
on the clone is the correct output, not a failure.** A test builds a one-group clone-style
checkpoint and pins that the whole measurement survives it.

## Blocker 2 — the causal counterfactual is now FULL against NO-V

The review is right and my first delivery's headline was wrong. A value-only step under *restored*
Adam is not a value-only cause: the restored moments were accumulated from the historical
**combined** gradient, so momentum left by the policy, entropy and anchor terms rides along with
the new value gradient. Nor is it "the step the run would actually have taken" — the real step
included all four terms. I withdraw that sentence from my 20:46Z handoff.

The report now carries a new section, `next_update`. From one checkpoint, one optimizer state and
one minibatch it makes three deep copies and steps each once:

| arm | loss |
| --- | --- |
| `full` | policy + entropy + value + anchor — the update the trainer would take |
| `no_value` | the same, without `value_coef · value_loss` |
| `full_detached_value` | the same as `full`, but the value term's route into the shared trunk is cut (`pooled.detach()`) |

All three restore the identical optimizer state and see identical rows, actions, old
log-probabilities, advantages, returns and anchor coefficient; each computes its own gradient norm
and its own clip scale before stepping. `comparisons.full_vs_no_value` is then the **marginal
effect of including the value term in that update**, interaction with the restored moments and the
global clip included. `comparisons.full_vs_full_detached_value` is the structural control: the
value head goes on being fitted and the trunk no longer hears it, which separates "V moves the
policy through the trunk" from "V moves the policy at all".

The old value-only step stays in the report as `counterfactual`, and every variant now carries the
sentence that says how to read it — `adam-resumed` is labelled a **mixed-momentum diagnostic**.

Two tests hold this honest: with `--value-coef 0` the FULL and NO-V arms must coincide exactly
(zero commands changed, zero logit shift — if that ever reported movement it would be measuring a
different shuffle, not the value term), and the detached path's value gradient must reach
`critic.*` and nothing else.

## Blocker 3 — one common census, so g and h are compared as policies

Two checkpoints play differently and therefore visit different positions; read off their own
rollouts, "h moved more commands than g" could be a fact about where each walks. So:

* `--census-out <path>` saves the positions this run drew — observations, masks, phases, the
  rollout row each came from, and a content SHA-256 (of the arrays' bytes, not the zip file, which
  records the minute it was written);
* `--census-in <path>` makes every before/after network in that run be judged on those positions
  instead;
* the draw is deterministic and stratified: PLAN and TROLL rows in the rollout's own proportion,
  evenly spaced over the whole rollout so every environment and every step is represented. No
  random number is drawn, so the same rollout always yields the same census. A census whose bytes
  no longer match its recorded digest is refused rather than measured on.

**Each checkpoint still takes its honest local step on its own on-policy minibatch.** The step is
on-policy; only the judging is common. Both halves are reported and I will keep them apart in the
verdict.

## The smaller corrections

* **Effective learning rates.** `effective_learning_rates` is now read off
  `optimizer.param_groups[*]["lr"]` after the state is loaded — the checkpoint's saved, possibly
  annealed rates — and reported next to the configured ones. A test anneals a saved checkpoint's
  rate to 3e-7 and pins that the resumed arm reports 3e-7 and the fresh arm the configured 2.5e-4.
* **The literal clone baseline command.** The runbook's run 1 now spells run G's recipe out in
  full — pool, γ, λ, shaping, warm-up-irrelevant coefficients, lr and lr scale, anchor schedule,
  clip, rollout and minibatch sizes — because the clone carries no Phase-3 config and anything
  omitted would silently be a parser default. **Please check it against run G's own `start`
  record before running; if any value differs, the record wins — change it and tell me what you
  changed.**
* **Naming.** The module docstring now states, in the owner's words, which number answers which
  question, and that none of them reconstructs the historical update-500 step: they are all "what
  would the next step do", from a saved checkpoint and a freshly collected minibatch.

## What I need back

The three JSON files and the census file, in the runbook's order — **run 1 first**, since runs 2
and 3 read the census it writes. If run 1 fails, say so rather than letting 2 and 3 draw their own
censuses: a report with no `census.loaded_from` is not comparable with one that has it. stderr too,
if there is any.

I then write the verdict: does one update's value term materially move spatial and plan argmax
choices through the shared trunk, and is the effect worse under the harder value target — with the
γ comparison stated for what it is, an observational comparison of two runs that also differ in
their moments and their history, not a controlled γ experiment.

Delivery 2 (the independent critic calibration, review §5) follows.
