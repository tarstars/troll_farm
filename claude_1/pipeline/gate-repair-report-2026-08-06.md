# Gate repair: uniform RAW/ABSOLUTE attribution (2026-08-06)

Owner ruling: the standing acceptance gate (`fuzz_panel.py`) must be
**RAW/ABSOLUTE**. Every detector episode blocks, inherited-from-parent or
not, on every map. No parent-differential exemption, no
inherited-report-only, no aligned-prefix exemption.

## The two bugs (removed)

The pre-repair gate had two parent-comparison exemptions on candidate
blocking, plus a parent-based P4 clause:

- **(a) D-9 parent-differential** — `gate_d9_parent_differential()` +
  `eval_p1()`: a D-9 episode the parent reproduced byte-for-byte on the
  identical map/opponent was downgraded to a report-tier
  `inherited-parent-D9` flag (round-6 "ROOT-A" ruling). **Removed.**
- **(b) D-1 inherited-report-only** — `eval_p1()`: a D-1 episode on a map
  where the parent also oscillates was downgraded to an
  `inherited-parent-D1` flag. **Removed.**
- **P4 liveness parent clause** — `eval_p4()`: a candidate stall window was
  exempted *"unless the parent also makes no progress in the same window"*
  (inherited WAIT-equilibrium). This was P4's only exemption and it was
  purely parent-based; no absolute all-WAIT terminal state was ever
  recognised. **Removed entirely.**

D-2..D-8 were already raw (confirmed, kept). **P3** (orchard-eligible
byte-inertness) is an *absolute* requirement (candidate == parent commands
on orchard-eligible maps), not an exemption — **kept as-is**. Report-tier
flags (margin collapse, R-5 horizon) were never blocking — unchanged.
`trace_detectors.py`, map generation, seeds, and the oracle are unmodified;
the parent run is still computed (for the P3 inertness check and this
diagnostic) but never exempts a candidate detector episode.

### Edits (file : symbol)

- `fuzz_panel.py` : `eval_p1` — deleted `gate_d9_parent_differential` and the
  D-1 inherited branch; every `FAIL` among D-1..D-9 is now a P1 violation.
- `fuzz_panel.py` : `eval_p4` — deleted the parent-progress clause; every
  stall window blocks.
- `fuzz_panel.py` : `run_pair` — deleted the now-dead `inherited-parent-D1`
  / `inherited-parent-D9` report-flag emission.
- Module docstring + `fuzz-panel-config.json` `notes` updated to the raw
  rule.

### Tests (TDD)

`test_fuzz_panel.py` gained a `TestRawGate` class and an end-to-end
oscillator-vs-itself case, all of which were RED against the pre-repair
code and are GREEN after:

- `test_p1_d9_blocks_even_when_parent_reproduces_it` — D-9 blocks under raw.
- `test_p1_d1_blocks_when_parent_also_oscillates` — D-1 blocks under raw.
- `test_p4_blocks_when_parent_also_stalls` — a stall window the parent also
  stalls in blocks under raw.
- `test_exit_1_raw_gate_blocks_oscillator_vs_itself` — the planted
  oscillator run against **itself** as parent: CLEAR under the old mixed
  rules (D-1 inherited-flagged, all-stall P4-exempted), **BLOCK** under raw
  (D-1 + P4). No `inherited-parent-D1/D9` flag is ever emitted now.

Full suite: `python3 -m unittest test_fuzz_panel` → 22 pass;
`test_pre_review` → 24 pass.

## Diagnostic: the raw gate on parent + two chatgpt_1 candidates

Config: committed `fuzz-panel-config.json` geometry — 6 seeds × 120 maps ×
2 seats = **240 candidate games**, 200 turns each. Parent for all runs:
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
(sha256 `a8eb3b2b…`). Candidates fetched from
`origin/agent/chatgpt_1-banana-solve`:
`candidate-banana-r2.min.rs` content-sha `7ad9d784…` (branch tip) and its
earlier revision content-sha `bbe54a48…`.

### Raw failure counts (blocking games / 240)

| run (candidate) | RAW blocking / 240 | (old mixed-rule / 240) |
|---|---|---|
| **PARENT vs PARENT — the FLOOR** | **223** | 20 |
| chatgpt_1 `bbe54a48` | **217** | 22 |
| chatgpt_1 `7ad9d784` (tip) | **221** | 89 |

### Raw breakdown by property (games with ≥1 blocking violation)

| run | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| FLOOR (parent) | 114 | 4 | 0 | 200 |
| bbe54a48 | 111 | 4 | 0 | 192 |
| 7ad9d784 | 129 | 0 | 7 | 195 |

### Raw P1 breakdown by detector (games / episodes)

| run | D-1 | D-4 | D-5 | D-6 | D-7 | D-9 |
|---|---|---|---|---|---|---|
| FLOOR (parent) | 32 / 35 | 6 / 6 | 1 / 1 | 9 / 15 | — | 74 / 196 |
| bbe54a48 | 27 / 29 | 6 / 6 | 1 / 1 | 9 / 15 | 2 / 2 | 74 / 196 |
| 7ad9d784 | — | 35 / 46 | — | — | 35 / 67 | 74 / 176 |

(All three inherit the **same 74-game / ~196-episode D-9 funding-phase
signature** from the parent — exactly the episodes the old
parent-differential gate dropped.)

### Before/after (measurable effect of the repair)

| candidate | OLD mixed | RAW | Δ | driver |
|---|---|---|---|---|
| `7ad9d784` | 89 | 221 | +132 | P4 62→195 (parent no longer exempts stalls), P1 77→129 (D-9 inherited now blocks) |
| `bbe54a48` | 22 | 217 | +195 | P4 0→192, P1 18→111 (D-9 inherited now blocks) |

## KEY FINDING (the reframing)

**Under the raw gate the stable parent's own floor is 223 / 240.** Running
the parent *as the candidate against itself*, it fails raw on 223 of 240
games; only **17** games are clean. Decomposing the floor:

- **201 / 240** games block for a reason **other than solely D-9** — i.e.
  on P4 no-progress (200 games), P1 D-1/D-4/D-5/D-6 inner-policy
  oscillation, or P2. These are the parent's *own non-banana* behaviours.
- Only **22 / 240** games block *solely* on D-9 (the banana-funding-phase
  signature).
- **P4 (no own-inventory / own-cargo progress in a rolling 60-turn window)
  alone accounts for 200 / 240 games.**

A banana candidate that is behaviour-**inert** — byte-equal to the parent
on every non-banana-divergent map (the P3 dormancy contract) — therefore
**inherits the parent's ≥ 201 non-banana failures**, because on those maps
its commands *are* the parent's commands and the raw gate no longer exempts
the parent's oscillation or WAIT-equilibrium. The floor of 223 is a bound
no inert candidate can beat.

Consequently, **passing the raw gate is not achievable by inertness.** It
requires the candidate to *eliminate* the parent-family inner-policy
oscillation (D-1/D-4/D-6/D-7) and the no-progress WAIT-equilibrium (P4) —
not merely to avoid perturbing banana behaviour. The banana-specific work
(D-9, ~22 sole-D-9 games) is a small minority of what the raw gate now
demands; the dominant obligation is liveness/anti-oscillation across the
whole policy.

(The two live candidates land at 217 and 221 — *near but slightly below*
the 223 floor — precisely because they are **not** inert: they diverge from
the parent on some maps, trading a few of the parent's failures for others
of their own, e.g. `7ad9d784` replaces the parent's D-1 signature with a
D-4/D-7 one. Neither closes the P4/D-9 gap, so both remain ~90 % blocking.)

## Artifacts

Raw-gate reports/JSON (scratchpad `diag/`): `report-floor.md` /
`out-floor.json`, `report-bbe54a48.md` / `out-bbe54a48.json`,
`report-7ad9d784.md` / `out-7ad9d784.json`; old mixed-rule counterparts
`out-OLD-{floor,bbe54a48,7ad9d784}.json`.
