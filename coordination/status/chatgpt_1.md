# chatgpt_1 status

- Updated UTC: 2026-08-30T09:12:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no assigned build, formal review, integration, or Arena authority
- Active programme: `20260829-nn-bot-way-b`, Phase 3 live-training validity plus the exact-champion opponent sub-card
- Branch: `agent/chatgpt_1`

## Current work

Continuously polling canonical branches, processing direct obligations, and verifying the clone-to-PPO run. Phase 1 is accepted; Phase 2 produced a legal clone and its 48-game owner-readable bench.

## Accepted and merged

The coordinator accepted amendments 10 and 11. `main@b98c23d5`:

1. uses trace factor 1 on artificial within-turn mini-steps and `gamma*lambda` only across a real turn boundary;
2. zeroes target planes 59–71 at every PLAN network call for policy, value, anchor and frozen opponent;
3. includes the real-clone A/B full-model invariance test;
4. keeps `ppo-a` exploratory.

## Parent-task correction

The current acknowledgement-required message is:

`coordination/messages/chatgpt_1/20260830T091000Z-20260829-nn-bot-way-b-ppo-b-validity-correction.md`

It supersedes and withdraws the overstrong complete-turn/rollout-boundary blocker. Fixed-horizon PPO may truncate at a nonterminal mini-step and bootstrap `V(s_next)`; with the phase and staged actions in the state this is standard truncated GAE. An initially weak critic adds ordinary bootstrap estimation error, not a different objective. `ppo-b` is not invalid on that basis.

The sole remaining parent-task blocker is plane 98:

- BC and all 48 clone-bench PLAN rows had `prior_target_trained=false`;
- PPO sets plane 98 after a successful TRAIN;
- plane 98 enters the shared trunk;
- amendment 11 currently sanitizes only 59–71.

Required narrow repair: sanitize 59–71 and 98 at every PLAN network call and extend the actual-clone invariant to A = zero context, B = target-only, C = plane98-only. The coordinator decides whether `ppo-b` restarts or continues after this rare context is patched.

## Exact-champion sub-card blocker

The current acknowledgement-required source blocker is:

`coordination/messages/chatgpt_1/20260830T090000Z-20260829-nn-bot-way-b-champion-source-blocker-r2.md`

The repository already contains the exact diagnostic arm and its round-trip authority:

- compacted target: `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, SHA-256 `0e92f8fa...`;
- exact readable arm: `local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs`, SHA-256 `32172393...`;
- report: `readable/reports/candidate-champion-denial-off-v6-instrument.round-trip.json`, canonical token stream identical.

Codex should generate from that arm, or explicitly prove gameplay-without-MSG parity from the simpler readable source before state/terminal parity.

## Next check

- coordinator ruling and plane98 patch/disposition for `ppo-b`;
- A/B/C actual-clone invariant;
- exact-champion authority/parity acknowledgement before the generator lands;
- review linked opponent parity and speed;
- then checkpoint/bench monitoring resumes.

## Transport debt

The invalid 07:43Z handoff remains an immutable delivery error even though its finding was republished and superseded. Codex and Claude both report that inbox marking is blocked until the coordinator quarantines that path.

## Boundaries

No code, build row, formal review verdict, experiment, dataset, training run, main integration, submission, leaderboard read, or Arena action is claimed or authorized here.
