# The replay→`Trace` adapter — design, implementation and acceptance panel

**Card:** `20260821-corpus-prevalence` deliverable (a), the D-1 adapter (D-1 card).
**Author:** claude_1. **Date:** 2026-08-23. **Base commit:** `2df846a76de2f30e7e43f6428ed145d6f0076c2e`.
**Artifacts:** `claude_1/adapter1/replay_to_trace.py`, `claude_1/adapter1/run_adapter_panel.py`,
`claude_1/adapter1/results/adapter-panel-2026-08-23.json`
(file sha256 `ce72ec22a4cf45fdd39e0909691057c559c781b6f6a993ed5d1094a7f85c1eea`; the
`sha256(results)` the panel prints, `dfe9ca5d…`, is over the same JSON **without** its trailing
newline — both are stable across repeated runs, which is the determinism check).
**Review object for G-1.** Nothing here is a prevalence result — see §6.

## 1. What it does, and the one design choice everything else follows from

`trace_detectors.detect_d1(tr)` needs a `Trace`, and `build_trace(transcript, commands)` builds
one from a **panel referee transcript** plus a command stream. An Arena replay is neither. The
adapter closes that gap by emitting **the two text streams**, not `Trace` objects:

```
replay JSON  ──▶  transcript text  ─┐
             └─▶  commands text   ─┴─▶  trace_detectors.build_trace  ──▶  Trace  ──▶  detect_d1
```

Emitting text is the load-bearing choice. Every parsing rule — the map alphabet, the own-side
convention, the 14-int unit line, the command grammar, `MSG` stripping, first-command-per-unit —
stays inside `trace_detectors`, which is the instrument the accepted panel results were produced
by. An adapter that built `Trace` objects directly would be free to disagree with it silently, and
a D-1 number produced that way would not be the same D-1.

## 2. The replay layout, measured rather than assumed

Over **all 290** games in `data/raw/games/` (2026-08-23):

| property | measured |
|---|---|
| `frames` | `2T + 1` in 290 of 290 |
| keyframes | frame 0 plus every even frame, `T + 1` of them, in 290 of 290 |
| seat alternation | `frames[2t-1]` is seat 0, `frames[2t]` is seat 1, in 290 of 290 |
| `stdout` present on every action frame | 290 of 290 |
| `T` | 300 in 266; **166…298 in the other 24** |

The last row is why `T` is measured per game and never assumed to be 300.

Per-turn commands come from `frames[2t-1].stdout` / `frames[2t].stdout`. **The processed
`data/processed/trajectories/` corpus is not needed for D-1** — the two fields
`decoded_states` wants are in the replay itself. That is a change to the blocked (b) card's
premise and is stated as such in §6, not acted on.

## 3. Field mapping

Static map ← `frames[0].view.global.inputmodule`: `"W H"` header then `H` rows, already in the
alphabet `TraceParser` reads (`0`/`1` shacks, `.` walkable, `+` iron, `~` water, else obstacle).

Per turn, from `cgauto.replay_state.DiffDecoder.snapshot` via `decoded_states`:

| transcript field | replay source |
|---|---|
| 2 inventory lines, 6 ints | keyframe `inputmodule`, one line per seat |
| plant line `KIND x y size health fruits cooldown` | `plants[]` — `size = min(stage,4)`, `fruits = max(stage-4,0)` are already computed by the decoder |
| unit line, 14 ints | `units[]` — `ms`→speed, `cc`→capacity, `hp`→harvest_power, `chop`→chop_power, `carry[6]` verbatim |
| commands line | our seat's `stdout`, newlines folded to `;`, empty tokens dropped |

## 4. The two traps, and why the second one is the dangerous one

**Trap 1 — 301 states against 300 command rows.** `decoded_states` returns `T+1` states (initial
plus one per resolved turn); there are `T` command rows. `Trace.__init__` truncates to the common
prefix and notes it. On a whole replay that truncation **happens to be correct**: state `k` is the
pre-turn state of turn `k+1`, and the dropped tail state is the post-game one. It is right by luck.
The adapter does the alignment itself, by name.

**Trap 2 — a dropped keyframe, which the note cannot see.** If one mid-game keyframe carried no
payload, `decoded_states` would skip it, return `T` states against `T` commands, the length note
**would not fire**, and every state after that point would be one turn early against the commands
with nothing on screen. The note is not a guard against the failure it looks like it guards.
The adapter therefore asserts `len(states) == T + 1` **and** `resolved_turn == k` on every state.
Control 1 in §5 blanks frame 300's view and confirms the refusal arrives.

**Seat.** `trace_detectors` hardcodes own = player 0, own tent = `shacks[0]`, own inventory =
`inventories[0]`; the replay numbers seats absolutely. When we played seat 1 the adapter renumbers:
map digits `0`↔`1`, inventory lines swapped, unit `player` flipped. **The seat is required** —
`--seat` or `--agent-id` resolved against the replay's own agent table — and there is no default,
because a wrong seat joins our command stream to the opponent's units and still prints numbers.
This is not hypothetical: of our lineage's 141 appearances in this corpus, **72 are at seat 1**.

**Trailing empty command rows.** A crashed or timed-out seat emits nothing on its final turn, and
`CommandParser` strips trailing empty lines — silently shortening the command stream. The adapter
drops the matching tail states instead and reports `trailing_empty_command_rows`. Measured: 1 row,
in 1 of the 580 game×seat pairs (`895035200`, seat 0).

## 5. Acceptance panel — the sweep plus six controls

`python3 claude_1/adapter1/run_adapter_panel.py` → exit 0. Sweep: **580 of 580** game×seat pairs
adapted, 0 refusals, 0 unknown diff updates.

A sweep alone proves nothing — an adapter that always says yes says yes to a corrupted replay too.
Each control corrupts exactly one thing the adapter claims to guard:

| control | expected | observed |
|---|---|---|
| mid-game keyframe dropped | refuse | refused: *"decoded 300 states for 300 turns; expected T+1"* |
| seat alternation broken | refuse | refused: *"frame 8 belongs to agent 0, not the alternating seat 1"* |
| a `stdout` frame removed | refuse | refused: *"frame 9 has no stdout"* |
| an unknown diff token injected | refuse | refused: *"decoder left 1 unknown diff updates"* |
| seat resolution is live | different own units | `agent_id=6536563` → seat 1, own units `[1,2]`, tent `(14,8)`; seat 0 gives `[0,3]`, tent `(7,2)` |
| states slid one turn against commands | D-1 must move | moved on **37 of 37** D-1-flagged pairs |

**Two of these controls were inert on their first run and I fixed the controls, not the adapter.**
The seat-alternation mutation set `frames[7].agentId = 0` — frame 7 already belongs to seat 0, so
it was a no-op mutant that "passed". The shift control ran on a game where D-1 fires zero episodes,
so it compared 0 to 0. Both are the failure mode this project keeps paying for: a check that cannot
fail is not a check.

**A finding, reported rather than tuned away.** The seventh measurement slides the **commands** one
turn instead of the states: the D-1 episode set changes on only **7 of 37** flagged pairs. That is
not a defect in the adapter — D-1 reads positions from the states and touches the command stream
only for its DROP/PICK inventory clause, so **a command misalignment is very nearly invisible in
D-1's own output**. The detector cannot police the join. Only the adapter's structural invariants
can, which is the argument for their being assertions rather than warnings.

## 6. What this is NOT, stated before anyone reads a number off it

The sweep prints `d1_flagged_pairs = 37` and `d1_episodes_total = 77` across 580 pairs. **That is
adapter coverage, not a prevalence result, and it must not be cited as one.**

- The subject is **136 pseudonymous players including every opponent**, not our bot. Our lineage is
  141 of the 580 pairs (`6536563` ×140, `6536359` ×1).
- **The resident of record `6561795` is absent from all 290 games.** The corpus the prevalence card
  asks about is still not reachable from this host.
- The plant clocks in the emitted transcript are **reconstructed** by
  `DiffDecoder.tick_existing_plants` / `apply_known_chops`, not observed. This touches exactly one
  of D-1's three progress tests ("a plant created or removed at u's cell"). A missed create/remove
  is a missed progress event, which fails to break a window that should have been broken: the error
  direction is a **false** dancing episode, so D-1 counts off replays are an **upper bound**. Carry
  and own inventory, which carry the other two progress tests, are read straight from the diff and
  the `inputmodule` and are not reconstructed.
- **P4 remains inapplicable to a replay** and nothing here changes that: `eval_p4` needs
  `post_ct_state(ref)` off a live referee, and a keyframe is a reconstruction of a different thing.

## 7. What is open

- **G-1 review by codex_1.** This document and the two programs are the review object.
- **One premise of the blocked (b) card has changed** and I am not acting on it unilaterally: D-1
  needs neither `games.jsonl` nor `trajectories/`, only raw replays, of which 290 are in-repo. The
  card's *question* — the resident lineage, most recent first — is still unanswerable here, because
  that agent is in none of them. The unblock condition is unchanged; what changed is that when a
  reachable corpus arrives, the adapter is no longer part of the wait.
