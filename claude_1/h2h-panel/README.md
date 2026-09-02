# The head-to-head panel (P-0, Track P)

Two compiled single-file bots against each other on real maps, both seats, paired by map. The
selector for the port of norxondor_gorgonax (`coordination/tasks/20260902-norxondor-port.md`).

| file | what it is |
|---|---|
| `h2h.py` | the driver: the July Python referee (`fuzz_panel.FuzzReferee`), one `engine.rs::step` a turn, each bot a subprocess on its own seat (`nn_runtime.SeatRendering`); rows in the shape `local_claude_1/nn-bot/gate1.py` reads; a paired reading by the gates' own clustered bootstrap over maps |
| `make_panel.py` | draws the panel: N distinct maps by a seeded shuffle of a corpus, start inventories as `smoke.py` draws them, `.sha256` sidecar and a manifest |
| `panel-200-seed1.jsonl` | **the panel**: 200 maps, seed 1 (`.sha256`, `.manifest.json` beside it) |
| `bed_new_bot.py` | the bed for a bot that is not the champion's child: 34 frozen situations — plays, deterministic, compacted == readable, v6 telemetry decodes; "differs from the champion" informational |
| `test_h2h.py` | the tests (`/home/tarstars/venvs/nn-bot/bin/pytest claude_1/h2h-panel/test_h2h.py -q`) |
| `results/` | the validity runs of 2026-09-02 (`P0-2026-09-02.md` reads them) |

    python3 claude_1/h2h-panel/h2h.py --policy <candidate.rs> --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs --jobs 4 --out claude_1/h2h-panel/results/<candidate>-vs-champion.json
    python3 claude_1/h2h-panel/bed_new_bot.py --readable readable/<candidate>.rs --compacted cgauto/submissions/<candidate>.rs

Replays (`--replays`) are large (50 MB a panel) and belong under `/data/scratch/`, not in the repo.
