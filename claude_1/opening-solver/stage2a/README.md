# Stage 2A — the opening dispatcher in the champion (rules first)

Task `20260903-opening-solver`, stage 2A (handoff `20260903T103500Z`). The offline opening solver's
dispatcher (`../solver.py`), in its deterministic form, ported to Rust inside the champion of record
as the opening controller from turn 1 to the third troll's TRAIN; the champion's own play takes over
from there, byte for byte what it is today. The report `REPORT-2026-09-03.md` reads the gates.

| file | what it is |
|---|---|
| `dispatcher.rs.in` | the Rust block: the second troll's talents from the draw (R1), the third troll's shape from the iron, the task values (R2, R5), the TRAIN on the pre-turn stock with no PICK on that turn (R3), the seed's cell (R4); one plan recomputed every turn from the live board |
| `make_opening_dispatcher.py` | the generator: five anchored replacements on the champion's diagnostics arm AND its readable source through `local_claude_1/third-troll/make_third_troll.py`'s chain (sha-checked bases, every anchor once in both files, compile, compaction round trip, distinct from every bot, the diff's +/- counts) |
| `champion-opening-dispatcher-v6-instrument.rs` (+ `.sha256`) | the built arm (the v6 diagnostics line untouched) |
| `opening-dispatcher-readable.rs` (+ `.sha256`) | the readable champion with the same edit; `readable/diffs/opening-dispatcher.diff` is the diff the owner reads |
| `cgauto/submissions/candidate-opening-dispatcher-v6-instrument.rs` | the compacted submission (`readable/reports/candidate-opening-dispatcher-v6-instrument.round-trip.json`) |
| `probe.py` | one smoke record turn by turn; `--debug FILE` builds a throwaway variant that prints every task's value to stderr (how the two defects below were found) |
| `results/` | `build.json`, the bed (`fixtures.json`, `bed.log`), the smoke (`smoke.json`, `smoke.log`), the timing (`turn-time.json`, `turn-time.log`), the field runs and the field reading |

    python3 claude_1/opening-solver/stage2a/make_opening_dispatcher.py
    python3 local_claude_1/third-troll/fixtures_diff.py --arm $PWD/claude_1/opening-solver/stage2a/champion-opening-dispatcher-v6-instrument.rs \
        --submission $PWD/cgauto/submissions/candidate-opening-dispatcher-v6-instrument.rs --out $PWD/claude_1/opening-solver/stage2a/results/fixtures.json
    python3 local_claude_1/third-troll/smoke.py --arm claude_1/opening-solver/stage2a/champion-opening-dispatcher-v6-instrument.rs \
        --records local_claude_1/third-troll/smoke-maps-seed0.jsonl --out claude_1/opening-solver/stage2a/results/smoke.json --third-spec "2 3 0 3|2 3 0 2|2 3 0 1"
    python3 claude_1/h2h-panel/turn_time.py --bot cgauto/submissions/candidate-opening-dispatcher-v6-instrument.rs --maps 3
    python3 claude_1/h2h-panel/h2h.py --policy cgauto/submissions/candidate-opening-dispatcher-v6-instrument.rs --bot <opponent.rs> --jobs 4 --out claude_1/h2h-panel/results/opening-dispatcher-vs-<opponent>.json
    python3 claude_1/h2h-panel/field.py --opponent <name>=<candidate run>,<champion run> ... --expected-cells 400 --json-out claude_1/opening-solver/stage2a/results/field.json

## Two defects the probe found before any gate, and what they teach

1. **The dance.** A Python dispatcher whose tasks persist, ported as "recompute the argmax every turn",
   stepped between two cells for 20 turns: the bottleneck weights and the seed's walk were measured from
   the door nearest the troll, which flips between two door-adjacent cells, so the argmax flipped with
   it. Fix: every input measured from a position-free reference (the doors as a set), a 5 % hold on
   last turn's target, and every remaining position-dependent term monotone along the walk.
2. **Points before the bill.** With only plums left on the bill, a near apple tree's quarter-point
   fruits every other turn outscored the map's only reachable plum tree 16 steps away, and the third
   troll never came (65 lemons in the shack at turn 200). Fix (R5 as ruled): while anything the bill
   needs can be fetched, a harvest for points alone is not an option.

Both fixes are deviations from the Python solver's letter (which let surplus compete and measured from
the troll's own door) in the direction of the ruled rules; the solver's verified schedules were not
affected by either because its tasks persisted and its panel maps had nearer plums.
