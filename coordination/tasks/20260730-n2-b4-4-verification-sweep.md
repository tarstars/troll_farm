# 20260730-n2-b4-4-verification-sweep: verify or retire every B4.4 claim

- Status: claimed — protocol frozen; implementation not yet started
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER N2 / B4.4 citation gate
- Base commit: 3aa8ed4c9fe85099ce4895db018893316c488ee8
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T19:08:47Z
- Last updated UTC: 2026-07-30T19:08:47Z

## Outcome

Reconstruct B4.4's historical source cut if possible, recompute every remaining numerical
and interpretive claim with correct units, and return per-claim `VERIFIED`, `CORRECTED`, or
`RETIRED_UNIDENTIFIABLE` verdicts so B4.4 can either be cited safely or retired.

## Frozen protocol

`docs/n2-b4-4-verification-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-n2-b4-4-verification-sweep.md`
- `coordination/messages/local_codex_1/*-20260730-n2-b4-4-verification-sweep-*.md`
- `coordination/status/local_codex_1.md`
- `docs/n2-b4-4-verification-protocol-2026-07-30.md`
- `cgauto/verify_b4_4_claims.py` (new)
- `tests/test_verify_b4_4_claims.py` (new)
- `local_codex_1/n2-b4-4-verification/**`
- `data/analysis/live-agent-6553250/n2-b4-4-verification-*` (new)

The integrator may update canonical live documents and ledger volume 3 only at reviewed
closeout.

## Shared read-only paths

- Exact inputs and hashes in the frozen protocol under
  `/home/tarstars/prj/troll_farm/data/`.
- `cgauto/peer_cohort_analysis.py` and its imported analyzers.
- `rust/src/bin/yamo_orchard_live.rs` and historical Git blobs for code grounding.
- B4.4, H3, H5, and B4.6 records in canonical docs and ledger volume 2.

## Do not touch

- `cgauto/peer_cohort_analysis.py` or any imported historical analyzer.
- `rust/src/bin/yamo_orchard_live.rs`.
- `/home/tarstars/prj/troll_farm/data/raw/`,
  `/home/tarstars/prj/troll_farm/data/processed/`, and the collection cron: exact reads
  only.
- Sealed ranges, simulation/A2 artifacts, resident code, submission tooling, TestSession,
  or Arena state.
- Peer-owned decision-evidence-index and N4 paths.
- Formatters over `rust/src/bin/` or `cgauto/`.

## Deliverables

- Frozen reconstruction/claim protocol and remotely published claim.
- Deterministic analyzer and focused synthetic tests.
- Exact consumed-input manifest, historical/current machine results, per-agent tables, and
  compact human report.
- Canonical C1–C7 verdict table and citation-safe B4.4 replacement text.

## Acceptance checks

- `python3 -m py_compile cgauto/verify_b4_4_claims.py`
- `python3 cgauto/verify_b4_4_claims.py --self-test`
- `python3 -m pytest -q tests/test_verify_b4_4_claims.py`
- full analyzer command and output hashes recorded
- historical structural anchors and every input failure explicit
- resident sacred SHA unchanged and no source/input writes

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Push implementation, tests, exact commands, manifests, C1–C7 verdicts, and replacement
language. `chatgpt_1` reviews source reconstruction, units/denominators, semantic purpose,
and the retirement boundary before canonical integration.
