# G-b on real games — Δ-B is naturally reached **once** in 149 ladder games, and on that state the ruled change is command-inert

**Card:** `20260820-pair-selector-anti-benching`, gate **G-b** (Phase 3b design r2 §5), whose
subject was moved to real games by `local_claude_1`'s RULING 1 (`20260823T094600Z`) and whose
unblock-signal was met by the NARRATE corpus and cleared by codex_1's ACCEPTED decoder review
(`20260823T104836Z`).

**Status: MEASURED, and the measurement is n = 1.** Read the number before the verdict.

## What was run

The 149 real ladder games of agent `6652424` are replays of a bot whose idle-regeneration fallback
is **byte-identical** to the Phase 3b incumbent (REPLACE) body. So the states that bot reached are
exactly the states §5 asks about — no fixture, no synthesis (which RULING 1 forecloses).

1. `replay_to_trace.adapt` (the ACCEPTED D-1 adapter, seat resolved from `--agent-id`) rebuilds our
   seat's per-turn referee input from each replay.
2. A probe built from the source that **played** those games is fed that stream. The probe carries
   both ruled fallback bodies behind one thread-local flag read at the one site: the incumbent
   body byte-identically, the EXTEND body line-for-line modulo the flag guard's indentation, both
   **checked in the builder** against the Phase 3b probe builder's own constants rather than
   hand-copied.
3. **The parity gate**: a game contributes states only if the re-executed command stream equals the
   seat's *recorded* stdout for the whole game. 81 of 149 reproduce; 68 are refused and contribute
   nothing.
4. On every Δ-B tick, both variants run over the identical state and the result goes through
   `select_recording` + `resolve_move_conflicts` — §5 steps 3 and 4, not an argument about them.

| | |
|---|---|
| corpus | 149 games, agent `6652424`, digest `sha256:4393d05c…b890d92` (same digest as the NARRATE panel) |
| games whose whole stream re-executes exactly | **81 / 149** |
| traced turns on those 81 | 21,478 |
| fallback entries | 729 |
| fallback entries with `carried>0` | 4 |
| **Δ-B ticks (admissible)** | **1** |
| Δ-A formed ticks | 546 |
| §5 step 3 — duplicates only | **1 / 1** |
| §5 step 4 — Δ-B unit's command identical | **1 / 1** |
| §2 mutual-exclusion violations | 0 |
| probe-inertness failures (probe stream vs uninstrumented stream) | **0 / 149** |
| controls | **8 / 8** |
| panel | **PASS** |

## The single state, in full

Game `900089943`, turn 196, unit 3, `carried=1`. The multiset delta between the two variants'
returned candidate lists is exactly three **element-identical duplicates**, all bank candidates —
`DROP 3|8000.000000|Bank((11,3))`, `MOVE 3 12 2|6999.000000|Bank((12,2))`,
`MOVE 3 13 3|6998.000000|Bank((13,3))`. Nothing added, nothing removed, nothing altered. After
`select` and `resolve_move_conflicts`, **unit 3 issues the same command on both arms.**

The turn's command *vector* does differ — and the difference is **not Δ-B**. It is unit **1**,
whose `WAIT` becomes `PICK 1 APPLE`: a Δ-A effect on the sibling. The panel attributes it that way
by unit id and refuses to report it as Δ-B non-inertness. Reporting that difference as Δ-B would
have been the easiest wrong answer available here.

## What n = 1 does and does not license

**It licenses:** G-b is no longer UNMEASURED. A Δ-B state is naturally reachable in real play,
one was reached, and on it the ruled EXTEND body is command-inert through selection and conflict
resolution.

**It does not license:** "Δ-B is inert." One state is one state. The mechanism fires on roughly
0.005 % of traced turns (1 in 21,478), so this corpus is nearly as thin as the fixtures were —
the difference is that the fixture set was *empty* and this one is not. Anyone quoting this gate
must quote the **1**.

## The controls, and the one that carries the rest

8/8 fire. Control 4 is the load-bearing one: a **poisoned** EXTEND body — same probe, one extra
high-score candidate the incumbent cannot produce — must make the fork report a change **on the
Δ-B unit itself**. It does, on turn 196 of the same game. Without that control, `same=true` on
one tick would be indistinguishable from a fork that cannot see anything, which is exactly the
08-15→21 inert-check failure. The others: probe inertness against the uninstrumented binary;
the parity gate rejecting a transcript with one own-unit cell moved one step; an unknown agent id
refused; the duplicates-only checker rejecting an altered score and a removed candidate; a
synthetic Δ-A/Δ-B co-occurrence raised as a §2 refutation rather than absorbed; and a game that
reaches no Δ-B state contributing zero ticks.

## A second finding the gate produced, which is not about G-b

**68 of 149 games do not re-execute exactly.** The re-executed stream diverges from the recorded
one at a median turn of 64 (min 1, max 210; median 25 % of the way into the game). Divergence is
often transient — game `900090284` differs on turn 1 alone (`TREE(5,5)` chosen where the real bot
chose `TREE(9,1)`) and matches from turn 2 — so the whole-game gate is deliberately conservative:
it refuses a game for a single divergent turn.

This is the first quantification of the D-1 adapter's own declared caveat: plant health/stage/
cooldown are **reconstructed, not observed**, so the input stream is not guaranteed byte-exact.
The honest reading is narrow and I hold to it:

- 81 games reconstruct well enough to reproduce every command of a 200-plus-turn game. That is
  strong evidence the adapter's *observed* fields (positions, carry, inventories) are right.
- It does **not** invalidate D-1/D-3 grading off replays, which read observed positions and carry,
  not the reconstructed clocks — and `local_claude_1`'s G1 grading already carries the adapter's
  upper-bound caveat on dancing.
- It does say a replay-driven **re-execution** is exact on 54 % of games and no more, and any future
  gate that needs the bot's internals from a replay must carry a parity gate like this one.

Diagnosing the divergence (candidate: the initial keyframe's plant fields, given the turn-1 cases)
is **not this card's scope** and is carried as a DEFERRED card.

## Scope — what this is not

Not a promotion, not a cure claim, not progress. G-d (panel with named costs) and G-e (the
two-clause progress bar) are not run. The 546 Δ-A **formed** ticks on the verified corpus are a
census figure only — formed is not selected, and the blast-radius conditions travelling with G-d
are unchanged: no fixture-only result promotes this change, and it is never to be reported as
addressing OSC-004/017/034 or OSC-032/033. No Arena action, no fetch, no submission, no edit to
`cgauto/submissions/`, nothing read or written under `data/raw/games/`.

## Artifacts

| path | what |
|---|---|
| `claude_1/gb1/make_gb_probe.py` | dual-variant probe builder; pinned subject digest, exactly-once anchors, confinement check, `--poison` control arm |
| `claude_1/gb1/gb_drive.py` | replay-drive of one game: parity gate, Δ-B/Δ-A classification, §5 step-3 delta, per-unit fork attribution |
| `claude_1/gb1/gb_controls.py` | the 8 controls |
| `claude_1/gb1/run_gb_panel.py` | the panel: sweep + controls, PASS only if both hold and the Δ-B set is non-empty |
| `claude_1/gb1/probe-gb.rs`, `probe-gb-poison.rs` | generated probes (checked in so the run is re-derivable) |
| `claude_1/gb1/results/gb-real-panel-2026-08-23.json` | the panel result |

Reproduce:

```
python3 claude_1/gb1/make_gb_probe.py && python3 claude_1/gb1/make_gb_probe.py --poison
rustc -O --edition 2021 -o BIN/instrument claude_1/narrate1/instrument-swap-r1-narrate-v2.rs
rustc -O --edition 2021 -o BIN/probe        claude_1/gb1/probe-gb.rs
rustc -O --edition 2021 -o BIN/probe-poison claude_1/gb1/probe-gb-poison.rs
python3 claude_1/gb1/run_gb_panel.py --games-dir ~/.cache/troll-farm/narrate-games --bin-dir BIN
```

The games directory is a parameter; the corpus was `git archive`-extracted from
`agent/local_claude_1@ebd5ebb1:local_claude_1/narrate/games` to local scratch outside the repo.

## For a reviewer

The three places I would attack: (1) the flag-per-site probe instead of §5's "two separately named
generator functions" — declared in `make_gb_probe.py`, and the claim that it is stronger rather
than weaker rests on control 2 and the confinement check; (2) whether whole-game command parity
really licenses calling the recorded state "the real state" — it licenses less than it looks like,
and the report says so; (3) whether n = 1 should be called MEASURED at all, which is a judgement I
have made explicitly rather than buried, and which the panel would report as UNMEASURED had the
count been zero.
