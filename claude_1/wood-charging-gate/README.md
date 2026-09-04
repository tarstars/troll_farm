# The wood-charging gate — pay for the third troll only if the troll beats the wood

Task `20260904-wood-charging-gate` (handoff `20260904T033533Z`, chartered to claude_1 on the owner's
approval; the owner's rule: *"we are going to predict two outcomes: with troll and without, and if
'with' wins, we do it"*). The champion of record plus ONE variable: a third troll that is funded only
while a forecast made from the live board says the troll's wood beats the wood its funding costs, and
abandoned back to ordinary play the turn it stops winning. The control is the champion itself.
`REPORT-2026-09-04.md` reads the gates.

| file | what it is |
|---|---|
| `gate.rs.in` | the Rust block: the door chop rate (the champion's own valuation of the best tree from our doors), the bill's fruit and iron times from the doors, the 27 chop-and-carry shapes, the two futures per shape (WITH, WITHOUT), the decision |
| `make_wood_gate.py` | the generator: seven anchored replacements on the champion's diagnostics arm AND its readable source through `local_claude_1/third-troll/make_third_troll.py`'s chain (sha-checked bases, every anchor once in both files, compile, compaction round trip, distinct from every bot, the diff's +/- counts). Four of the seven are the third-troll instrument's funding pathway verbatim (the roster cap, the funding mode, the bill split by ability, the chop fallback); the joint three-troll `select` is NOT carried (one variable) |
| `champion-wood-gate-v6-instrument.rs` (+ `.sha256`) | the built arm (the v6 diagnostics line untouched) |
| `wood-gate-readable.rs` (+ `.sha256`) | the readable champion with the same edit; `readable/diffs/wood-gate.diff` is the diff the owner reads |
| `cgauto/submissions/candidate-wood-gate-v6-instrument.rs` | the compacted submission (`readable/reports/candidate-wood-gate-v6-instrument.round-trip.json`) |
| `gate_read.py` | the gate read on the 24-map smoke slice: a stderr-only debug variant of the arm (its commands checked equal to the arm's on every map) plays beside the arm and the resident; per game the turns evaluated / admitted / declined and the reasons, the tuples, the third troll in game turns, the wood banked by turns 50 and 100 against the champion's |
| `calibrate_kappa.py` | the one calibration: the ratio of the record's realised wood per troll-turn (the starter's, the trained troll's) to the gate's trip rate on this slice |
| `gate-v1.rs.in`, `results/*-v1.*` | the first forecast (trip rates as realised rates, a contested-forest cap) and its read: it declined on every one of 4,593 evaluated turns and the candidate was the champion in play on 24/24 — kept as the record of why the calibration exists |
| `results/` | `build.json`, `kappa.json`, the gate read, the bed (`fixtures.json`, `bed.log`), the smoke (`smoke.json`, `smoke.log`), the timing (`turn-time.json`), the panel and field runs, `field.json` |

    python3 claude_1/wood-charging-gate/make_wood_gate.py
    python3 claude_1/wood-charging-gate/gate_read.py --out claude_1/wood-charging-gate/results/gate-read.json
    python3 local_claude_1/third-troll/fixtures_diff.py --arm $PWD/claude_1/wood-charging-gate/champion-wood-gate-v6-instrument.rs \
        --submission $PWD/cgauto/submissions/candidate-wood-gate-v6-instrument.rs --out $PWD/claude_1/wood-charging-gate/results/fixtures.json
    python3 local_claude_1/third-troll/smoke.py --arm claude_1/wood-charging-gate/champion-wood-gate-v6-instrument.rs \
        --records local_claude_1/third-troll/smoke-maps-seed0.jsonl --out claude_1/wood-charging-gate/results/smoke.json \
        --third-spec "$(cat claude_1/wood-charging-gate/results/third-specs.txt)"
    python3 claude_1/h2h-panel/turn_time.py --bot cgauto/submissions/candidate-wood-gate-v6-instrument.rs --maps 3
    python3 claude_1/h2h-panel/h2h.py --policy cgauto/submissions/candidate-wood-gate-v6-instrument.rs --bot <opponent.rs> --jobs 4 --out claude_1/h2h-panel/results/wood-gate-vs-<opponent>.json
    python3 claude_1/h2h-panel/field.py --opponent <name>=<candidate run>,<champion run> ... --expected-cells 400 --json-out claude_1/wood-charging-gate/results/field.json

## The rule as built

The champion has no third troll — it trains exactly one and never gathers for another — so the one
variable is the gated funding pathway as a whole. With two trolls, on every turn while 100 turns
remain, for each of the 27 shapes (speed 1–3, carry 1–3, harvest 0, chop 1–3) whose bill this map can
pay:

- **the funding time**: the starter's fruit trips (one item a trip from the doors, the champion's own
  `collection_eta`) and the trained troll's iron trips (a load a trip, mined at min(chop, carry) a
  turn); the wall is the longer; the troll arrives the turn after;
- **WITHOUT** = 4 × (fruit turns × the starter's realised rate + iron turns × the trained troll's
  realised rate): the wood the two gatherers would have banked in the same turns;
- **WITH** = 4 × the third troll's realised rate × the turns left after its arrival − the bill's fruit
  at face value (a point each, spent). The fruit's value as swap seeds is reported, not charged.

A realised rate is the trip rate from the live board (so it falls as the forest thins and rises with
the shape's talents) times κ, the measured ratio of banked wood to trip rate (`calibrate_kappa.py`;
the starter's κ and the trained troll's, the third troll scaled by the trained troll's). The gate
admits the best net shape whose WITH is strictly greater than WITHOUT; otherwise it declines and the
bot is the champion byte for byte. Nothing is remembered between turns: the decision is re-made from
the board every turn, and every input is measured from the doors as a set, never from a troll's cell
(the stage-2A lesson: a position-dependent input flips with a troll's step).

Conventions: a **game turn** is the 1-based index of the command line the bot answered; the referee
replay's tooltip `turn` is a frame index at two frames per game turn and is not used here.
