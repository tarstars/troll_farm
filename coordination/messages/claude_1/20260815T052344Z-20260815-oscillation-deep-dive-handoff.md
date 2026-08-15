---
schema_version: 2
type: handoff
task_id: 20260815-oscillation-deep-dive
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260815T052344Z-20260815-oscillation-deep-dive-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260814T230500Z-20260815-oscillation-deep-dive-d2-d3-handoff.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: b4ecdfbd55e0419bbeb030d7ecef9ee15da1ad84
artifact_paths: ["claude_1/p2-viewer-feasibility-response-2026-08-15.md"]
created_utc: 2026-08-15T05:23:44Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: yes

# P-2 answered: viewer is FEASIBLE — with three data-contract corrections, one affecting 13 of 34 situations

## For the owner, in plain terms

The picture tool you asked for is buildable, and the proposed shape — one self-contained page per
situation, nothing to install, works offline — is the right one.

I checked the actual saved data rather than the description of it, and the two disagree in three
places. All three are cheap to fix now and expensive after the tool is written. The biggest: the
maps contain **iron and water squares** that the plan does not mention, in **13 of the 34**
situations — a tool built to the plan would have drawn those as walls.

**Nothing is built.** Scope is yours to agree first, as instructed.

## Artifact

`claude_1/p2-viewer-feasibility-response-2026-08-15.md` at `b4ecdfbd`.

## The three confirmations you asked for

**1. The 14-number unit row — confirmed exactly:**
`[id, player, x, y, movement_speed, carry_capacity, harvest_power, chop_power, carry×6]`, carry
order `PLUM, LEMON, APPLE, BANANA, IRON, WOOD`. Source: `trace_detectors.unit()` and
`ITEM_NAMES`; verified on a real row — OSC-001's `[5,1,2,2,1,2,1,0,0,0,0,0,1,0]` is opponent
unit 5 carrying one IRON. `player` 0 = ours, 1 = opponent. Same 6-slot order in `inventories`.

**2. Map digits — confirmed, and two characters are missing from the proposal:**
`'0'` = our shack, `'1'` = enemy shack (`trace_detectors.py:280-283`, `shacks[int(ch)] = cell`).
But measured across all 34 maps: `#` 749, `.` 1608, `0` 34, `1` 34, **`+` 10 (iron), `~` 8
(water)**. Thirteen situations carry special terrain — OSC-003, 004, 011, 014, 015, 016, 017,
018, 020, 021, 025, 026, 030 — and **OSC-026 has both**.

Also load-bearing: **shack and terrain cells are NOT in the `walkable` set** — the parser adds
only `'.'`. A renderer shading walkability from that set will show both shacks and all special
terrain as impassable.

**3. OSC-033 — your premise is wrong, but there is a real special case:**
**OSC-033 is `completeness: "FULL"`. All 34 are FULL**; there is no PARTIAL in this library, so
nothing degrades on completeness grounds.

The genuine case is different: OSC-033 is `kind: "P4_STALL"` with **one** cell in
`window.cells` and **143 consecutive `WAIT` commands** — a unit standing still, not pacing. Your
proposal describes `cells` as "the two squares it paces between", true for 32 of 34;
**OSC-032 and OSC-033 have a single cell**, and **4 of 34 are `P4_STALL`** against 30
`D1_EPISODE`. My recommendation is stronger than "degrade gracefully": **put the kind on the
page**, because an adjudication session should never have to infer from the picture whether it
is looking at a stall or an oscillation.

## Feasibility, measured

- **34 situations** confirmed independently (34 files + `index.json`; exactly 34 maps with one
  `0` and one `1`). Your correction from 33 stands.
- **Windows 7–195 turns, 3,184 turns total** — trivially small for embedded-JSON static pages.
- **Own-side replay is sound:** every window's commands cover every turn contiguously in all 34
  (`turns == range(turn_start, turn_end+1)` checked per situation). No holes to step over.
- **Both of your hard limits are correct**: commands carry only the own side's line, so opponent
  movement inside the window really is unrecorded; and goals really are absent.

## Counter-proposal — four changes

1. **Fail loudly on unknown map characters** rather than defaulting them to wall. A broken page
   that says so beats a plausible picture that is wrong.
2. **Show `kind` and cell count in every page header**; render single-cell situations as stalls.
3. **Draw the opponent's frozen position distinctly, not just captioned.** In a joint session
   someone will point and say "the enemy was there" — the picture must carry the uncertainty,
   because captions are read once and pictures continuously.
4. **Render the recorded command verbatim** beside each turn, not only the inferred destination.
   The command is data; the destination is my interpretation, and they should not be shown at
   equal confidence.

**One question for the owner, not for us:** the blind/reveal toggle is what makes adjudication
evidence rather than opinion. If it is Phase 2 only, every D4 session before Phase 2 is unblinded
by construction. Better decided deliberately than discovered mid-session.

## On your correction

Noted and independently confirmed: the subject-correct tree is
`oscillation-library-98628e98/library/` and **P-1's target set is 34, not 33.** For the record,
this is a known trap in my own notes — the parent-lineage tree has been cited as M3a before, and
that is exactly the error your correction prevents.

Nothing owed back to me on P-2 beyond the owner's scope decision. **I have built nothing.**
