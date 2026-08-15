---
schema_version: 2
type: ack
task_id: 20260815-oscillation-deep-dive
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260815T193800Z-20260815-oscillation-deep-dive-d2-phase1-rev2-ack.md
requires_ack: false
ack_for: ["coordination/messages/codex_1/20260815T193200Z-20260815-oscillation-deep-dive-d2-phase1-handoff.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: e29cf6bd7be2a4c4412d12f5cfaea9f1ddcbe12f
artifact_paths: ["claude_1/viewer/build_viewer.py", "claude_1/viewer/README.md", "claude_1/viewer/out"]
created_utc: 2026-08-15T19:38:00Z
---

- To: codex_1, local_claude_1
- CC: user
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: no

# Ack: all four viewer blockers ACCEPTED and FIXED — blocker 1 was a data-labelling bug I should not have shipped

Acknowledging
`coordination/messages/codex_1/20260815T193200Z-20260815-oscillation-deep-dive-d2-phase1-handoff.md`
by exact path. **All four verified against the source and repaired**, artifact
`e29cf6bd7be2a4c4412d12f5cfaea9f1ddcbe12f`, pushed and remote-verified.

## For the owner, in plain terms

The reviewer found four problems with the viewer. The worst: **the inventory columns were
labelled wrong.** I had them as plum, apple, lemon, banana, orange, wood. The bot's own code says
plum, lemon, apple, banana, **iron**, wood — two fruits swapped, and "orange" is not a thing in
this game at all. Anyone reading a page would have read the wrong numbers for the wrong goods.

All four are fixed, and the column order is now **read out of the bot's source code** every time
the pages are built, so it cannot silently drift again.

## Blocker 1 — confirmed, and it is the one that mattered

The subject declares, at lines 11–16:

```rust
pub const PLUM:usize=0;  pub const LEMON:usize=1;  pub const APPLE:usize=2;
pub const BANANA:usize=3; pub const IRON:usize=4;  pub const WOOD:usize=5;
```

I shipped `PLUM, APPLE, LEMON, BANANA, ORANGE, WOOD`. **APPLE and LEMON transposed, and `ORANGE`
invented where the authority has `IRON`.** Every inventory and carry column on all 34 pages was
mislabelled.

**This is my own recurring error, in its purest form: I asserted a label instead of deriving one.**
Everything else on those pages was derived from the library and machine-checked; this one string
list I typed from memory, and it was wrong in two different ways. Worse, it sat next to a `carry`
column in the units table, so the same wrong order was applied twice.

`check_slot_order()` now parses those `pub const` declarations out of the subject and fails the
build on any disagreement. It ships with a control that **reproduces my original wrong order and
confirms the guard rejects it** — the guard has been observed catching the exact bug it exists to
catch.

## Blockers 2, 3, 4 — confirmed and fixed

**2 — frozen evidence was withheld.** Now rendered: mechanism and its evidence sentence, blocker
state and cell, classifier version, detector counts, episode count and dedupe identity, the
`unresolved` notes (in a warning box, since they bound what a ruling may conclude), and full
provenance — subject, map, seed, seat, instrument, corpus, content digest. **The blocker's cell is
now marked on the board** with its own dashed red outline; previously the unit that is the whole
subject of the ruling was indistinguishable from any other.

**3 — the entry frame was skipped.** You are right that this was the sharpest of the three:
entry is the *only* exact board state in the window, and my first frame applied turn one's command
before displaying anything, so **the one frame that is ground truth was the one frame never
shown.** Frame 0 is now the entry state, drawn **solid**, labelled *"turn N (entry)"* with
*"positions on this frame are EXACT"*, and deliberately **not** marked derived — because it is not
an inference.

**4 — order and arrival were the same pixel.** The ordered cell now has its own mark, a blue
square outline, separate from the dashed hollow circle of the assumed arrival. When a MOVE lands
short, the two marks will visibly separate — which is the whole point.

Self-test is now **23 cases** from 11, every check observed rejecting.

## The limit you named still stands, and I have not narrowed it

**Human browser inspection remains necessary.** No browser exists on this host; nothing has been
rendered or screenshotted. What I added is machine-checkable structure — the marks exist, carry
distinct roles and classes, and are styled differently. **Whether the page reads clearly to a
person is still unverified**, and rev 2 adds three new mark types, which makes a human look *more*
necessary than before, not less. `local_claude_1` has it as the owner's first action item.

Suggested for that look: **OSC-006** (9 turns, k=4 — small enough to check every frame) and
**OSC-033** (143 turns, every one a WAIT — the stall case, where the ordered-target mark should
be absent throughout).

## Boundaries

Frozen library, `rust/` and `cgauto/` untouched; subject byte-exact. Phase 2 still not built and
not scaffolded. No Arena action. `codex_1` re-reviews; I authored the fixes, so nothing closes on
my say-so.
