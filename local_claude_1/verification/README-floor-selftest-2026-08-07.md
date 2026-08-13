# local_claude_1 independent floor self-test — 2026-08-07

Coordinator half of the owner-ordered review (19:30Z 2026-08-06). Executed on the project host
by `local_claude_1`, from the committed tooling, not from any agent's report.

## Command

```bash
cd claude_1/pipeline
python3 fuzz_panel.py --config <floor-config> --report <report> --json <result>
```

Config is `local_claude_1-floor-selftest-config-2026-08-07.json`: the committed
`claude_1/pipeline/fuzz-panel-config.json` with **candidate source set equal to the parent
source** (both `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`), absolute
paths, and a private games/bin cache. Nothing else changed.

Tooling hashes at execution:

- `claude_1/pipeline/fuzz_panel.py` — `cc7db6f2f048a1739e587cff9e26e5783d08f69672e233b227a6294f03b6571d`
- `claude_1/pipeline/fuzz-panel-config.json` — `f5394e7a8b974062b07f42bc535e113dca2e9d67b64c9b196c1a4b63660b99fe`

Note: this panel is **not** byte-identical to the `b16f44d6` pinned recipe panel
(`45d40344…`); it carries claude_1's later P4 terminal-state calibration. The result below is
therefore the *calibrated* floor, and is the number to compare against claude_1's calibrated
floor column.

## Result — the gate blocks its own reference implementation

**BLOCK, 118 of 240 games**, 240 games, 0 flagged, 14.5 s wall.

This reproduces claude_1's reported calibrated floor (118/240) exactly.

Total detector episodes over the floor run (parent judged against itself):

| detector | episodes |
|---|---|
| D-1 | 35 |
| D-2 | 0 |
| D-3 | 0 |
| D-4 | 6 |
| D-5 | 1 |
| D-6 | 15 |
| D-7 | 0 |
| D-8 | 0 |
| D-9 | 196 |

## Findings

1. **The owner's strict gate is unsatisfiable as written.** The standing rule adopted
   2026-08-06 is raw `D-1 == 0` and `D-4 == 0` over this panel with no inherited-parent
   exemption. The parent — the reference implementation of the current live lineage — itself
   produces **35 D-1 and 6 D-4 episodes**. No candidate derived from it can satisfy the rule,
   and a gate its own reference fails cannot rank a successor.
2. **D-2, D-3 and D-8 never fire at all.** They are unexercised, not clean; reporting them as
   PASS overstates coverage. claude_1's "UNPROVEN, never PASS" proposal is confirmed by this
   run.
3. **D-9 dominates the floor** (196 of 253 total episodes here) while firing on a bot that by
   construction displaces no TRAIN funding. Directionally this supports claude_1's
   zero-information claim, but note the statistic differs from claude_1's reported "exactly 74
   times in all three runs" — that is a different metric (or a different calibration stage), and
   the two counts must be reconciled before section 5 of the redesign is ratified. I did not
   verify the constant-74 claim.

## Scope

Read-only measurement. No source, frozen artifact, submission, TestSession, or Arena mutation.
Sacred source unchanged.
