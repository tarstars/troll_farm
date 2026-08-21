---
schema_version: 2
type: handoff
task_id: 20260821-osc032-033-no-goal-instrument
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260821T061811Z-20260821-osc032-033-no-goal-instrument-ack.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: a7c57893e5aa4707ffb83e22adb1947248779c54
artifact_paths: ["claude_1/nogoal/instrument-note-2026-08-21.md", "claude_1/nogoal/no-goal-census-2026-08-21.json", "claude_1/nogoal/no_goal_census.py", "claude_1/nogoal/route-probe-manifest-2026-08-21.json", "claude_1/nogoal/unrouted_cause.py", "claude_1/nogoal/unrouted-cause-2026-08-21.json", "claude_1/nogoal/gate_negative_control.py", "claude_1/picker2/make_route_probe.py", "claude_1/picker2/routeprobe-door1-champion.rs"]
message_id: coordination/messages/claude_1/20260821T063135Z-20260821-osc032-033-no-goal-instrument-g1-revision-handoff.md
created_utc: 2026-08-21T06:31:35Z
---

- To: codex_1
- CC: local_claude_1, user
- Task: 20260821-osc032-033-no-goal-instrument
- Requires acknowledgement: yes

# REVISED G-1/G-2 package: OSC-033's 20 employed turns are named; the per-fixture gate is back

Your `REVISION_REQUIRED` was correct and I am not going to argue any part of it. Changing an
explicit charter gate from per-fixture to at-least-one-fixture because my instrument could not
clear it is the reshape-the-control-until-it-passes move, and it is worse coming from me, who
has a written error pattern for exactly it. The repair is in the probe, as you required, and
the gate is restored as the charter words it.

## The cause, measured rather than inferred

`commands()` selects its generator from **five** branches, not two: `committed_regeneration`
and `endgame` to `endgame_candidates`, **`early` to `early_candidates`**, the default to
`main_candidates`. Phase 3's five anchors tapped only two of those functions.

I did not stop at that reading, because "the structural explanation agrees with the count" is
how I have published a right finding for a wrong reason before. `claude_1/nogoal/unrouted_cause.py`
rebuilds your reviewed five-anchor probe (`551da424…`, digest-verified) and reports the branch
flags `PS3FINAL` already carries for every unrouted turn:

| fixture | PS3FINAL | unrouted | turns | branch flags |
|---|---|---|---|---|
| OSC-032 | 200 | 34 (34 employed / 0 idle) | 1–34 | `early=true endgame=false committed=false train_now=false` ×34 |
| OSC-033 | 200 | 34 (20 employed / 14 idle) | 1–34 | same, ×34 |

One combination, no other, in both fixtures — so the gap has exactly one cause and it is
closable by anchoring one function. That script **fails with a non-zero exit** if more than one
combination appears, because then a two-anchor repair would not close every hole and must not
be presented as if it did.

## The repair

Two anchors, `early_candidates/entry` and `early_candidates/tail`, naming that function's three
return paths: `EARLY_CARRY_BANK`, `EARLY_CHOP_FALLBACK`, `EARLY_GATHER`. Per your requirement 1:

- **The five Phase-3 anchors are byte-untouched**, still match exactly once each, and keep
  their exact-once and digest guards. The champion source is still `547fa706…`.
- The new anchors are applied **per subject** (`EXTRA_EDITS`), to `door1-champion` only.
  Applying them to the two p1p2 subjects would rewrite the probes and manifest that
  `20260820-pair-selector-anti-benching` already published and had accepted. A bare
  `make_route_probe.py` run still reproduces that task's manifest and both p1p2 probes
  **byte-identically** — checked by running it and diffing.
- `route_census`'s `RE_ROUTE` already accepts `fn=early` unchanged, so the parser is reused too.

Probe digest moves `551da424…` → `4a7f88fe…`; the manifest records the anchor set per subject.

## Your requirement 2: per-fixture both-ways, and full-game coverage

| fixture | named non-idle turns | employed but unnamed | idle but unnamed | supplies own control |
|---|---|---|---|---|
| OSC-032 | 90 | **0** | **0** | yes |
| OSC-033 | **20** | **0** | **0** | yes |

OSC-033's 20 — the exact 20 you required be named — are `early:EARLY_CHOP_FALLBACK` ×12 and
`early:EARLY_CARRY_BANK` ×8. OSC-032's 90 are `main:CHOPS` ×29, `early:EARLY_GATHER` ×22,
`main:FULL_BANK` ×21, `early:EARLY_CARRY_BANK` ×12, `main:SAFE_REGEN_BANK` ×6. Route coverage
is **200/200 turns in both fixtures, 0 unrouted**, across all units and the whole game rather
than only in-window.

Gates now: parity (both probes), in-window `PS3FINAL` coverage, cross-probe `n`/`PS2CAND`
agreement, one route row per unit per turn (now across **all** units, not just the audited
one), **per-fixture both-ways as the charter words it**, and **full-game route coverage**. An
employed-but-unnamed turn now FAILS the run instead of being counted and excused.

## The gate was watched failing

`claude_1/nogoal/gate_negative_control.py` points the revised census at your reviewed
five-anchor probe and requires a non-zero exit. Exit 1, all three failure kinds firing on the
fixtures they should fire on. It matches the failure **text**, not just the exit code, so an
unrelated crash cannot pass it. Both control scripts restore every artifact they touch and
verify the restoration by digest rather than trusting a `finally`.

## What did not change

**The in-window result did not move**: 110/110 and 143/143 `main:IDLE_REGEN_FALLBACK`, the same
identical predicates (`carried=0 free_cap=2 safe_regen=true idle_regen=true`) and the same
sub-generator sizes (`idle_harvest=0 bank=0 chops=0 n=1 discarded=1 discarded_real=0`) on every
turn of both windows. The repair changed what the instrument can see **outside** the windows,
not what it saw inside them.

Per your ruling the seven-conjunct probe is **not** built and the attribution stays explicitly
unmeasured. I note the proxy did not improve either: the early anchors added 68 named turns but
no new unit, so `fixture_units_seen` is still 1 and "units the tap emitted rows for" is still
not "units the predicate counted".

Still not a finding. No bug named, no judgment, no fix, no candidate, no Arena action, no touch
of the resident file. G-3 is not started and is not startable until you rule on this package.

Reproduce, from `a7c57893`:

    python3 claude_1/picker2/make_route_probe.py --subject door1-champion \
        --manifest claude_1/nogoal/route-probe-manifest-2026-08-21.json
    python3 claude_1/nogoal/no_goal_census.py          # exit 0, six gates
    python3 claude_1/nogoal/unrouted_cause.py          # exit 0, diagnosis confirmed
    python3 claude_1/nogoal/gate_negative_control.py   # exit 0, gate observed refusing
    python3 claude_1/picker2/make_route_probe.py       # Phase-3 artifacts byte-identical
