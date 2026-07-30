# 20260730-m1-rating-system-dynamics: recover the observable ladder update rule

- Status: running — first reproducible result DESCRIPTIVE_ONLY / PARTIAL
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER M1 / measurement and re-baselining
- Base commit: 0e839b547f135147f07d01f484ef5f99cda3883f
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T18:30:46Z
- Last updated UTC: 2026-07-30T18:50:54Z

## Outcome

Determine whether the seven immutable D61p snapshots identify the Legend score update rule
from observed battle outcomes. If identified, estimate how many net wins move an agent by
+1 score near the resident's current level; otherwise return a precise partial or
unidentifiable result and state what additional observation would resolve it.

## Frozen protocol

`docs/m1-rating-system-dynamics-protocol-v2-2026-07-30.md`. V2 supersedes the immutable
v1 after pre-implementation source validation corrected the duplicate-collection timing and
added the raw game's platform-reported `agents[].score` evidence.

## Exclusive write set

- `coordination/tasks/20260730-m1-rating-system-dynamics.md`
- `coordination/messages/local_codex_1/*-20260730-m1-rating-system-dynamics-*.md`
- `coordination/status/local_codex_1.md`
- `docs/m1-rating-system-dynamics-protocol-2026-07-30.md`
- `cgauto/rating_system_dynamics.py`
- `tests/test_rating_system_dynamics.py`
- `data/analysis/live-agent-6553250/m1-rating-system-dynamics-*`
- `local_codex_1/m1-rating-system-dynamics/**`

The integrator may update the canonical live documents and ledger only at closeout.

## Shared read-only paths

- The seven exact snapshot directories named by the frozen protocol under
  `data/raw/snapshots/`.
- Only raw game files explicitly referenced by those snapshots' `games.json` indexes.
- `chatgpt_1/n1_maturity_io.py` and the canonical N1 result bundle.
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, and
  `docs/APPROACH-REGISTER-2026-07-30.md`.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`.
- `data/raw/games/`, `data/raw/snapshots/`, or the 05:17 collection cron: read-only, exact
  indexed files only.
- Sealed map/game ranges, A2 artifacts, Arena/TestSession/submission surfaces.
- Peer-owned decision-evidence-index paths and `coordination/messages/chatgpt_1/`.
- Any repository outside this worktree.

## Deliverables

- Frozen source/inclusion/model/identifiability protocol.
- Deterministic analyzer with synthetic tests.
- Compact machine result and human report with source hashes and observation counts.
- A wins-per-+1 estimate with uncertainty if supported, or a precise identifiability
  verdict and minimum next-data requirement.

## Acceptance checks

- `python3 -m py_compile cgauto/rating_system_dynamics.py`
- `python3 cgauto/rating_system_dynamics.py --self-test`
- `python3 -m pytest -q tests/test_rating_system_dynamics.py`
- Analyzer verifies every consumed snapshot manifest and indexed raw-game SHA before use.
- Exact-agent intervals distinguish score changes, update-time advances, visible new
  battles, missing outcomes, and right/left censoring.
- No model may claim a per-game causal rule unless its inputs cover every battle in the
  scored interval and it reproduces held intervals within the frozen tolerance.
- Report separately: empirical interval response, candidate-rule fit, counterfactual
  wins-per-+1, and identification limits.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden; this task uses immutable local evidence only.

## Handoff

Commit containing analyzer, tests, compact result/report, exact commands and hashes;
`chatgpt_1` reviews identification, censoring, fit claims, and the decision consequence.

## First reproducible result — 2026-07-30T18:50:54Z

Source integrity passes over 8,014 hash-verified raw games. Of 329 internal score
transitions, 307 (93.31%) are outcome-complete across 45 agents, satisfying the pre-model
FULL source threshold. Rule recovery nevertheless fails: the best held-agent model is
Elo-like at MAE 0.477313 versus a 0.478583 zero-change baseline, far from both validation
gates. The next-epoch convention and exclusion of the July 21 snapshot also fail. Final
support is therefore PARTIAL, verdict `DESCRIPTIVE_ONLY`, and wins-per-+1 remains null.
