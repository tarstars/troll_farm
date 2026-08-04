---
type: HANDOFF
task_id: 20260804-orchard-code-cost-ablation
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-04T07:20:00Z
requires_ack: true
---

# Handoff: apple-orchard physical code cost = 15,013 bytes (23.9 % of source)

All deliverables are committed under `claude_1/orchard-code-cost/` on
`agent/claude_1-orchard-code-cost`.

## Headline

- Baseline: frozen live E7a, 62,820 bytes, SHA `97bfe71e…` (read-only, hash re-verified).
- Activation-disabled reference: 62,581 bytes, SHA `8fc1b7f3…` — one anchor-checked edit.
- Physically stripped: 47,807 bytes, SHA `102caecd…`.
- **Cost: 15,013 bytes / characters removed = 23.898 % of the baseline = 15.013 % of the
  100,000-character allowance.** Secondary (labelled): gzip −2,922 (−20.9 %), tokens −4,656
  (−22.4 %).

## Acceptance gates — all pass

1. Baseline hash exact; sacred source untouched (`fff6669b…` verified by the fixture
   harness); no formatter run.
2. Both artifacts: `rustc --edition=2021 -O -Awarnings` clean; empty input exit 0, zero
   output.
3. **Central gate — stripped vs reference: 25/25 games, 7,234/7,234 command lines
   identical** (`stripped-vs-reference-panel.json`).
4. Reference vs baseline: 24/25 identical; the sole difference is orchard-activation game
   `897833045` (vs viewlagoon, first divergent turn 79) — the exact intended semantic
   change (`reference-vs-baseline-panel.json`).
5. Fixtures: both artifacts `SEMANTIC_FIXTURES_EXACT_PASS` 10/10.
6. No orchard-only implementation remains (14-identifier residue check machine-enforced);
   shared infrastructure kept and inventoried: PredictedTree (general chop prediction),
   generic apple handling, chopping, banking, denial, the Bot trait,
   `opponent_eta_penalty`.
7. No Arena/TestSession action; write set respected.

## Deliverables

- `build_orchard_code_cost.py` — deterministic two-stage builder, anchor counts machine-checked.
- `activation-disabled-reference.rs`, `e7a-without-orchard-code.rs`.
- `orchard-code-cost-report.md` — plain-language report with the itemized inventory
  (state machine 97, geometry 124, timing 98, wrapper state 298, wrapper impl 10,241,
  turn-loop driver 3,373, reservation channel + main switch 782).
- `manifest.json` — all hashes, counts, exact commands, gate results.
- `run_equality_panel.py` + the four evidence JSONs.

Combined with yesterday's live ablation (−2.03 rating): the orchard costs 23.9 % of the
source budget and buys ≈2 rating points. Task complete on my side; release follows your
review.
