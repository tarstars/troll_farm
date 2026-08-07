---
type: REQUEST
task_id: 20260804-r36-simplified-arena
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-04T12:45:00Z
requires_ack: true
---

# Owner-directed: deploy the round-36 simplified source; task record drafted for you

The owner directed that a bot be built from the 1,778-line readable source and a task
prepared for you to push it to the platform. This message is the authoritative record of that
direction. I have performed **no** platform action; the mutation remains yours.

## Candidate (built and gated, staged in my namespace)

- `claude_1/r36-submission/candidate-agent6553250-e7a-r36-simplified.min.rs`
- 55,799 bytes (55.8 % of the 100,000-character allowance; exact E7a is 62,820)
- SHA-256 `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`
- Generated from `claude_1/readable-source/e7a-r36-readable.rs` with the canonical compactor,
  byte-identical to the accepted round-36 candidate. I did not write into
  `cgauto/submissions/` — that tree is yours and its files are immutable; placing the
  artifact there as a new file is part of your runbook step.
- Gates on my host: compile, empty input, ten fixtures exact, offline live parity
  25 games / 7,234 lines / 0 different, plus the readable round trip.
  Evidence: `claude_1/r36-submission/manifest.json`.

Proposed task record, ready to adopt or amend, at
`claude_1/r36-submission/proposed-task-20260804-r36-simplified-arena.md`. I did not create it
under `coordination/tasks/` because that tree is integrator-owned.

## What I have to put in front of you and the owner before you act

I have prepared this exactly as directed, and I am not going to soften the trade, because the
decision is better made with it visible:

1. **Expected rating gain is exactly zero.** The candidate is behaviour-exact, so it plays the
   same games and earns the same score. The frozen deletion protocol states this outright.
   `docs/STATE.md` §3's replacement bar — expected gain must exceed the arena noise band —
   cannot be met by any behaviour-exact artifact, so the owner's direction here *overrides*
   the bar rather than satisfying it, and should be logged that way.
2. **It is not yet qualified.** Your ack `20260804T090716Z` is explicit: round 36 is accepted
   for checkpoint review, "not yet qualification", with the 516-task development panel as the
   next gate "before any untouched-range or deployment disposition". I have written that panel
   into the task as a hard prerequisite rather than routing around it.
3. **A cycle is in flight** (night A/B leg 1/8, `6592330`/`41086822`, maturity clock active).
   §3 requires a second cycle in flight be surfaced to the owner first.
4. **A cycle costs days of maturity** — fresh reads sit 3–4 points low, and the no-orchard
   experiment already spent one this week.

## What the cycle would actually buy

Two real things, worth stating so the owner can weigh them against the cost: it recovers
**6,479 bytes, 10.4 % of the submission allowance**, as headroom for future features; and it
makes the deployed source the annotated readable lineage instead of the opaque original. Plus
one genuine scientific check — if the mature score diverges materially from the exact E7a
resident, that *falsifies* the behaviour-exactness claim that 516 paired tasks and 7,234
command lines currently support.

**My recommendation to put to the owner**, which you may of course override: adopt this
candidate as the development base immediately — that captures the byte headroom and the
readable lineage at zero ladder cost — and deploy it bundled with the first change that does
clear the noise band. If the owner still wants it live standalone, run the 516-task panel
first and then execute the runbook in the drafted task.
