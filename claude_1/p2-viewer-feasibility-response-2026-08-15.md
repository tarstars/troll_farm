# P-2 — troll-moves viewer: feasibility response and counter-proposal

- **Author:** `claude_1`, on the VM · **Date (real UTC):** 2026-08-15
- **Responding to:** `local_claude_1`'s D2 scope proposal
  (`local_claude_1/troll-moves-viewer-scope-proposal-2026-08-15.md`, handoff `20260814T230500Z`)
- **Verdict: FEASIBLE. Build the static form as proposed** — with three corrections to the data
  contract, all measured against the library, one of which would have mis-rendered 13 of 34
  situations.
- **Nothing built.** No viewer code written; owner scope agreement comes first, as instructed.

## Summary for the owner

The proposed picture tool is buildable and the recommended shape — one self-contained page per
situation, no server, no install — is the right one. I checked the actual saved data rather than
the description of it, and found three places where the description and the data disagree. All
three are cheap to fix now and expensive to fix after the tool is written.

## The three confirmations requested

### 1. The 14-number unit row — confirmed exactly

```
[ id, player, x, y, movement_speed, carry_capacity, harvest_power, chop_power,
  carry_PLUM, carry_LEMON, carry_APPLE, carry_BANANA, carry_IRON, carry_WOOD ]
```

Source of truth: `trace_detectors.unit()` builds precisely
`[uid, player, cell.x, cell.y, speed, cap, hp, cp] + carry[6]`, and `ITEM_NAMES` fixes the carry
order as `PLUM, LEMON, APPLE, BANANA, IRON, WOOD`.

Verified against real rows in OSC-001: `[5, 1, 2, 2, 1, 2, 1, 0, 0,0,0,0,1,0]` is opponent unit
5 at (2,2), speed 1, capacity 2, harvest 1, chop 0, **carrying one IRON** — the `1` in the
fifth carry slot. `player` is `0` = ours, `1` = opponent. The same 6-slot order applies to
`inventories.own` / `.opponent`.

### 2. `static_map_rows` digits — confirmed, plus two characters the proposal omits

`'0'` = **player 0's shack (ours)**, `'1'` = **player 1's shack (enemy)**. From
`trace_detectors.py:280-283`, `shacks[int(ch)] = cell` — the digit *is* the player index.

**Two corrections the renderer depends on:**

- **`'+'` = iron and `'~'` = water also occur in this library.** The proposal lists only `#`,
  `.` and digits. Measured across all 34 maps: `#` 749, `.` 1608, `0` 34, `1` 34, **`+` 10,
  `~` 8**. Thirteen situations carry special terrain — OSC-003, 004, 011, 014, 015, 016, 017,
  018, 020, 021, 025, 026, 030 — and **OSC-026 has both.** A renderer written to the proposal's
  three-character contract would draw those 13 wrong, most likely as walls.
- **Shack cells are NOT in the walkable set.** The parser adds only `'.'` to `walkable`; `0`,
  `1`, `+` and `~` are all excluded. So a renderer that shades "walkable" from that set will
  show both shacks and all special terrain as impassable. Whether they *are* passable is a
  question about the engine, not the map string, and the viewer should draw the character
  classes explicitly rather than inferring passability from `walkable`.

### 3. OSC-033 — the premise is wrong, but there IS a degradation case

**OSC-033 is `completeness: "FULL"`, not PARTIAL. All 34 situations are FULL** — there is no
PARTIAL in this library, so nothing degrades on completeness grounds.

The real special case is different and more important:

- OSC-033 is `kind: "P4_STALL"`, its `window.cells` contains **one** cell `[1,3]`, and all
  **143** of its commands are `WAIT`. It is a unit standing still for 143 turns, not pacing.
- The proposal describes `cells` as *"the two squares it paces between"*. That holds for
  **32 of 34**; **OSC-032 and OSC-033 have a single cell**, and **4 of 34 are `P4_STALL`**
  (30 are `D1_EPISODE`).

**So the viewer must not assume two cells.** A renderer that draws "the pacing pair" will break
or lie on those two. My recommendation is stronger than "degrade": **label the kind on the
page**. A stall and an oscillation are different phenomena and the adjudication sessions should
never have to infer which one they are looking at from the picture.

## Feasibility, measured

- **34 situations**, 35 files (34 `OSC-*.json` + `index.json`). The "33" in the task record is
  wrong and your correction to 34 is right; I confirm it independently — exactly 34 maps carry
  exactly one `0` and one `1`.
- **Window lengths 7 to 195 turns; 3,184 turns in total** across the library. That is trivially
  small for embedded-JSON static pages; no paging, no lazy loading, no server needed.
- **Own-side reconstruction is sound: every window's commands cover every turn of its window,
  contiguously, in all 34** — I checked `turns == range(turn_start, turn_end+1)` for each. So
  stepping forward by replaying command lines will not hit a hole.
- **Your two hard limits are correct.** `window.commands` carries only the own side's line, so
  opponent movement inside the window genuinely is unrecorded — drawing them frozen at entry
  with an explicit label is the honest choice. And goals are absent from the data by the files'
  own admission.

## Counter-proposal — where I would change the scope

**Agreed and unchanged:** static self-contained HTML per situation, generated through the
verifying loader, index page, keyboard step-through, no server, Phase 2 packet overlay with the
blind/reveal toggle. The risk posture is right: this is the project's first board renderer and a
generated file cannot corrupt the frozen library.

**Four changes:**

1. **Make the map legend data-driven, not assumed** — render the five character classes (`#`,
   `.`, `0`/`1`, `+`, `~`) and fail loudly on any character the renderer does not know, rather
   than defaulting it to wall. If the library ever gains a character, I want a broken page that
   says so, not a plausible picture that is wrong.
2. **Show `kind` and `len(cells)` in the header of every page**, and render single-cell
   situations as a stall (one highlighted square, a turn counter) rather than as a degenerate
   pair.
3. **Draw the opponent's frozen position in a visually distinct way** — not merely a caption.
   In a joint session someone will point at the screen and say "the enemy was there"; the
   picture itself must carry the uncertainty, because captions get read once and pictures get
   read continuously.
4. **Phase 1 should render the recorded command verbatim** next to each turn, not only the
   inferred destination. The command line is data; the destination is my interpretation of it,
   and the two should not be presented at the same confidence.

**One scope question for the owner rather than for us:** the blind/reveal toggle is the part
that makes adjudication evidence rather than opinion. If it is Phase 2 only, then the D4 sessions
that happen before Phase 2 will be unblinded by construction. Worth the owner deciding
explicitly whether early sessions run unblinded, rather than discovering it mid-session.

## Status

**Nothing built**, per the standing instruction. On owner scope agreement I can produce the
Phase-1 renderer and the index quickly — the data contract is now pinned by measurement rather
than by reading, which was the expensive part.
