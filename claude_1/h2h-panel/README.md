# The head-to-head panel (P-0, Track P)

Two compiled single-file bots against each other on real maps, both seats, paired by map. The
selector for the port of norxondor_gorgonax (`coordination/tasks/20260902-norxondor-port.md`).

| file | what it is |
|---|---|
| `h2h.py` | the driver: the July Python referee (`fuzz_panel.FuzzReferee`), one `engine.rs::step` a turn, each bot a subprocess on its own seat (`nn_runtime.SeatRendering`); rows in the shape `local_claude_1/nn-bot/gate1.py` reads; a paired reading by the gates' own clustered bootstrap over maps |
| `make_panel.py` | draws the panel: N distinct maps by a seeded shuffle of a corpus, start inventories as `smoke.py` draws them, `.sha256` sidecar and a manifest |
| `panel-200-seed1.jsonl` | **the panel**: 200 maps, seed 1 (`.sha256`, `.manifest.json` beside it) |
| `bed_new_bot.py` | the bed for a bot that is not the champion's child: 34 frozen situations — plays, deterministic, compacted == readable, v6 telemetry decodes; "differs from the champion" informational |
| `field.py` | **rung 1's field reading** (ruling 09-02 08:4xZ): the candidate's and the champion's `h2h.py` runs against the same opponent, paired by (map, seat), the difference candidate − champion in win indicator and margin, per opponent and for the field (every opponent's cells of one map carried together), clustered bootstrap over maps; **verdict on the field win-indicator interval** (ruling 09-02 09:23Z; the margin printed beside it): above / below / straddles zero, INCONCLUSIVE on any fault |
| `test_field.py` | its tests (`/home/tarstars/venvs/nn-bot/bin/pytest claude_1/h2h-panel/test_field.py -q`, 10 tests, no compiled bot needed) |
| `test_h2h.py` | the tests (`/home/tarstars/venvs/nn-bot/bin/pytest claude_1/h2h-panel/test_h2h.py -q`) |
| `endgame_sig.py` | the two endgame signatures (MOVE per troll-turn in turns 251–300; tree-size units standing at the end) and the roster before turn 150 and at the end, from an `h2h.py --replays` file replayed through the same referee |
| `turn_time.py` | one bot's per-turn wall time inside the referee against the platform's budget (1000 ms turn 1, 50 ms after; `docs/mechanics.md`): first-turn max, warm median / p99 / max, the count over 50 ms; run before a bot's 400-game run |
| `results/` | the validity runs of 2026-09-02 (`P0-2026-09-02.md` reads them) and the champion of record's field runs (below) |

    python3 claude_1/h2h-panel/h2h.py --policy <candidate.rs> --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs --jobs 4 --out claude_1/h2h-panel/results/<candidate>-vs-champion.json
    python3 claude_1/h2h-panel/bed_new_bot.py --readable readable/<candidate>.rs --compacted cgauto/submissions/<candidate>.rs

    python3 claude_1/h2h-panel/field.py --opponent champion=<cand>-vs-champion.json,champion-vs-champion.json --opponent orchard6=<cand>-vs-orchard6.json,champion-vs-orchard6.json --expected-cells 400 --json-out claude_1/h2h-panel/results/<cand>-field.json

Replays (`--replays`) are large (50 MB a panel) and belong under `/data/scratch/`, not in the repo.

## The champion of record's field runs (2026-09-02, pinned; a candidate's day costs only its own four)

Policy `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` (sha `0e92f8fa…`) against each
opponent on the 200-map panel, both seats, 4 jobs on the VM. These are the `<champion-run.json>` halves of every
`--opponent` pair in `field.py`.

| opponent | file | sha256 | W–T–L (champion) | margin [95%] | faults |
|---|---|---|---|---|---|
| the champion itself | `results/champion-vs-champion.json` | `563c91f39ab5f227188b72ef7d8906d5f0bcfe642cf48ae1e2667d243efd5762` | 113–174–113 | 0.00 | 0/0/0 |
| orchard 6 (`candidate-orchard6-v6-instrument.rs`, `32384936…`) | `results/champion-vs-orchard6.json` | `8ff7782720885c6affc741090bec6bfdfdf1466ca815a1502e3f27936c567fd2` | 324–11–65 | +26.04 [+21.55, +30.57] | 0/0/0 |
| the old champion, denial on (`candidate-champion-v6-instrument.rs`, `72673124…`) | `results/champion-vs-old-denial-on.json` | `703938fff6f0d83845c9bbda824a0a9acf7d8e158dce81a14dca114a15423e2f` | 147–131–122 | +0.68 [−0.08, +1.43] | 0/0/0 |
| the network clone (`candidate-nn-clone.rs` at `3ad8b7c0`, `4c5a096d…`) | `results/champion-vs-nn-clone.json` | `11e7ae378df403e3d5005e0a435a288897a56816d504390b4e380104a8ce7864` | 331–3–66 | +55.52 [+48.16, +62.91] | 0/0/0 |

The clone's time budget (`results/turn-time-nn-clone.json`, `turn_time.py` on 3 maps × 2 seats, 1,800 timed turns, the
VM idle): first-turn max 12.2 ms, warm median 6.5 ms, p99 9.7 ms, max 12.1 ms, 0 turns over 50 ms — inside the platform's
limit, so it stays in the field. The clone's games run long (272 of 400 to the turn limit) and it is the slowest
opponent at ~2,800 games an hour against ~9,700–29,000 for the rule bots; a candidate's four runs take about 15 minutes.

## The port v2's four field runs (2026-09-02 11:21Z–11:36Z; rung 1: FIELD_BELOW_ZERO)

Policy `cgauto/submissions/candidate-norxondor-port-v2.rs` at codex_1's `7e45fa4c` (sha `411b0565…`), the same panel,
opponents and jobs as the champion's runs above. `claude_1/norxondor-port/REPRO-2026-09-02.md` reads them.

| opponent | file | sha256 | W–T–L (port) | margin [95%] | faults |
|---|---|---|---|---|---|
| the champion of record | `results/port-v2-vs-champion.json` | `521e0a0c9992b6b15cb5cc085d1691f44a8569720d93bb0a230f3212bc9adef3` | 16–2–382 | −59.77 [−64.38, −55.10] | 0/0/0 |
| orchard 6 | `results/port-v2-vs-orchard6.json` | `97c3a886a811d1337abdf204ea46d4272b3aaa687613c79a7a4a5ced5f7f30a7` | 29–0–371 | −84.67 [−91.03, −77.79] | 0/0/0 |
| the old champion, denial on | `results/port-v2-vs-old-denial-on.json` | `b673b5fcfb27f29533c43a22ce4ea95ecf9bf4ceb2eb0f899d9d677b20b5542a` | 10–4–386 | −48.80 [−52.74, −44.94] | 0/0/0 |
| the network clone | `results/port-v2-vs-nn-clone.json` | `1341e35cf935e1f5cabfb191036d72a88f45b074e732b3982675759e87d5fd45` | 186–4–210 | −9.08 [−18.66, +0.73] | 0/0/0 |

`results/port-v2-field.json` (`d3942b556115c9faeb5d103da4fe9d12dde244dd65b423a2db9a7fceb522d782`): FIELD Δwin −0.4213 [−0.4525, −0.3894], Δmargin −71.14 [−75.61, −66.67] —
**FIELD_BELOW_ZERO**. `results/port-v2-vs-legality24.json` is the 24-map legality run (48 games, 0/0/0, the duel
reproduced to the decimal). `endgame_sig.py` reads the two endgame signatures and the roster from an `h2h.py --replays`
file through the same referee (`results/port-v2-endgame-sig.json`).
