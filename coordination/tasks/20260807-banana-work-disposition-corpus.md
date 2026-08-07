# Banana work disposition — shared corpus definition (2026-08-07)

Owner-directed review of the whole recent banana effort. This file is the **single, shared
definition of what is under review**, referenced identically by both reviewer task records:

- `coordination/tasks/20260807-banana-disposition-review-chatgpt_1.md`
- `coordination/tasks/20260807-banana-disposition-review-local_codex_1.md`

Owned by `local_claude_1` (integrator). Reviewers must not edit this file. It exists so that two
independent reviews cover exactly the same ground and their verdicts are directly comparable.

## Deliverable, identical for both reviewers

One document: **what we should take from this work, and what we should discard.** Every corpus
item below gets exactly one verdict:

| verdict | meaning |
|---|---|
| `KEEP` | reusable as-is; state what it is good for |
| `KEEP_WITH_CONDITIONS` | reusable only after named, specific repairs |
| `DISCARD` | do not reuse; state the defect that kills it |
| `UNRESOLVED` | cannot be judged from committed evidence; state exactly what is missing |

Plus two required sections:

1. **Lessons that must survive even if the code does not** — findings, mechanisms, and
   measurement facts worth carrying into any future attempt, independent of any artifact.
2. **Costs and dead ends** — what consumed effort and returned nothing, so it is not repeated.

Rules: every quantitative claim must name the exact command and the SHA-256 of every input;
no verdict may be attributed to another agent without citing the exact message path; declare a
conflict of interest on any item you authored and mark those verdicts `SELF-AUTHORED` (they are
not disqualified, they are weighted and cross-checked against the other reviewer).

## A. Design layer — author `claude_1`

- `claude_1/banana-restoration-r2/design-banana-fsm-2026-08-06.md` (11-state FSM, 3 review
  rounds: `d3557f31`/`46588155` → `9369a4ec`)
- `claude_1/banana-restoration-r2/invariant-spec-2026-08-04.md` (29 invariants)
- `claude_1/banana-restoration-r2/integration-seam-2026-08-04.md`
- `claude_1/banana-restoration-r2/enumeration_manifest.py` + `enumeration-manifest.json`
  (1,594 rows, materialized after finding F8)
- `claude_1/banana-restoration-r2/conversion_race_oracle.py` (ASSET_SURVIVAL_ORACLE)

## B. Implementation lineage

claude_1 rounds, with the frozen verdicts already on record:

- `f29efd0e`, `280ed777`, `2f58edef`, `9f5ef833` — implementation-invalid, distinct
  lifecycle/oracle/reachability/liveness defects; red evidence files
  `red-evidence-*-2026-08-0{4,5}.md`
- `47c98f53` — withdrawn by the author pre-host after 141/240 fuzz blocks
- `eac2eb36` — round 6, 47/240, explicitly not a handoff
- `claude_1/banana-restoration-r2/build_banana_candidate.py`, `banana_blocks/block-i{1..6}.rs`,
  `research-banana-r2.rs`

chatgpt_1 solve arm:

- `bbe54a48…9951` (84,094 B) — handed off as valid; BLOCK 22/240 on the pinned panel
- `7ad9d784…fb49` — branch tip; BLOCK 89/240 (regression: D-4 35, D-7 35, D-9 24)
- `chatgpt_1/banana-solve/build_candidate.py` and `build_candidate_v2..v11.py`
- `chatgpt_1/banana-solve/candidate-banana-r2-manifest.json`, `generated/banana_blocks/block-i1.rs`

## C. Verification / gate layer — author `claude_1`

- `claude_1/pipeline/fuzz_panel.py` + `fuzz-panel-config.json` (+ `test_fuzz_panel.py`)
- `claude_1/banana-restoration-r2/test_trace_detectors.py`, `semantic_harness.py`,
  `regression_tests.py`, `make_banana_traces.py`, `detector-selftest-report-2026-08-04.md`
- `claude_1/pipeline/pre_review.py` (+ `test_pre_review.py`), `run_historical_validation.py`
- `gate-results-2026-08-04.md`, `gate-results-v2..v6`, `diagnosis-r5/r6`
- `gate-repair-report-2026-08-06.md`, `gate-repair-p4-report-2026-08-06.md` (P4 terminal-state
  calibration)
- `claude_1/pipeline/design-gate-redesign-2026-08-07.md` — **architecture reviewed separately**
  under `20260807-gate-architecture-review`; here give only a disposition verdict, do not redo
  that deep-dive

## D. Gate / contract layer — author `chatgpt_1`

- `chatgpt_1/banana-solve/gate-contract-v1.json` + `.md`
- `run_stable_gate.py`, `run_zero_oscillation_gate.sh`, `run_corrected_pinned.py`, `run_fuzz.py`
- `owner_contract_final.py`, `owner_contract_final_adapter.py`, `owner_contract_tests{,_v2,_v3}.py`
- `regression_adapter.py`, `analyze_pinned_attribution.py`
- trigger files `*-TRIGGER`, and the six `.github/workflows/chatgpt-banana-*.yml`
  (removed from the task branch at `f17d19cc`; four remain on `main`)
- the `ci/zero-oscillation-published/` CLEAR evidence — **cited but absent from the branch**

## E. Review and measurement record

- `local_codex_1`'s FSM design review (5 REVISION_REQUIRED items),
  `data/analysis/live-agent-6553250/banana-restoration-r2-fsm-design-review-2026-08-06.md`
- `chatgpt_1/banana-restoration-r2-fsm-design-rereview-2026-08-06.md` (10 findings) and
  `…-round3-review-2026-08-06.md` (4 blockers)
- `claude_1/banana-restoration-r2/fable-review-of-chatgpt1-solve-2026-08-06.md`,
  `fable-fuzz-reproduction-report-2026-08-06.md`,
  `fable-packet-review-of-chatgpt1-2026-08-06.md` (+ the two evidence JSONs),
  `fable-independent-design-review-2026-08-06.md`
- `local_claude_1/verification/README-floor-selftest-2026-08-07.md` — coordinator host run:
  parent judged against itself is **BLOCK 118/240**, D-1 = 35, D-4 = 6, D-2/D-3/D-8 = 0
- the m012 episode: coordinator endorsement withdrawn; **inherited parent behaviour**, chatgpt_1
  correct
- the fabricated `GATE_ACCEPTED` closeout and its consequences

## F. Earlier banana lineage — authors `chatgpt_1`, `local_codex_1`

- `cgauto/make_banana_factory_b100_candidate.py`, `make_banana_ring_b100_candidate.py`,
  `slim_banana_*`, `smoke_banana_ring_b100_candidate.py`,
  `validate_banana_ring_b100_candidate.py`, `analyze_banana_factory_b100_restoration.py`,
  `analyze_d89a_banana_seed_factory.py`
- `cgauto/submissions/candidate-agent6553250-banana*.min.rs` (supply-mother-first,
  supply-overlap-one, supply-pulse, banana5-geometry-portfolio, banana5-stack-portfolio)
- live implementation-invalid trials `6590083`/`41081195` and `6590136`/`41081465`
- `coordination/tasks/20260802-banana-ring-b100-successor.md`

## Standing constraints that bound every recommendation

- **Owner ruling 2026-08-07: raw `D-1 == 0` and `D-4 == 0`, no inherited-parent or
  aligned-prefix exemption, STANDS.** The owner accepts that the parent lineage must be repaired
  first. No recommendation may weaken this; flag incompatibilities instead.
- Owner intent for banana behaviour is unchanged (bounded self-reproducing orchard early, late
  fruit→wood, bank when we control it, never create opponent-harvestable fruit, second-worker
  funding first, carrier commitment persistence, no occupied-cell chasing, hysteresis).
- Parent is `a8eb3b2b…4e55`, 62,725 B. The sacred source
  `rust/src/bin/yamo_orchard_live.rs` (`fff6669b…`) is byte-untouchable.
- No candidate has ever earned value or Arena testing on this task.
