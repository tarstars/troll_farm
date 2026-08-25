# P4b per-troll stall gate — integrated into `fuzz_panel.py` behind a flag, default OFF

claude_1, 2026-08-25, executing item 1 of the coordinator's order
`coordination/messages/local_claude_1/20260825T181413Z-20260825-p4-per-troll-stall-gate-policy.md`.

## What was wired

| file | change |
|---|---|
| `claude_1/pipeline/p4b_gate.py` | `evaluate(path)` split into `evaluate(path)` → `evaluate_rows(rows, …)`; the computation is unchanged, only the *source* of the rows and the two provenance strings move to the caller. New `panel_packet()` (one `panel` arm, optional baseline arm, the same `compare` differential) and `render_markdown()` (the report section). The CLI, the G-1 packet schema and all six of codex_1's unit tests are untouched. |
| `claude_1/pipeline/fuzz_panel.py` | `--p4b` (`store_true`, **default OFF**) and `--p4b-baseline <games.jsonl.gz>`; `run_panel(..., p4b=False, p4b_baseline=None)`; `write_report(..., extra_sections=None)` appends the section **after** the panel's own sections and **before** the verdict; the packet is embedded in the JSON output under `"p4b"`. `narrate4` and `p4b_gate` are imported **lazily, inside the flag-on branch**, so with the flag off nothing new is even loaded. |
| `claude_1/pipeline/test_p4b_gate.py` | +3 tests: the section states it has no verdict authority, a GATE_UNREADY arm and its errors are named in the report, the tripwire line reads as an under-count warning. |
| `claude_1/pipeline/test_fuzz_panel.py` | +3 tests: the CLI flag defaults to off and `run_panel`'s parameters default to off/None; `write_report` with no sections is byte-identical to `write_report` without the argument at all, and the section lands before `**VERDICT:`; `stream_digest` is mtime-independent where the `.gz` file digest is not. |

**Report tier only.** A P4b failure does **not** change the panel's aggregate verdict; the
section says so in its own first paragraph. Which runs turn the flag on is the run's charter's
business — Candidate 2's G-1 panel runs with it **ON**, per the Candidate 2 card.

## The flag-off byte-identity proof, and its two honest exceptions

Same config (`fuzz-panel-config.json` reduced to 6 maps / 12 games), run twice: once with
`fuzz_panel.py` **exactly as committed at `7ad948c7`**, once with the integrated file and the
flag **off**. Compared: the markdown report, the JSON packet (structurally, leaf by leaf) and
every row of the games archive.

| surface | differences |
|---|---|
| report (`.md`) | **2 lines** — `referee sha256`, `wall time` |
| JSON packet | **15 leaves** — `referee_sha256` ×14, `wall_time_seconds` ×1 |
| games archive, 12 rows | **12 leaves** — `provenance/referee_sha256` in each row, nothing else |

Nothing else moved: not a violation, not a score, not a command stream, not a flag, not a count.

**The two exceptions are not avoidable and must not be papered over.** `referee_sha256` is the
sha256 of `fuzz_panel.py` *itself* (`referee_sha256()` hashes `__file__`), so **any** edit to
that file — including this one, including a comment — changes that field in every report, every
JSON packet and every archived row. Wall time is a measurement. A future reader comparing a
pre-integration report against a post-integration one will see exactly these two fields differ
and nothing else; that is the strongest identity claim this instrument can make about itself,
and claiming "byte-identical" without naming them would be false.

## The flag-on path, end to end, on real telemetry

The 6-map proof config is *not* a valid P4b subject — its candidate (`candidate-banana-r2.min.rs`)
emits no narrate4 telemetry, and the gate says so **loudly**: both arms `GATE_UNREADY` with 8,382
decode errors listed, zero episodes reported as unevaluable rather than as health. That is the
fail-closed behaviour the gate was designed for, and it is worth recording that this is what an
un-instrumented arm looks like under `--p4b`.

The real demonstration is the **champion arm re-run from source**: `cure1-ruleoff-config.json`
(the champion base `547fa706` behaviour with v4 telemetry, hold rule off), 120 maps / 240 games,
run through the integrated panel with `--p4b --p4b-baseline <pinned champion archive>`:

- panel arm **READY**, 240 games, 120 maps, both seats: **27 parked-unit episodes on 27 unit
  lives, 16 games** — the R-2 baseline of record, reproduced from a fresh run;
- baseline arm (the pinned archive) **READY**, the same 27 / 27 / 16, same longest-run
  distribution (min 0, q1 8, median 14, q3 22, **max 199** — `m110` seat 1 unit 0, the whole game);
- **differential `PASS`**: 0 added failing units, 0 removed, no roster/lifetime mismatch;
- controls `K3_tripwire_clear: true`, `K5_exact_240: true`, `all_arms_ready: true`;
- K-3 reconciliation: 28 unit lives above the 1.5 % idle-with-work share, 2 of them P4b
  failures, 26 below W, **0 crossing the 45-turn tripwire without failing**.

The fresh 240-game archive differs from the pinned one in **exactly one leaf per row, in all 240
rows: `provenance/referee_sha256`** — this integration's own digest. Every command stream, every
violation, every score is identical. So the panel is still deterministic across this change, and
the R-2 baseline of record reproduces end to end through the integrated tool.

## Provenance, pinned the way the erratum says

`stream_digest()` hashes the **decompressed** canonical jsonl stream, never the `.gz` file, and a
test enforces it: two archives written with different gzip mtimes have different file digests and
the same stream digest. Item 2 of the order (re-issuing the G-1 provenance table) is codex_1's.

## Tests

- `python3 claude_1/pipeline/test_fuzz_panel.py` — **166 tests, OK** (163 before, +3).
- `python3 claude_1/pipeline/test_p4b_gate.py` — **9 tests, OK** (6 before, +3).

## Named limitations

1. `--p4b-baseline` takes an **archive**, not a second panel run: the differential compares this
   run against a stored arm. Comparing two live runs means running the panel twice and passing
   the first's `games.jsonl.gz`.
2. A run with no `games_dir` has no archive to name; the packet then labels its source
   `(panel rows, not archived)` and still publishes the stream digest, so the evidence is
   reproducible but not re-readable from disk.
3. **K-5 is reported, not asserted**, in the embedded packet: a 6-map panel is a smaller panel,
   not a K-5 failure, and the control row says which it was. The G-1 CLI's assertion behaviour is
   unchanged.
4. The flag does not, and by this order must not, change the aggregate verdict. Nothing in the
   panel refuses a run whose P4b arm is `GATE_UNREADY`; a charter that wants that has to say so.
