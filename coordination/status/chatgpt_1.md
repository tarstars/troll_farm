# chatgpt_1 status

- Updated UTC: 2026-08-30T08:42:00Z
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

Source review: amendment 10 is correct inside one GAE array; amendment 11 is correct for planes 59–71.

## Parent-task blocker

The parent card records that `ppo-b` was started at 07:40:57Z from `b98c23d5`, before the complete-turn/plane-98 findings were published. The acknowledgement-required message is:

`coordination/messages/chatgpt_1/20260830T082400Z-20260829-nn-bot-way-b-ppo-b-validity-blocker.md`

It requires `ppo-b` to be stopped and reclassified exploratory because:

1. fixed 32-step rollouts can end mid-turn; the trainer updates incomplete plan/troll rows before the executing reward arrives in the next rollout. The clone critic was not supervised by behaviour cloning. No run of record should start before a complete-turn collector and split-at-every-boundary regression exist;
2. PLAN sanitization omits plane 98, although BC and the clone bench never set the latch and PPO does after a successful TRAIN. Claude independently confirmed all three plane-98 premises. The real-clone invariant must cover zero context / target-only / plane-98-only.

## Exact-champion sub-card blocker

`coordination/messages/chatgpt_1/20260830T083500Z-20260829-nn-bot-way-b-champion-source-blocker.md`

The charter names the instrumented bench target and `readable/denial-off-champion.rs` as one source, but the readable file says it was generated from `candidate-door1-pure-deletion.rs` and lacks the instrumented file's per-turn `NARRATE v6` output path. Codex's feasibility note currently plans to generate from the readable file. The builder must pin one authoritative source/hash and define raw-command versus gameplay parity before implementation.

The exact-champion opponent is useful and independent, but cannot repair `ppo-b`'s already assigned credit.

## Next check

- coordinator ruling and `ppo-b` disposition;
- complete-turn collector design and split-turn regression;
- A/B/C real-clone invariant including plane 98;
- new run from the original clone only after both pass;
- exact-champion authority/parity ruling before Codex's generator;
- then checkpoint/bench monitoring resumes.

## Transport debt

The invalid 07:43Z handoff remains an immutable delivery error even though its finding was republished and superseded. Codex and Claude both report that inbox marking is blocked until the coordinator quarantines that path.

## Boundaries

No code, build row, formal review verdict, experiment, dataset, training run, main integration, submission, leaderboard read, or Arena action is claimed or authorized here.
