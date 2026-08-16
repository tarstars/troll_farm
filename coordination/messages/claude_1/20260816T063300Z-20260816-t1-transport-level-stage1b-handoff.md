---
schema_version: 2
type: handoff
task_id: 20260816-t1-transport-level
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260816T063300Z-20260816-t1-transport-level-stage1b-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 6d0d7b2169074b70947a0d3e091fa0f6e389affe
artifact_paths: ["claude_1/t1/fixture_harness.py", "claude_1/t1/baseline-resident-2026-08-16.json"]
created_utc: 2026-08-16T06:33:00Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260816-t1-transport-level
- Requires acknowledgement: yes

# handoff: T-1 stage 1b — P4 clause wired and CLOSED. All 34 now carry a live detector clause.

## For the owner, in plain terms

Yesterday I handed you a test that worked on 30 of the 34 recorded situations and told you plainly
that the other four — the "standing still" cases — were only half-checked. That half is now built.
All 34 are properly covered, and the test still fails on all 34, which remains the correct answer
because no fix exists yet.

## Delivered

Artifact `6d0d7b2169074b70947a0d3e091fa0f6e389affe` on `agent/claude_1`, pushed and
remote-verified. **Still 0 FIXED / 34** — unchanged, and now for the right reason on every row.

The four stalls previously read `silent=True` because nothing was checking them. They now read:

```
NOT FIXED OSC-031  P4_STALL  turns 11-200   P4  silent=False progress=False
NOT FIXED OSC-032  P4_STALL  turns 91-200   P4  silent=False progress=False
NOT FIXED OSC-033  P4_STALL  turns 58-200   P4  silent=False progress=False
NOT FIXED OSC-034  P4_STALL  turns 6-99     P4  silent=False progress=False
```

## The design decision worth reviewing

**I wired the panel's own `fuzz_panel.eval_p4` rather than writing a "stalled" predicate here.**
A second definition would let the word mean one thing to the gate and another to this harness —
and this project has already paid for a figure changing meaning at a boundary more than once.

Two things I checked rather than assumed before reusing it:

- `eval_p4(tr_c, tr_p, ...)` accepts `tr_p` **for signature parity and never consults it**
  (`fuzz_panel:1831-1838`, and the inherited-exemption clause is explicitly removed). So passing
  the candidate trace twice is faithful, not a fudge to make the call typecheck.
- `post_ct_state(ref)` supplies the world *after* the final command set resolves, which the
  post-C_T rule needs to judge turn T at all. Omitting it would silently drop the last turn's
  obligation.

Which clause applies is decided by the situation's own `kind`: **D-1 for `D1_EPISODE`, P4 for
`P4_STALL`.** The result records `detector_clause` per row so nobody has to infer which check ran.

## The control, because I have shipped this exact bug before

`check_p4_fidelity()` requires **every frozen stall to reproduce as a P4 violation overlapping its
window**, and the baseline run aborts if one does not.

That control exists specifically because **the D-1 clause shipped wired-but-inert two days ago**
and I did not catch it by reading the code — only the negative control found it. Wiring a new
clause without the same guard would have been repeating the mistake while writing the report about
it. The self-test now asserts the P4 clause is observed *firing* (violations-in-window ≥ 1), not
merely not-crashing.

Self-test **7 → 10 cases**, all passing.

## What this does and does not establish

**Does:** every one of the 34 situations now has a detector clause that fires on the unmodified
resident and reproduces its frozen finding, plus a progress clause. The instrument is ready to
judge a candidate.

**Does not:** say anything about T-1's design, which does not exist yet. And the grading rule
stays as frozen — FIXED needs detector silence **and** progress. A candidate that converts an
oscillation into a polite standstill will read `silent=True, progress=False` and score
**NOT FIXED**, which is the outcome I most expect to have to report honestly.

## Boundaries

Resident byte-exact `98628e98…`; `rust/`, `cgauto/` and the frozen library untouched. No Arena
action, no banana code, no D1-B change. Prediction registry still unread; I will not tune against
it.

## Next

Stage 2 — `Target::None` visibility (`:643-646`) — then idle-yield and swap. `codex_1` reviews the
instrument first per your ordering; it is now feature-complete for grading, and it has twice
demonstrated it can be wrong in a way that flatters the result.
