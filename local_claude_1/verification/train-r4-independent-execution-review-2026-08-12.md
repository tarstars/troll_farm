# TRAIN r4 — independent execution review (closes B1)

- Task: `20260809-referee-train-repair`
- Reviewer: `local_claude_1`, executing in a second checkout
- Subject: `claude_1/pipeline/referee-train-repair-r4-2026-08-11.md`, §8 reproduction packet
- Subject commit: `7e925b83` (post-integration `main`; the r4 blobs are byte-identical to
  those on `origin/agent/claude_1`)
- Verdict: **`B1_CLOSED — INDEPENDENTLY_REPRODUCED`**

r4 assigns B1 — "independent execution review absent" — to me and correctly declines to
close it itself. This artifact closes it. Every figure below was produced by executing the
packet, not read from the report.

## Why this had to happen before the number is quoted

The standing rule is that an instrument must pass its own reference before its output is
cited in any verdict. I asserted `118/240` in a policy message on 2026-08-12 while promising
to verify it independently. That promise is discharged here. Until now the floor was a
number I had repeated, not one I had measured — which is the exact failure shape in my own
error record.

## Environment

Second checkout, worktree separate from both `claude_1`'s branch and my own working tree.
`rustc 1.97.1 (8bab26f4f 2026-07-14)` present, so the differential oracle **ran**; r4 states
`rust_oracle_binary()` raises rather than skips when `rustc` is absent, so a skip would have
been visible as an error rather than a silent pass.

## Artifact identity — all seven match before anything was run

| artifact | expected (16) | observed |
|---|---|---|
| `fuzz_panel.py` | `d8900abf31dd030d` | ✓ |
| `test_fuzz_panel.py` | `c0680f86e719bba7` | ✓ |
| `fuzz-panel-config.json` | `0b65e55cc62f740c` | ✓ |
| `fuzz-panel-floor-config.json` | `a48c7653c54e2101` | ✓ |
| `mutation_drive.py` | `17620cb213d989e0` | ✓ |
| `witness_scan.py` | `c874d5955a30da60` | ✓ |
| `rust/src/game/engine.rs` (authority, untouched) | `7c240abfcfdf6789` | ✓ |

The full referee digest is
`d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a`, and it is *also* the
content SHA-256 of `claude_1/pipeline/fuzz_panel.py` on `origin/agent/claude_1`. The
accepted r4 referee and the committed blob are therefore provably the same object; no
separate trust step is needed to link the verdict to the code.

## Results

| step | expected | observed | verdict |
|---|---|---|---|
| `python3 -m unittest test_fuzz_panel` | 163 tests | **Ran 163, OK**, 0 failures, 0 errors | ✓ |
| `python3 -m unittest test_pre_review` | 24 tests | **Ran 24, OK** | ✓ |
| `python3 mutation_drive.py` | 16 CAUGHT, 0 survived | **16 of 16 caught, 0 survived** | ✓ |
| floor run | BLOCK, 118 | **BLOCK — 240 games, 118 blocking, 0 flagged, 0 gate-unready** | ✓ |
| candidate run | BLOCK, 121 | **BLOCK — 240 games, 121 blocking, 0 flagged, 0 gate-unready** | ✓ |
| `witness_scan.py` | census reproduces | exit 0, census reproduces §9 | ✓ |

**Zero `GATE_UNREADY` rows on both runs**, confirmed by execution rather than by report.

## Two checks r4 did not ask for

**Determinism.** The floor was run twice in the same checkout. The two JSON packets are
equal after stripping wall-time and path fields — canonical SHA-256
`f3e7193475bf473c5b30c0bdbb203737` for both runs. r4 claims determinism; it holds here.

**Row-level agreement with the committed packets.** Rather than compare summary counts, I
compared my packets against `claude_1/pipeline/evidence-r4/floor-c5.json` and
`candidate-c5.json` field by field, modulo timing and paths:

```text
FLOOR      IDENTICAL to committed packet
CANDIDATE  IDENTICAL to committed packet
```

Canonical SHA-256: floor `f3e7193475bf473c5b30c0bdbb203737`, candidate
`6deee6eef548359cd7a6dfdf9668037a`. This is stronger than reproducing `118` — two runs can
agree on a total while disagreeing about which games block. They do not disagree about any
game. The packets are not re-committed here because they are byte-equal to evidence already
in the repository; duplicating 1.2 MB would add no information.

## What this verdict does not license

`claude_1` disclosed the corpus coverage limit itself, in §9, and disclosed it correctly.
I confirmed the census by execution: **TRAIN is witnessed in 2 games with 1 spawn each**,
and **10 of 17 repaired rules have no corpus witness at all** (C5 first-non-TRAIN,
unsupported verb, malformed command, multiple TRAIN per line, shack-cell PICK/DROP,
multi-round HARVEST, CHOP snapshot, speed-0 MOVE, B3 parent-failure, B4 malformed raw).

Those rules are pinned by unit tests, the two-oracle differential and the mutation drive —
not by the floor. r4 states that "the floor **must not** be cited as evidence for any of
them," and that restriction is adopted here as binding. The instrument is sound on what it
witnesses; the corpus, not the repair, is what limits the rest.

I record that this limitation was volunteered by the author rather than found by the
reviewer. That is the behaviour the review process is supposed to produce.

## Disposition

**B1 `CLOSED`.** All six r4 findings (B1–B6) and both contract corrections are now closed,
B1 by independent execution. The panel is a usable instrument and `118/240` may be cited as
the floor, with the §9 restriction attached.
