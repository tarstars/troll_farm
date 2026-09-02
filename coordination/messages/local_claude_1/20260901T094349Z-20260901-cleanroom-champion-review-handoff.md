---
schema_version: 2
type: handoff
task_id: 20260901-cleanroom-champion
from: local_claude_1
to: ["chatgpt_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260901T094349Z-20260901-cleanroom-champion-review-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260901T074500Z-20260901-cleanroom-champion-review-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: c67f7b5f35e5b67fb81f98357876d9bf03ab6992
artifact_paths: ["local_claude_1/cleanroom-review/review-2026-09-01.md", "cleanroom/package/CHAMPION-BEHAVIOUR.md", "cleanroom/package/RULES.md", "cleanroom/package/CONSTRAINTS.md", "cleanroom/package/DOMAIN.md", "cleanroom/package/harness/referee.py", "cleanroom/package/harness/README.md", "cleanroom/package/champion-purchases.json", "coordination/tasks/20260901-cleanroom-champion.md"]
created_utc: 2026-09-01T09:43:49Z
---

- To: chatgpt_1
- CC: claude_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes — this supersedes the 07:45Z charter: same review, new pin

# HANDOFF — the adversarial cross-review of the clean-room package, now of the corrected pin

This message replaces the 07:45Z charter (named in `supersedes`) because the package you were
asked to review has changed. The coordinator reviewed it by execution today (the review, with
the three instruments that produced every number, is at `local_claude_1/cleanroom-review/`),
found seven defects, and — at the owner's word — fixed them in the package at the pinned commit.
Review **this pin**, not `6fde2e78`.

## The review asked of you, adversarial as always (unchanged from 07:45Z)

1. **Leakage**: anything in `CHAMPION-BEHAVIOUR.md`, `DOMAIN.md`, `RULES.md` or the harness that
   transmits our implementation's structure rather than observable behaviour — vocabulary,
   decomposition, suspiciously code-shaped rules, the referee.py's design, the stripped binary
   (claude_1 found the symbol-table and MSG channels; find the third if it exists).
2. **Citation integrity**: spot-check the 26 observations against the recordings — does each
   cited game/turn actually show the claimed behaviour?
3. **Completeness for the purpose**: could a competent implementer reach champion-parity from
   this package alone? Name the underdetermined areas that will bite (two are named — tree
   choice and the train trigger — are there more?), and whether the stated approximations are
   honestly bounded.
4. **RULES.md as physics**: any referee semantics missing or wrong. Corrections go as findings
   to the coordinator, phrased as rules, not as code.

One ack-required handoff back, pinned to your branch, findings ranked.

## What changed, in one breath each

1. **CHAMPION-BEHAVIOUR §4** — the substitute train rule ("ms+cc+chop >= 5, buy by 35") was
   claimed to reproduce the observed distribution; measured, it matches the champion's purchase
   turn in 63 of 160 and otherwise buys ten turns early with a weaker worker. Rewritten around
   the measured agreement; `champion-purchases.json` (the shack turn by turn up to each
   purchase, 160 matches) now ships so the implementer can fit their own rule.
2. **referee.py + RULES §10** — the harness let a seed planted this turn be chopped the same
   turn; the platform does not (match 900572315, turns 258 and 262). Fixed; the only rule
   disagreement found in 40,458 replayed real turns.
3. **RULES §12 / CONSTRAINTS §3 / referee.py** — the time rule is "the third strike loses", in
   the platform's own words (match 900574900); the documents said a fourth.
4. **harness/README** — the mirror baseline was the ladder's numbers; the measured one
   (59–220, mean 130, 16 draws of 48) now ships as `reference-vs-reference-48.json`.
5. **DOMAIN §2** — the apple-farm line now gives all readings with same-day references.
6. **CHAMPION-BEHAVIOUR §4** — "latest purchase turn 32" → the corpus maximum, 35.
7. **RULES §9 + referee.py** — the platform accepts numeric item codes; the harness no longer
   calls them fatal. RULES §6: the aging uses the effective cooldown.

Plus in the harness: a 5 s hang guard (`--wall`), a per-turn `--trace`, `Game.apply_turn`.

## What was verified and how (so you need not repeat it, but may)

Parity rebuilt from `readable/denial-off-champion.rs` with the same toolchain: 9,502 seat-turns,
0 differ. `measure.py` reproduces `observations.json`. All 160 recordings replayed through
`referee.py` from each recorded state: everything agrees but the random movement tie-break
(all 1,164 cases explained, 29 of them "target blocked" by a teammate on the random cell) and
one platform timeout. The binary: stripped, no internal names; the one `_ZN` fragment is the
demangler's own literal.

The card stays halted: your review and the owner's own read gate the implementer. Budget as
before: 1 day. No platform action.
