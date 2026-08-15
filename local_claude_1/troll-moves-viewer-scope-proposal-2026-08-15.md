# Troll moves viewer — scope proposal (deliverable D2 of the oscillation deep-dive)

- Status: PROPOSAL — claude_1 feasibility response received (FEASIBLE); awaiting owner scope agreement
- Author: local_claude_1
- Date: 2026-08-15
- v2 2026-08-15: revised per codex_1 review (oscillation-d2-d3-review-2026-08-15.md) and
  claude_1 P-2 feasibility response; v1 findings corrected in place.
- Parent task: `coordination/tasks/20260815-oscillation-deep-dive.md` (D2; serves the D4 adjudication sessions)

## 1. Purpose and users

A picture tool. It takes one frozen "oscillation situation" (a saved snapshot of a game moment
where a troll got stuck — usually pacing between two squares, in four cases standing still, see
the `kind` field below) and shows it on screen: the map, both players' trolls, and what
what the own side was commanded to do turn by turn. The owner and the agents will look at it
together in joint sessions and decide what the trolls SHOULD have done (deliverable D4). It must
also work alone, asynchronously: an agent opens a situation, studies it, writes an analysis.
The owner must be able to open and drive it without any agent present.

## 2. Data contract (what it reads)

**Phase 1 input — the frozen situation library.** IMPORTANT: the correct library is
`claude_1/banana-restoration-r2/oscillation-library-98628e98/library/` (34 situations, 46
episodes) — the tree the loader `oscillation_library.py` opens by default. The task file cites
`oscillation-library/` "33 situations / 47 episodes", but that tree's own index says WRONG
SUBJECT — PARENT LINEAGE, must not be cited. The viewer targets the correct tree; the "33" in
the task text should be corrected to 34. The viewer loads through `load_library()` so the
freeze hashes are verified (it refuses silently modified data).

Fields actually present in a situation file (verified on OSC-001; semantics confirmed by
claude_1's P-2 measurement of the whole library):

- `static_map_rows` — the map as ASCII rows. Full alphabet, CONFIRMED: `#` wall, `.` open
  ground, `0` our shack, `1` enemy shack (the digit is the player index), `+` iron deposit,
  `~` water. `+` and `~` occur in 13 of the 34 situations (OSC-003, 004, 011, 014, 015, 016,
  017, 018, 020, 021, 025, 026, 030; OSC-026 has both). CAUTION: the loader's `walkable` set
  contains only `.` — it excludes shacks AND iron AND water — so the renderer must draw each
  character class explicitly and must NOT shade "everything not walkable" as wall (that would
  mis-render those 13 maps). Any unknown character must fail loudly, not default to wall.
- `world_state_at_entry` — snapshot at the turn the episode starts, an ENTRY snapshot only
  (see hard limit 2 below): `units` (both players; each unit is a 14-number row, CONFIRMED as
  `[id, player, x, y, movement_speed, carry_capacity, harvest_power, chop_power]` followed by
  6 carried-item counts in the fixed order PLUM, LEMON, APPLE, BANANA, IRON, WOOD; `player` 0 =
  ours, 1 = opponent), `inventories.own` / `inventories.opponent` (6 numbers, same item order),
  `plants` (e.g. `["BANANA", 2, 2, 4, 6, 0, 43]`), `turn`. Also `initial_world_state` (turn 1).
- `window` — the episode: `turn_start`, `turn_end`, `unit` (the stuck troll), `cells` (ONE or
  TWO squares: two = the pacing pair in 32 of 34 situations; OSC-032 and OSC-033 have a single
  cell — a stall, not pacing; OSC-033 is 143 consecutive WAITs), and `commands` — one entry per
  turn with the OWN side's full command line (e.g. `"MOVE 0 5 2;WAIT"`).
- `kind` — top-level field: `D1_EPISODE` (pacing, 30 of 34) or `P4_STALL` (standing still,
  4 of 34). A stall and an oscillation are different phenomena; the kind MUST be displayed on
  every page so sessions never infer it from the picture.
- `classification` — mechanism label, blocker analysis (which peer blocks, its stats, how
  still it stood), a small ASCII `geometry_excerpt` with legend, `mechanism_evidence` prose.
- `unresolved`, `provenance`, `multiplicity`, `detectors` — shown as side text.

**Three hard limits of this data (they shape the whole tool):**

1. **No per-turn snapshots, and commands are goals, not realized states.** Only two full world
   states exist (turn 1 and episode entry). Within the window we have the own side's command
   lines — contiguous for every turn in all 34 (claude_1 verified) — but a `MOVE id x y` names
   a GOAL: where the troll actually landed depends on the referee's step rules, its speed, and
   simultaneous collisions with the opponent, whose within-window moves are not recorded at
   all. So own positions after entry are an INFERENCE, and collisions are unknowable. The
   viewer therefore renders three distinct classes: the verbatim command (ground truth), the
   command's target square (ground truth), and a command-derived predicted position (inference,
   visibly marked as inferred — e.g. hollow/dashed troll icon). It must never label derived
   positions "exact" or "realized". Opponent trolls are drawn frozen at their entry positions,
   with the uncertainty carried in the picture itself, not only a caption.
2. **Everything stateful is an entry snapshot, not current-turn state.** Inventories, plants
   (growth/removal), opponent positions, and unit cargo/stats are frozen at episode entry and
   cannot be advanced honestly from own commands alone. Every such panel and marker is labeled
   "at entry" while stepping through turns.
3. **The bot's goals are not in the data.** Each file says so itself under `unresolved`. So
   "goals per turn" in Phase 1 means: the observed command and the target it names. True
   goals, candidates and scores arrive only with the Decision Packet (Phase 2).

**Phase 2 input — Decision Packet overlay (separate, later).** The Decision Packet
(`chatgpt_1/decision-packet-spec-2026-08-10.md`, frozen contract; D1 of this task) is a JSON
record explaining one full turn: every candidate action considered, with intent, target, score
and score terms; rejected candidates with reason codes; pair selection; resolver rewrites with
branch (`DIRECT`/`DETOUR`/`WAIT_NO_LANDING`/`ALREADY_AT_LANDING`). The viewer should accept an
optional directory of per-turn packet JSONs alongside a situation and overlay them. The spec's
section 16 "blind view" matters: for fair adjudication the viewer needs a toggle that HIDES
scores and the bot's choice until the human has committed a judgment. Timing — SYNCED TO THE OWNER RULING 2026-08-15 (per codex_1 re-review): Phase-1
display-only LIVE sessions are authorized and may run without blind mode, since Phase 1
contains no Decision Packet material to be biased by; the blind/reveal control must exist
before PHASE-2 (packet-overlay) adjudication begins — under the top-down template the
human commits L1–L4 before step 5 opens the code's view, which is the same discipline
enforced socially until the control exists. It hides only Decision Packet material;
Phase 1 still shows the board and the frozen evidence.

## 3. Proposed form

**Recommended: a single self-contained HTML file per situation**, generated by one small
Python script (`render_situation.py <OSC-ID>` → `OSC-001.html`), plus an index page linking all
34. No server, no build step, no dependencies beyond the browser; keyboard step-through (arrow
keys = one turn forward/back, Home/End = window start/end). All data is embedded in the file,
so a situation page can be sent to the owner as one attachment and works offline.

Rationale: the project's no-churn culture and maintenance cost. A generated static file has no
runtime to keep alive, no package versions to rot, nothing to install on the owner's machine,
and it cannot accidentally touch the frozen library (it only reads via the verifying loader).
The prior art (`cgauto/make_oscillation_exercise_pdf.py`, output
`docs/reports/2026-08-09-oscillation-exercise.pdf`) is prose-only — it draws no board — so
this is the project's first board renderer; starting minimal is the right risk posture.

**Alternative (not recommended now):** a richer local web app (small Python server, live
loading of any situation or packet, richer interaction). More capable for Phase 2 volume, but
it adds a running process, a port, and upkeep — revisit only if the static form proves cramped
during real sessions.

## 4. Features

**Phase 1 (must-have):**
- Board grid from `static_map_rows`, drawn per character class: wall, open ground, our shack,
  enemy shack, iron, water — plus plants (species + growth) at entry. Legend data-driven; any
  unknown map character fails loudly rather than defaulting to wall.
- Header on every page: the situation `kind` in plain words ("pacing between two squares" /
  "standing still — stall") and the number of window cells.
- Both sides' trolls with unit IDs and stats/cargo on hover/click, all labeled "at entry"; own
  side vs opponent clearly distinct; the stuck troll and the blocking troll specially marked.
- Step forward/back through the window turns; turn counter always visible.
- Per-troll command line shown VERBATIM for the turn (ground truth), with the command's target
  square marked, and the inferred position drawn in a visibly-inferred style (hollow/dashed)
  plus a faded trail — never at the same visual confidence as recorded data (hard limit 1).
- Inventories (own and opponent, the 6 counters) as a side panel, labeled "at entry" (hard
  limit 2) — they do not update while stepping.
- Window highlighted: the one or two `window.cells` tinted; a timeline bar showing window
  start/end inside the whole game. Single-cell situations render as a stall (one highlighted
  square + turn counter), not as a degenerate pair.
- Side panel: mechanism, blocker analysis, `mechanism_evidence`, `unresolved` items,
  provenance — so a session never needs the raw JSON open.
- Honest uncertainty: opponent trolls frozen at entry with the uncertainty encoded in the
  picture itself (distinct icon style), not only a caption. (All 34 situations are FULL — there
  is no PARTIAL completeness case to degrade for; the earlier "OSC-033 is PARTIAL" claim was
  wrong. OSC-033's specialness is being a 143-turn WAIT stall, handled by the kind/stall
  rendering above.)

**Phase 2 (Decision Packet overlay, only after D1 exists):** per troll per turn, the candidate
list with scores and score terms; rejected candidates with reason codes; resolver rewrites
(original vs rewritten command, branch, detour reasoning); blind/reveal toggle per section 16
of the packet spec.

**Non-goals:** no live game connection; no modification of any bot (the sacred compact file
stays byte-exact); no replay of arbitrary games in Phase 1 (only the frozen library); no
judgment recorded by the tool itself unless the owner asks for it (open question below); no
attempt to guess opponent moves the data does not contain.

## 5. Acceptance checks

1. The generator runs over the full correct-subject library and produces all 34 pages plus the
   index with zero errors; the loader's integrity check passes first. The 13 situations with
   iron/water terrain render those squares as iron/water, not as walls.
2. On a named known case (e.g. OSC-001, map m110, window turns 6–200), the 2-square pacing
   between cells (6,2) and (5,2) is visibly obvious within three key presses.
3. The owner can open a page and step through unaided (no agent, no terminal), on plain-word
   labels only — every code (M1, D-1, etc.) explained in a legend.
4. The rendered positions at the ENTRY turn exactly match `world_state_at_entry` (the only turn
   where exactness is claimable). For later turns, every inferred own-troll position is drawn
   in the inferred style and is consistent with the verbatim command shown beside it — an
   internal-consistency check only, NOT evidence that the inferred positions match what
   happened in the game (they cannot be verified; see hard limit 1).
5. OSC-032 and OSC-033 (single-cell, `P4_STALL`) render as stalls with the kind stated in the
   header — no crash, no fabricated pacing pair; OSC-033 shows its 143 consecutive WAITs.

## 6. Open questions

**For the owner:** (a) Session format — screen-share over one page, or pages sent ahead for
solo review then discussed? (b) Should the viewer include an annotation box so your D4 ruling
is typed inline and saved to a separate file (never into the frozen library)? (c) Is
per-situation single-file HTML acceptable, or do you want one combined page? (d) Confirm the
subject correction: sessions run over the 34-situation correct-subject library, not the
33-situation parent tree the task text cites (claude_1 confirmed 34 independently by
measurement). (e) Adjudication sessions must not begin before the hide-the-scores ("blind")
control exists — otherwise early judgments are unblinded by construction. Confirm this ordering.

**For claude_1 — RESOLVED by the P-2 response:** (a) FEASIBLE as scoped (static form; 3,184
window turns total across the library, trivially small for embedded pages). (b) Unit-row and
map-character meanings confirmed by measurement; folded into section 2 above. (c) SUPERSEDED —
the question assumed exact reconstruction was possible; it is not. Commands cover every window
turn contiguously in all 34 (verified), but a command is a goal, not a landing; derived
positions stay inference (hard limit 1). (d) Still open: whether the Phase 2 overlay changes
any Phase 1 layout decision worth making now (e.g. reserving the side panel).
