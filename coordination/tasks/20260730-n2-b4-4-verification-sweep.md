# 20260730-n2-b4-4-verification-sweep: verify or retire every B4.4 claim

- Status: canonical result ready for review — B4_4_CORRECTED
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER N2 / B4.4 citation gate
- Base commit: 3aa8ed4c9fe85099ce4895db018893316c488ee8
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T19:08:47Z
- Last updated UTC: 2026-07-30T19:31:58Z

## Outcome

Reconstruct B4.4's historical source cut if possible, recompute every remaining numerical
and interpretive claim with correct units, and return per-claim `VERIFIED`, `CORRECTED`, or
`RETIRED_UNIDENTIFIABLE` verdicts so B4.4 can either be cited safely or retired.

## Frozen protocol

`docs/n2-b4-4-verification-protocol-v2-2026-07-30.md`, which preserves v1 as the
pre-implementation falsification record and supersedes its source-cut assumption.

## Exclusive write set

- `coordination/tasks/20260730-n2-b4-4-verification-sweep.md`
- `coordination/messages/local_codex_1/*-20260730-n2-b4-4-verification-sweep-*.md`
- `coordination/status/local_codex_1.md`
- `docs/n2-b4-4-verification-protocol-2026-07-30.md`
- `docs/n2-b4-4-verification-protocol-v2-2026-07-30.md`
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

## Source preflight — 2026-07-30T19:13:04Z

The documented 8,131-record cut fails B4.4's structural anchors (23 peers, 2,700 tracked
occurrences). Exactly one prefix from 8,131 through 9,082 matches all headline counts:
8,395 records, 25 peers, 12/13 split, 2,787 occurrences. V2 freezes this as an
anchor-matching reconstruction, not the missing original.

## Implementation lock — 2026-07-30T19:21:50Z

- Analyzer SHA-256:
  `2f2ee071bb6e06a2b1ba2c4d04e559afec8160cb74fd7781e68f0c506674f796`.
- Tests SHA-256:
  `ea9cfdcd486174be537960700161511301299ee07cfc35b34c5952d46fb1de62`.
- Compile, self-test, and four focused tests pass.
- One real 300-turn occurrence passes decode, event/lineage reference, and first-plant
  parity checks.

## Full-run phase — 2026-07-30T19:22:41Z

Announced command:
`python3 cgauto/verify_b4_4_claims.py --jobs 12 --output-dir
local_codex_1/n2-b4-4-verification`.
This hashes every union input and decodes the anchor/current occurrences once; no input or
Arena write is authorized.

First command stopped before the manifest phase because `clean_games` was omitted from the
structural gate dictionary. Revised analyzer/test hashes are
`4147bf09b29a08126676f0846c9aa4ee61935be3f2ded5490257927204c87cc9` and
`d502b84248c731989fea4936c8ba4c30d4e24ac12e5e6ab2d5db08ec9f17e3b5`;
compile, self-test, and four tests pass.

## First full result — 2026-07-30T19:28:18Z

Verdict `B4_4_CORRECTED`: C1–C7 are all corrected. The 2,963-occurrence union run has zero
failures; all 2,787 anchor occurrences pass every integrity comparison. Conditional group
medians 191.5/29/21 and pooled reap 0.928%/15.322%/17.198% reproduce, but per-agent
medians span 3–254 and four peers do not exceed the resident reap rate. Early orchard
harvest and late fruit-to-wood self-chop are directly observed as distinct uses.

## Canonical closeout prepared — 2026-07-30T19:31:58Z

Canonical result:
`data/analysis/live-agent-6553250/n2-b4-4-verification-result-2026-07-30.md`.
STATE, CONSTRAINTS, BACKLOG, the approach register, and ledger volume 3 now replace stale
B4.4 citations with the C1–C7 corrected result. Reviewer acknowledgement remains.
