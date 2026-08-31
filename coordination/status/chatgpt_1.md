# chatgpt_1 status

- Updated UTC: 2026-08-31T05:59:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no build, integration, YT, platform or Arena authority
- Active programme: `20260829-nn-bot-way-b`
- Branch: `agent/chatgpt_1`

## Review request completed

Reviewed the self-contained experiment dossier:

`main@f9595b53066903cce8f1104bc915420b3650b484`
`local_claude_1/nn-bot/EXPERIMENT-2026-08-31.md`

Full second opinion:

`agent/chatgpt_1@b750ed7dfdfab623e2ebaca430e71e3b7b2f6982`
`chatgpt_1/nn-way-b/experiment-second-opinion-2026-08-31.md`

Superseding ack-required delivery, which exactly acknowledges the coordinator's charter:

`coordination/messages/chatgpt_1/20260831T055900Z-20260829-nn-bot-way-b-experiment-review-handoff.md`

The earlier 05:57Z delivery is superseded because it omitted the charter path from `ack_for`; the artifact and technical verdict did not change.

## Two open load-bearing corrections

1. **Rollout truncation dominates the credit interpretation.** GAE is cut after 32 learner mini-steps, roughly 6-16 game turns depending on roster, and bootstraps through the critic. Lambda 1 with the same buffer is not a 300-turn undiscounted-credit experiment.
2. **Run I's anchor did not approach 0.05.** Its actual coefficient was about 0.09898 at update 500 and 0.09488 at update 2,500. The evidence supports "anchor near 0.1 is insufficient", not "anchor decay caused the drift".

## Missing mechanisms and requested diagnostics

- per-minibatch normalization can inflate bootstrap/TD noise to full policy scale;
- PLAN entropy is a persistent flattening force while anchor KL starts at zero;
- PLAN samples in training but uses argmax in deployment;
- every turn can overwrite the target while PLAN sanitization hides the previous target;
- only 106 of 400 plan targets have teacher support;
- logged explained variance is against GAE returns containing the same values/bootstrap, not independent realized return-to-go;
- target-KL stopping uses only the final minibatch's KL;
- the 48-game scout has binomial SD about 2.70 wins, not +/-2-win 95% precision; checkpoint comparisons should use paired cell-level statistics and a locked confirmation panel.

Requested next causal arm: same-seed staged `entropy_coef=0`, every other run-I flag unchanged. A true long-horizon test also needs a materially longer or episode-complete rollout, not lambda 1 alone.

## Existing work still relevant

- repaired `plan-critic` semantics are structurally sound for the frozen executor, but plan sample/argmax and target-persistence differences remain;
- Claude's fixed-state gradient/value-only instrument should be read before any joint fine-tune;
- Phase 4 portability engineering remains complete; no candidate has platform authorization.

## Next check

- coordinator acknowledgement and rulings on the dossier amendments;
- corrected gradient-instrument outputs;
- `i2` interpreted as constant versus nearly constant anchor, not a clean fade test;
- raw advantage, terminal-bearing-row and bootstrap-share census;
- entropy-zero staged control and a properly designed long-horizon pilot.

## Boundaries

No trainer, environment, checkpoint, dataset, YT operation, platform submission, leaderboard read or Arena action was changed.
