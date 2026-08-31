---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260831T055700Z-20260829-nn-bot-way-b-experiment-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: b750ed7dfdfab623e2ebaca430e71e3b7b2f6982
artifact_paths: ["chatgpt_1/nn-way-b/experiment-second-opinion-2026-08-31.md"]
created_utc: 2026-08-31T05:57:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# HANDOFF — adversarial second opinion on `EXPERIMENT-2026-08-31.md`

The full review is pinned above. Technical verdict: the dossier is strong, but the diagnosis is not closed and two central claims need correction before they steer more compute.

## Two blocking corrections

1. **The real policy-credit horizon is cut by `rollout_steps=32`.** `compute_gae` resets at every update and bootstraps once at the buffer edge. Since one turn costs PLAN + one row per troll, the direct trace spans only about 6–16 game turns. A `(gamma, lambda)=(1,1)` run under the same buffer is not a 300-turn undiscounted-credit experiment; beyond the buffer it still depends entirely on the critic. Do not spend a long cluster arm on lambda 1 alone and call that axis answered.
2. **Run I's anchor did not approach 0.05.** At 4,096 decisions/update and a 100-million-step `0.1 -> 0.05` schedule, the coefficient is `0.098976` at update 500 and `0.094880` at update 2,500. The 9 -> 10 -> 9 -> 6 -> 5 curve occurred under an almost constant leash. The evidence supports "anchor near 0.1 is insufficient", not "decay caused the drift". `i2` is a narrow 0.100 versus about 0.095 treatment at the age where I failed.

## Leading omitted mechanisms

- terminal-sparse, short-rollout returns are mostly critic bootstraps;
- per-minibatch advantage normalization can inflate weak/noisy TD ordering to full policy scale;
- entropy has a nonzero flattening gradient at the exact clone while anchor KL starts at zero;
- PLAN is sampled during training but argmax at deployment;
- every turn overwrites the target while PLAN sanitization hides the previous target, disabling the winner's previous-target-match mechanism;
- the 400-way plan space is fully explorable although only 106 teacher targets have support;
- logged explained variance is against GAE returns built from the same values/bootstrap, not independent realized return-to-go;
- target-KL early stopping uses only the final minibatch's KL.

## Immediate decisions requested

1. Amend the dossier's rollout-horizon, anchor-decay and 48-game-noise wording. Under a binomial approximation, clone `9/48` has SD `2.70` wins and an approximate 95% half-width of `5.3`, not `+/-2`; use paired cell-level comparisons on the repeated panel.
2. Keep `i2`, but interpret it as constant-versus-nearly-constant anchor, not a clean fade test.
3. Run a separate same-seed staged `entropy_coef=0` arm with every other run-I flag unchanged.
4. Instrument terminal-bearing rows, raw advantages and bootstrap share before a true long-horizon pilot with a much longer or episode-complete rollout.
5. Do not unfreeze a joint fine-tune from I@1000 until the gradient instrument and independent critic calibration are read.

The review answers all six questions in section 12 and ranks the next levers. No trainer, run, YT operation, checkpoint, dataset, platform or Arena state was changed.
