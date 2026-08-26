---
schema_version: 2
type: update
task_id: 20260825-dance-cure-candidate-1-hold
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T115700Z-20260825-dance-cure-candidate-1-hold-update.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T105100Z-20260825-dance-cure-candidate-1-hold-update.md"]
supersedes: []
created_utc: 2026-08-25T11:57:00Z
---

- To: myself (the queue item)
- CC: local_claude_1, codex_1, user
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes (self-addressed; the card below IS the queue item)

# replacement card — the G-2 grade is delivered and it FAILS; what is left is other agents' to rule, and I hold nothing buildable

This discharges `coordination/messages/claude_1/20260825T105100Z-…-update.md`. Its
`UNBLOCK-SIGNAL:` was the coordinator's G-2 package handoff. It fired at
`local_claude_1/20260825T113500Z` (`agent/local_claude_1@5d51b8c7`), and the grade the card
promised is published at `20260825T115600Z` / `agent/claude_1@22d6b2bb`.

**Every item that card listed "on the record before I see any of it" was run, and each has its
number in the report.** Accepted attribution pipeline unmodified; the v4 branch census (H 253 ·
L 245 · P 42,136 · R 341 · W 108 · N 39,706); holds-followed-by-progress; `R_pos` by the
pre-committed script with **the same function object on both sides** (v3 baseline JSON re-derived
byte-identical under the one-keyword substitution); the read's **own** scope-active share
(146/160, 91.25 %), the panel's 228/240 not transferred; idle-with-work 0.4360 % against 1.5 %;
D-3 0; long-stall 0.0000 % against the champion's 1.3072 % on the identical function; classes
1–7; D-1 rows split by `r=`.

**Result: FAIL on (a) 44.00 % vs 65.00 % and on (b) 4.3122 vs 3.8386. No kill rule fired.** The
finding under the verdict: the hold fires 253 times in 102 of 160 games and in **none** of the 25
D-1 windows — `HOLD_SEEN` 0, `REGRESSIVE_NO_HOLD` 24, `NEITHER` 1.

**The crosswalk I owed is paid, not carried.** 339 agree, 18 `R_pos`-only, **0** `r=R`-only, and
all 18 disagreements sit off the BFS map where the arm's own Manhattan fallback decides — 0
unexplained. The card's promise was that a poor result would be published as a finding rather than
folded into the gate; it came back good, and it is published the same way and folded into nothing.

**What I did NOT convert into a pass**: the fourth kill rule has no population on a ladder read
and is recorded NOT MEASURABLE; long-stall is a labelled proxy for P4; clause (a)'s 95 % interval
[24.40, 65.07] contains the bar and Fisher gives p = 0.1003, which states the read's power and
does not soften the FAIL.

**Nothing buildable is left with me.** G-3 does not start on a failed G-2 by the coordinator's own
policy. The disposition of Candidate 1 — revise, park, retire — and the fate of the reserved
second Arena action are `local_claude_1`'s with the owner; I make no recommendation and propose
myself as builder for nothing. I take no Arena action of any kind.

DEFERRED: **any response to the G-2 grade** — codex_1's assigned fresh-archive execution check and
package-identity verification, and the coordinator's disposition. If either returns a defect in my
grade I rebuild it; if the coordinator orders a revised Candidate 1 or a Candidate 2 build and
names me the builder, that is new work under a new card and not this one.

UNBLOCK-SIGNAL: `codex_1` publishes its execution-check verdict on `agent/claude_1@22d6b2bb`, or
`local_claude_1` publishes a disposition, ruling or revision toward `claude_1` on
`20260825-dance-cure-candidate-1-hold`. Nothing else changes this card. I do not re-issue it
unchanged on a bare wake; its heartbeat is 24 hours.

Write set while held: nothing further under `claude_1/cure1/**` or `claude_1/narrate4/**` — both
are as published and immutable in effect. Resident SHA-256 unchanged at `fff6669b…`.
