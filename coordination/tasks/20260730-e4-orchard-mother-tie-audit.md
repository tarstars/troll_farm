# 20260730-e4-orchard-mother-tie-audit

- Status: done — `KEEP_LEXICOGRAPHIC`; peer review pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER E4 / secure-orchard tie audit
- Base commit: 76d7ece67047fea814ec744bc28e0a7a676bb46d
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T22:05:35Z
- Last updated UTC: 2026-07-30T22:35:52Z

## Progress

- Claim/protocol published at `bcae0425375913cc6a09c1952f272d71c5502a64`.
- Analyzer SHA-256:
  `968ad30331f184a7c222b4811938f720647e82b00bda9fc354a7a6f8b51b437a`.
- Test SHA-256:
  `df6a5952f28588e73312aca4a18cfbdabc8aec36e7fbab4374826c22e9ae58c1`.
- Exact transform, 57/seat census, ten tied-seed registry, self-test, ten focused tests,
  and a seed-31/motion compile smoke pass.
- Implementation lock:
  `local_codex_1/e4-orchard-mother-tie-audit/implementation-lock.json`.
- First full jobs-8 computation wrote no result: all sentinels exposed the `motion`
  opponent's wall-clock and randomized-collection nondeterminism.
- Lock v2 adds a temporary child-only deterministic runtime without mutating any bot
  source. Eight `HashMap` probes and four complete repeat-control cells are exact:
  `local_codex_1/e4-orchard-mother-tie-audit/implementation-lock-v2.json`.
- Jobs-8 completes 152/152 rows with 16/16 exact sentinels and provisional
  `KEEP_LEXICOGRAPHIC` at weighted margin −0.0855. Full jobs-1 row-hash parity is pending.
- Jobs-1 matches jobs-8 in tied, sentinel, and delta row hashes; normalized payloads are
  exact after excluding only `jobs`.

## Result

- Mechanism: `ACTIVE_TIE` — 10/10 seeds, both seats, 6/6 families.
- Tied-panel margin delta: −8.55; exact 1,000-map weighted: −0.0855.
- Seat deltas: −7.667 / −9.433; family means all negative, worst −26.65.
- Verdict: `KEEP_LEXICOGRAPHIC`.
- Report:
  `data/analysis/live-agent-6553250/e4-orchard-mother-tie-audit-result-2026-07-30.md`.
- Manifest:
  `local_codex_1/e4-orchard-mother-tie-audit/manifest.json`.

## Outcome

Measure the one distinct live E4 tie: equal enemy-distance secure-orchard mother cells.
Reverse only the lexicographic secondary comparator, run the exhaustive tied-map choice on
reused seeds against the six fixed local opponents, and return the frozen verdict.

## Frozen protocol

`docs/e4-orchard-mother-tie-audit-protocol-2026-07-30.md`.

## Exclusive write set

- this task record;
- `coordination/messages/local_codex_1/*-20260730-e4-orchard-mother-tie-*.md`;
- `coordination/status/local_codex_1.md`;
- `cgauto/e4_orchard_mother_tie_audit.py` (new);
- `tests/test_e4_orchard_mother_tie_audit.py` (new);
- `data/analysis/live-agent-6553250/e4-orchard-mother-tie-audit-*` (new);
- `local_codex_1/e4-orchard-mother-tie-audit/` (new, compact);
- canonical approach register/BACKLOG/CONSTRAINTS/STATE/ledger only at closeout.

## Shared read-only paths

- Exact live source, simulator, map generator, six frozen opponent sources, and offline
  policy-league helpers.
- Existing secure-orchard coverage probe/result, X1/A2-0b, D171/D176, E2, and N4 records.
- Reused seeds and exact tied/sentinel lists in the frozen protocol.

## Do not touch

- Resident/dev source, submissions, existing runner/analyzer/result, raw games, external
  bulk roots, sealed/fresh/official/confirmation ranges, cron, TestSession, or Arena.
- Peer-owned N4/evidence-index paths.
- No formatter, persistent alternate source, selector fitting, threshold tuning, or second
  comparator.

## Acceptance

- Protocol gates and exact hashes reported without reinterpretation.
- Alternate source exists only in a temporary directory and differs at one comparator.
- Complete tied map × six family × two-seat coverage plus sentinel identity.
- Jobs parity, focused tests, compact result/report, and sacred-source verification.
- One frozen verdict; no candidate or Arena implication.

## Arena authority

No platform access or mutation.
