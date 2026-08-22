---
schema_version: 2
type: handoff
task_id: 20260815-oscillation-deep-dive
from: claude_1
to: ["local_claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/claude_1/20260815T152700Z-20260815-oscillation-deep-dive-d2-phase1-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 423b87a1be7d06c6c8fe4f29b35650fb5a896a3a
artifact_paths: ["claude_1/viewer/build_viewer.py", "claude_1/viewer/README.md", "claude_1/viewer/out"]
created_utc: 2026-08-15T15:27:00Z
---

- To: local_claude_1
- CC: user, codex_1
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: yes

# handoff: D2 Phase 1 viewer DELIVERED — 34 pages, all acceptance items met, one limit you must know before the first session

## For the owner, in plain terms

You can now look at every recorded oscillation as a picture instead of as a file of numbers. Open
one page, press the arrow keys, and watch the troll pace back and forth turn by turn.

The page is careful about one thing above all: **it separates what we recorded from what we
guessed.** What the bot *ordered* is printed exactly as it was recorded. Where the troll *ended
up* is our inference — an order to walk somewhere does not guarantee arriving — so it is drawn as
a dashed, hollow circle and labelled as an assumption. Solid things are facts; dashed things are
guesses.

**One honest caveat before you use it in a session:** no web browser is installed on the machine I
work on, so I could not open these pages and look at them. Everything about their *structure* is
machine-checked. How they actually *look* is not. Someone should open one page once before the
first live session.

## Delivered

Artifact `423b87a1be7d06c6c8fe4f29b35650fb5a896a3a` on `agent/claude_1`, pushed and verified on
the remote before this message. Open `claude_1/viewer/out/index.html`.

- 34 self-contained pages + index. **No server, no external script, stylesheet, font or image** —
  works from `file://` and offline.
- Keyboard step-through: `←` `→` per turn, `Home`/`End` to the ends.
- **Generated through the verifying loader.** `load_library(verify=True)` fails closed on any
  digest, file-set, count, schema or enumeration mismatch; if the library is not intact, no page
  is produced at all.
- Display-only. It captures nothing — you record rulings separately, as ruled.

## Acceptance, checked against the generated output rather than intent

| your criterion | verified |
|---|---|
| renders all 34 subject-correct situations | 34 pages |
| the 13 with `+`/`~` terrain | 13 pages draw iron/water classes |
| the 2 single-cell stalls | OSC-032, OSC-033 render as *"one-cell STALL — the unit does not move at all"* |
| a known 2-cycle is visible | 32 pages render as an n-cell cycle with the paced squares highlighted |
| owner can drive it unaided | keys + on-screen buttons + legend on every page — **structurally present, not visually confirmed; see the limit** |

Frame indices are consistent with frame counts on all 34 pages, and every page is self-contained
(no external reference).

## The three honesty rules, and why the design refuses to guess harder

`codex_1`'s V1 was right and this build is shaped by it. A command is an **order**, not a landing:
`engine.rs::next_cell` returns the target only when `d <= speed`, so a distant `MOVE` lands
part-way, and simultaneous resolution against the opponent can move it again — and the opponent's
commands are *not in this library*.

So: verbatim command and its parsed target are **ground truth** (solid); the one inferred value is
**hollow and dashed** and never called realized; every side panel is stamped `at entry` and never
advanced.

**The generator deliberately does NOT compute a predicted landing.** Doing so would mean a
BFS/speed mirror of `engine.rs` inside a viewer, and a mirror that disagrees with the authority is
worse than no mirror — that is a lesson this project already paid for. The single inference drawn
is *"at the target of the most recent MOVE"*, stated as an assumption on every page.

## Guards — 11 cases, and two of them caught real defects in my own code

`python3 claude_1/viewer/build_viewer.py --self-test` → **11 cases, all pass, every check observed
rejecting.** Two were not ceremony:

1. **The inference-marking check was inert.** It matched the required class against the whole tag
   — and `data-role="derived-position"` itself contains the substring `derived`, so an element
   with no marking satisfied it. It passed for the wrong reason. Only the negative control
   exposed it; it now reads the `class` attribute specifically. **A check I wrote to enforce the
   most important rule on the page could not fail**, and I would not have known without running
   the control.
2. **The opponent was drawn hollow** — the same treatment as inference — while the legend said
   "solid red circle". Ground truth and assumption looked alike, which is the exact confusion
   these rules exist to prevent. Fixed, and now machine-checked: `.own` must be hollow+dashed,
   `.opp` must not be dashed and must not be hollow.

## The limit, stated plainly

**The visual layer is unverified by execution.** No browser on this host; nothing screenshotted.
The checks prove the marks carry their structural role and class, and that ground-truth and
inferred marks are styled differently. They do **not** prove the page looks right — a stylesheet
that is well-formed but visually confusing passes every case above.

**Ask before the first session:** someone opens one 2-cycle page (OSC-006 is the cleanest: 9
turns, k=4) and one stall (OSC-033, 143 turns, every one a WAIT) and confirms the dashed circle
reads as provisional at a glance. If it does not, that is a CSS fix, not a rebuild.

## Boundaries

Frozen library read-only and verified untouched; `rust/` and `cgauto/` untouched;
`yamo_orchard_live.rs` byte-exact `fff6669b0bc0b15b…`. No Arena action. Phase 2 (packet overlay,
blind mode) **not built and not scaffolded** — gated on P-1 and a separate go.

`codex_1` reviews; I authored it, so nothing closes on my say-so.

## Next

Back to **P-1 rollout step 2** (single-state capture for mode, candidate generation and
exclusions) unless you re-order. Still open from my D3 ack and not blocking: the packet
cardinality question (which turns of a 7–195-turn window get packets), and §16's blind adjudicator
naming the unreachable `chatgpt_1` where your ruling makes the owner judge.
