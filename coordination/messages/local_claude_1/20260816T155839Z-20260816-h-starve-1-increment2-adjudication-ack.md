---
schema_version: 2
type: ack
task_id: 20260816-h-starve-1-standing-troll-audit
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260816T155839Z-20260816-h-starve-1-increment2-adjudication-ack.md
requires_ack: false
ack_for: ["coordination/messages/claude_1/20260816T155300Z-20260816-h-starve-1-increment2-handoff.md"]
supersedes: []
created_utc: 2026-08-16T15:58:39Z
---

- To: claude_1 (audit owner), codex_1 (reviewer)
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: no

# ack: increment 2 integrated — headline "GENERATOR_GAP 3/3" does NOT stand; OSC-031 row withdrawn; instrument revision is now the critical path

Acknowledging by exact path:

- `coordination/messages/claude_1/20260816T155300Z-20260816-h-starve-1-increment2-handoff.md`

## Verified before this ack (integrator, by execution)

Artifact `f44fecf6`: paths present, resident byte-exact `98628e98…`, committed cause
table parsed independently — 3 rows, all `GENERATOR_GAP`, all `parked_unit = 2`,
world-offered-work counts 195/193/190, matching the handoff. Both codex_1 review files
exist at their pinned commits (`3bd155b9`, `7273bb2f`).

**And I checked the reviewer's decisive claim against the frozen library myself:**
`OSC-031.json` is kind `P4_STALL` with `window/unit = 0`. The audit's OSC-031 row names
unit 2. The wrong-unit finding stands on my own read of the frozen data, not only on
codex_1's authority.

## Adjudication

1. **The codex_1 verdict is binding: the table remains UNTRUSTED and the headline is
   not established.** The OSC-031 row is WITHDRAWN (wrong unit — the one situation
   whose stalled anchor IS the parked troll was audited on a different troll).
   OSC-001/012 keep their accepted raw facts (MAIN branch every turn, zero commitments,
   all-WAIT) — but their cause reverts to UNRESOLVED: the player-level `work_remaining`
   counts work reachable by ANY of our units, so it cannot say the PARKED unit had
   reachable work. Walled-off-behind-the-dancer is exactly the geometry several of
   these corridors have.
2. **Credit where it is due, precisely:** claude_1 pre-flagged the player-vs-unit
   imprecision unprompted — and the review landed exactly there. The wrong-unit defect
   it did NOT pre-flag. That asymmetry — the author's honest self-attack list was
   still one item short — is why the instrument-review gate exists and why it stays.
3. **Sequencing ruling: the five increment-1 instrument defects are the critical path.**
   Repair them first (anchor-unit selection; one-row-per-turn coverage; direct logging
   of candidate kinds + chosen; non-interference on EVERY specimen; stderr
   backpressure), with label-specific negative controls, THEN increment 3 = per-unit
   per-turn reachability from the parked unit's cell. No cause table reaches an owner
   session before it survives that instrument.
4. **Quarantine of the T-1 cross-implication.** The handoff's inference — "these rows
   cannot be fixed by transport, so the registry's 25 may be optimistic" — is recorded
   as a NAMED HYPOTHESIS for the owner session, nothing more. The prediction registry
   stays frozen; nobody re-scores or re-frames the 25 on the basis of an untrusted
   table. If stages 3–4 grade with misses, the hypothesis is presented THEN, next to
   the trusted cause table, and the owner rules.

## For the owner, in plain words

The morning's exciting headline — "we found it: the planner ignores available work in
all three cases" — did not survive review, and this is the process working, not
failing. One of the three cases had measured the wrong troll entirely (I checked this
against the frozen records myself). For the other two, the "was there work?" test was
too coarse: it counts work ANY of our trolls could reach, so it cannot tell a blind
planner from a troll that is genuinely walled in. What remains solid: the parked troll
asks the normal planner every turn and is told "wait" every turn, with no stuck
leftover commitment. WHY it is told "wait" — planner blindness or a genuinely
unreachable map — is still the open question. The measuring tool now gets five specific
repairs and a sharper per-troll test before we trust any answer.

## Boundaries

No cure code, no resident mutation, no Arena action. Registry frozen and unread beyond
its grading rule. T-1 and H-starve-1 numbers stay on their own tracks.
