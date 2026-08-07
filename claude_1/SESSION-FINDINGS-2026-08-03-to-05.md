# Session findings digest — 2026-08-03 → 2026-08-05 (claude_1)

Purpose: context-flush-safe index of everything established in this working arc. Every claim
cites its committed artifact; this file adds no new facts. A fresh session resumes from:
`coordination/status/claude_1.md` (state), this digest (history), and
`python3 scripts/inbox_sweep.py --me claude_1 --fetch` (obligations).

## 1. Live resident and ladder facts

- Live resident = **round-36 simplified E7a**, 55,799 B, SHA `2caac7c6…`, behaviour-exact
  with live E7a; deployed after 0/516 panel + exact platform recovery; settled 22.81 /
  rank 32. (`claude_1/r36-submission/`, integrator arena messages 2026-08-04.)
- **Same-source ladder variance is ±1.2**: identical bytes scored 25.30@12 and 23.56@32;
  orchard-behaviour readings span 22.81–25.30, no-orchard 23.11–24.76 across 13 settled
  legs. → **Standing measurement rule: effects < 1.5 points are decided on paired
  development panels only; single ladder reads decide nothing in that range.**
  (`claude_1/r36-submission/complexity-vs-standing.md`, register v2.)
- Orchard live value: **indistinguishable from zero** on pooled evidence (the −2.03 ablation
  and +2 first-mature were single draws). Orchard keep/drop reopened but parked (no-churn).
  (`claude_1/hypothesis-register/HYPOTHESIS-REGISTER-2026-08-04-v2.md`.)
- Measured feature economics: orchard = 15,013 B (23.9 % of source)
  (`claude_1/orchard-code-cost/`); door-unblocking = 5,991 B (9.5 %) and changed **0**
  of 7,234 replayed commands — action paths never executed
  (`claude_1/door-unblocking-cost/`); replay-gate coverage of the bot = **79 % regions /
  80 % functions** (`claude_1/e7a-incremental-simplification/r36-coverage-analysis…`).

## 2. Hypothesis programme (owner-approved)

Register v2 order: **1 banana wood-printer (active) · 2 catastrophe/variance census
(unassigned) · 3 H3a denial (paused) · 4 H1 orchard gate (G1–G3 done, G4 dev-endpoints-only
queued with integrator) · 5+ as listed.**
(`claude_1/hypothesis-register/HYPOTHESIS-REGISTER-2026-08-04-v2.md`.)
H1 artifacts: frozen protocol + margins 0/−128/−256 + bridge-validated gate arms
(`claude_1/h1-orchard-gate/`).

## 3. Banana restoration (P1) — verdict lineage and open state

`f29efd0e` INVALID (no I-9 one-seed reservation; I-10a incomplete; no readable source) →
`280ed777` INVALID (growth-during-chop; D-8 vacuity) → `2f58edef` INVALID (scripted t5
masked unreachable flip response; three divergent deadline definitions) → `9f5ef833`
INVALID (225-turn full-carrier oscillation on host map 9,854,000 — articulation-cell
deadlock) → `47c98f53` **withdrawn by my own fuzz gate before verdict**
(correction `20260806T003000Z…`, supersedes the round-5 handoff).

Established assets, all under `claude_1/banana-restoration-r2/`:
- Invariant spec (29 invariants + revisions), 6-insertion seam with byte-exact inverse,
  **CONVERSION_RACE_ORACLE** (one named oracle drives spec/code/R-3/R-4/D-8 —
  `conversion_race_oracle.py`), detectors D-1…D-9, regressions R-1…R-5 each proven failing
  on the bytes that motivated them, semantic harness TIER-P/TIER-C, mini-referee with
  dynamic opponents, readable research source pipeline.
- Round-5 diagnosis worth remembering: the deadlock cause was
  `banana_forbidden={mother}` in movement-conflict resolution when the mother is the
  articulation cell of all door routes — NOT the protected-cell filter (refuted by probe).
  Mother protection = chop/plant-over/camp, **transit is legal**
  (`diagnosis-r5-2026-08-05.md`, `gate-results-v5-2026-08-05.md`).

**Open round 6 (next work):** fuzz corpus = 141/240 violating games in 7 families → 4 root
causes: (a) solo activation before second-worker funding (74 games, D-9); (b) residual
articulation-deadlock family incl. carrier-behind-mother (37 games); (c) fruit-safety at
contest (D-6, 29); (d) liveness stalls (24). Corpus + traces:
`claude_1/banana-restoration-r2/fuzz/`. Host cross-check map 9,854,000 stays in scope.

## 4. Coordination transport v2 — COMPLETE, Phase-3 mandatory

- v2 schema (exact-path `ack_for`/`supersedes`, canonical-completeness handoffs with
  `artifact_commit`), authoritative inbox (`scripts/inbox_sweep.py`, 41 tests), integrated
  by the integrator; **v2 is mandatory for new messages project-wide.**
- claude_1 legacy backlog: 28 paths audited and closed
  (`claude_1/legacy-backlog-audit-2026-08-05.md`); seen-state live
  (`claude_1/inbox-seen.json`).
- Publication convention: **work on task branches, but merge artifacts to canonical
  `agent/claude_1` BEFORE publishing the handoff message there.** A message pointing at
  unfetched task-branch content is not a delivery (learned twice).

## 5. Pipeline v2 — the process findings

- **Failure analysis of the four rejections:** only two classes ever repeated — vacuous or
  scripted evidence, and model divergence. Structural cause: implementation and tests share
  one imagination; local evidence surface ≈ 1 % of the host panel's.
  (`claude_1/PIPELINE-2026-08-05.md`.)
- **Mechanized enforcement** (`claude_1/pipeline/`): `pre_review.py` (trace provenance via
  compile-and-regenerate; single-model oracle audit; red-for-the-right-reason signature
  matching; claims coverage) — validated by retroactively BLOCKing the reconstructed
  round-3/round-4 states; `failure-ledger.json` (append-only classes, each citing the
  review that created it).
- **Fuzz panel** (`claude_1/pipeline/fuzz_panel.py`): 120 seeded maps × both seats,
  closed-loop candidate+parent, properties = all detectors + R-5 class + orchard-dormancy
  byte-inertness + parent-relative liveness; deterministic, 480 games ≈ 12 s. **First run
  blocked our own candidate (141/240)** — proof that random sampling beats imagined
  scenarios. Ledger class `UNSAMPLED_STATE_SPACE`. Runs last inside pre-review: no handoff
  ships while it blocks.

## 6. Operational lessons (cheap to forget, expensive to relearn)

- Verify file edits by grepping the result — a silent string-replace no-op left a stale
  status file visible to peers for a day.
- `git lfs checkout` does not smudge in a linked worktree even with object + attributes
  present; `git lfs smudge < pointer > file` does.
- rustfmt is not token-neutral (trailing commas, closure braces); the readable-source
  pipeline repairs its token stream (`claude_1/readable-source/format_readable.py`).
- The compactor is idempotent modulo one trailing newline; lineage files carry the newline.
- Subagent reports are drafts: every load-bearing claim gets independently re-verified
  (anchor counts, hashes, exit codes, and — since round 2 — reading traces against the
  invariant list by eye).
