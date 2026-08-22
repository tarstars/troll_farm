# Gate repair #2: absolute terminal-state calibration of P4 (2026-08-06)

Repair #1 (0a048cf8 / f76f3599 / 2c1eca6e) made the fuzz-panel acceptance
gate **RAW/ABSOLUTE**: every D-1..D-9 episode and every P4 stall blocks, with
no parent-relative exemption of any kind. **That ruling stands and is not
weakened here** — nothing in this repair consults the parent.

Repair #1 also exposed that the raw gate was *unsatisfiable and
non-discriminating*: run parent-vs-parent (byte-identical candidate) it
blocked **223 / 240** games, and P4 liveness alone accounted for 200 of
them.

## Diagnosis (measured, not assumed)

Over the 204 P4 stall windows of the parent-vs-parent floor run:

| stall windows | count |
|---|---|
| total | 204 |
| **ending at turn 199 (the sim horizon; turns run 0..199)** | **198** |
| mid-game (window_end 66 / 99 / 108 / 170 / 190) | 6 |

and, at the state where each trailing window ends:

| trailing-window state | count / 198 |
|---|---|
| own cargo empty | 198 |
| **no plant left anywhere on the map** | **174** |
| no plant reachable by an own unit | 174 |
| no reachable plant **and** empty cargo | 174 |
| all-WAIT for the whole window | 156 (150 of the 174) |
| ≥ 1 reachable plant still standing | 24 |

So P4 was flagging "the bot finished the work the map offered and coasted to
the horizon" as a liveness failure. That is a **harness calibration defect**,
not a bot defect, and it was the dominant term in the raw floor.

## The predicate (one sentence)

> A stall window blocks only over the turns in which the referee world state
> still offers the own player a resource action — i.e. some own unit still
> carries something to bank or plant, or some plant still stands on a cell an
> own unit can walk to (harvest / chop) — so a stall that begins after the
> world is exhausted for the rest of the game is excused, while any stall of
> ≥ `liveness_window` **live** turns, mid-game or running to the sim horizon,
> still blocks.

Implementation (`claude_1/pipeline/fuzz_panel.py`):

- `work_remaining(tr, t)` : **fuzz_panel.py:713** — pure world-state test on
  the referee state `S_t` from the candidate's own transcript: own cargo
  non-empty → True; no plants → False; otherwise BFS over `smap.walkable`
  from the own units and ask whether any plant cell is reached.
- `live_horizon(tr)` : **fuzz_panel.py:735** — first turn of the maximal
  terminal suffix (`tr.T + 1` if the world never runs out).
- `eval_p4(tr_c, tr_p, window)` : **fuzz_panel.py:788** — trims each stall
  window to `[a, live_horizon-1]` and blocks iff the trimmed length is still
  ≥ `window`. Violations now carry `live_end` / `terminal_from` for audit.

Why this predicate:

- It is grounded in the **referee/world state** (static map + plants + own
  units), as required, not in a command pattern. All-WAIT was *not* used even
  as a supporting condition: it holds in only 150 of the 174 excused windows,
  and the other 24 are units wandering an empty board — churn, not a
  resource-liveness failure. Requiring all-WAIT would have punished
  wandering while excusing nothing extra.
- Only `HARVEST`/`CHOP` (need a reachable plant), `DROP` (needs cargo) and
  `PLANT` (needs a carried fruit) can move the own inventory or own cargo
  through a resource action, so the two clauses are exactly the closure of
  "nothing left to harvest, chop, plant, or bank".
- Deliberate boundary, stated for the record: banked fruit could in principle
  be `PICK`ed back out and re-planted, which the progress metric would score.
  The calibration does **not** demand that — P4 is a liveness floor, not an
  optimality oracle, and requiring bots to recycle banked score would reward
  churn. On the floor run this is moot: **0** of the 199 games with a
  terminal suffix ended with a plantable fruit banked.
- Trimming (rather than exempting whole trailing windows) is the conservative
  form: a bot that idles for 100 turns while plants stand and is then bailed
  out by the opponent chopper clearing the board still blocks. On this data
  the two forms coincide exactly (174 excused, 30 blocking either way).

## Tests (TDD)

`test_fuzz_panel.py` gains `synth_trace` / `stall_trace` (real `td.Trace`
objects built from synthetic transcripts, so the predicate sees exactly what
a live game exposes) and `TestP4TerminalCalibration` (7 tests).

RED against repair-#1 code, GREEN after:

- `test_finished_work_then_idle_to_horizon_passes` — works to turn 120, clears
  the last plant, idles to 199 → was BLOCK(120,199), now PASS.
- `test_only_plant_unreachable_is_terminal` — the one remaining plant walled
  off from the unit → PASS.
- `test_work_remaining_is_a_pure_world_state_predicate` — the predicate and
  horizon helpers exist and are world-state-only.
- `test_no_parent_reference_in_eval_p4_body` — `eval_p4`'s body (docstring
  stripped) contains none of `parent` / `inherit` / `aligned` / `tr_p`.

GREEN before **and** after — the over-exemption guards (these are what a
naive "excuse any trailing stall" or "excuse all-WAIT" fix would break):

- `test_midgame_stall_with_work_remaining_blocks` (40–109, ripe plant on the
  board, then resumes).
- `test_trailing_stall_with_work_remaining_blocks` (40–199 to the horizon
  with a reachable ripe plant).
- `test_trailing_stall_with_unbanked_cargo_blocks` (board cleared but cargo
  never banked).

`test_p4_blocks_when_parent_also_stalls` keeps its repair-#1 intent (no
parent exemption) on a world where work remains all game.

Suites: `python3 -m unittest discover` in `claude_1/pipeline` → **53 pass**
(`test_fuzz_panel` 29, `test_pre_review` 24).

## Re-measurement (calibrated raw gate)

Same committed geometry: 6 seeds × 120 maps × 2 seats = **240 candidate
games**, 200 turns. Parent for every run:
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
(sha256 `a8eb3b2b…`). Candidates from `origin/agent/chatgpt_1-banana-solve`,
`chatgpt_1/banana-solve/candidate-banana-r2.min.rs`: commit `bf94dbc0` →
blob sha256 `bbe54a489c98222d…` and branch tip `91d4907a` → blob sha256
`7ad9d784c6bd6941…` (both verified against the declared prefixes; both
available).

### Blocking games / 240

| run | repair #1 (raw) | repair #2 (calibrated raw) | Δ |
|---|---|---|---|
| **PARENT vs PARENT — the FLOOR** | 223 | **118** | −105 |
| chatgpt_1 `bbe54a48` | 217 | **116** | −101 |
| chatgpt_1 `7ad9d784` (tip) | 221 | **146** | −75 |

### Per-property breakdown (games with ≥ 1 blocking violation)

| run | P1 | P2 | P3 | P4 (was) |
|---|---|---|---|---|
| FLOOR (parent) | 114 | 4 | 0 | **29** (200) |
| `bbe54a48` | 111 | 4 | 0 | **25** (192) |
| `7ad9d784` | 129 | 0 | 7 | **79** (195) |

### P1 breakdown by detector (games / episodes) — unchanged by this repair

| run | D-1 | D-4 | D-5 | D-6 | D-7 | D-9 |
|---|---|---|---|---|---|---|
| FLOOR | 32 / 35 | 6 / 6 | 1 / 1 | 9 / 15 | — | 74 / 196 |
| `bbe54a48` | 27 / 29 | 6 / 6 | 1 / 1 | 9 / 15 | 2 / 2 | 74 / 196 |
| `7ad9d784` | — | 35 / 46 | — | — | 35 / 67 | 74 / 176 |

Byte-identical to the repair-#1 numbers, confirming the change touched P4
only.

The residual floor P4 term — 30 windows in 29 games — is exactly what the
calibration is *supposed* to keep: 6 mid-game stalls and 24 stalls running to
the horizon **with a reachable plant still standing** (one game has both).
The bot sits, or wanders, next to live work; those are genuine parent
liveness bugs and remain blocking.

## KEY QUESTION: is the gate discriminating?

**Partly — it now ranks, but it still cannot accept.**

*Discrimination (the good news).* Per-map paired comparison against the floor
(identical map + opponent + seat):

| candidate | maps it blocks that the parent passes | maps the parent blocks that it passes | net |
|---|---|---|---|
| `7ad9d784` | **35** (D-4 21, D-7 13, P4 30, P3 3 violations) | 7 | **+28** (146 vs 118) |
| `bbe54a48` | 2 (D-7 1, P4 1) | 4 | −2 (116 vs 118) |

Before the calibration the tip candidate scored *better* than the parent
(221 < 223) — the gate carried no information. It now scores **28 games
worse**, and the excess is attributable per map: 30 new P4 stalls where work
demonstrably remained, 21 D-4 and 13 D-7 episodes, and 7 P3 dormancy
(orchard-inertness) breaches. That is the expected signature of a candidate
inducing real defects, and it is now visible. `bbe54a48` sits within noise of
the parent (−2), consistent with a near-inert candidate — also a meaningful
reading rather than an artefact.

*Not yet acceptable (the remaining defect).* The floor is **118 / 240 =
49 %**, not near 0. An inert candidate still cannot be CLEAR. What dominates
now:

| floor term | games |
|---|---|
| P1 / **D-9** | **74** (63 of them block on D-9 *alone*) |
| P1 / D-1 | 32 |
| P4 (residual, genuine) | 29 |
| P1 / D-6 | 9 |
| P1 / D-4 | 6 |
| P2 | 4 |
| P1 / D-5 | 1 |
| floor with D-9 removed | 55 |
| floor with D-9 + D-1 removed | 46 |

**Next calibration defect, named: D-9's unpaired clause.** D-9 ("second-worker
TRAIN displacement") flags, absolutely, *any banana-attributable command
(`PLANT`/`PICK … BANANA`) issued before the candidate's `TRAIN` while it has
one unit*. Pre-TRAIN banana funding is precisely the shipped, arena-rated
parent's own strategy (`preseed-orchard-coverage`), so the detector fires
196 times across 74 parent games and is the single largest term in the floor
— 63 games block on nothing else. As an absolute rule it encodes a design
opinion the reference implementation contradicts, so no inert candidate can
pass it. That question belongs to the detector's integrator
(`trace_detectors.py` is out of scope here and unmodified); it is the next
thing to resolve before the gate can be an *acceptance* authority rather than
a ranking one. After D-9 the next terms are D-1 (32 games of parent-family
oscillation) and the 29 genuine P4 stalls.

## Artifacts

Scratchpad `diag2/`: `cfg-{floor,bbe54a48,7ad9d784}.json`,
`report-*.md` (markdown — note the `--report` output is markdown regardless
of the file name used), `out-*.json`, `cand-{bbe54a48,7ad9d784}.min.rs`;
game archives under `fuzz/games-p4cal-*`. Repair-#1 counterparts remain in
`diag/`.
