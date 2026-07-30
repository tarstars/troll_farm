# N2 — B4.4 verification sweep protocol v2

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T19:13:04Z
- Base commit: `f5689063ed8a555f1a1b7fde7b1cfe1edd72d8a8`
- Supersedes:
  `docs/n2-b4-4-verification-protocol-2026-07-30.md`
- Reason: pre-implementation source validation falsified v1's 8,131-record primary-cut
  assumption and identified one unique later prefix matching every published structural
  anchor

All v1 sections remain binding except §2 and the source-related gates in §5, which are
replaced below. V1 remains immutable evidence of the preregistered falsification test.

## 2. Frozen source identity — corrected

The original B4.4 JSON report was ephemeral and is absent. The tracked commit-`46d36098`
stats file records 8,131 parsed games, but direct reconstruction of the first 8,131 records
produces only 23 cohort peers (12 strong, 11 peer/weak) and 2,700 tracked occurrences. It
therefore cannot be the input cut behind the published B4.4 anchors.

An exhaustive prefix scan from record 8,131 through the current 9,082-record file found
exactly one prefix reproducing the jointly published structural anchors of 25 peers,
12 strong, 13 peer/weak, and 2,787 tracked occurrences:

- first **8,395** newline-delimited records of
  `/home/tarstars/prj/troll_farm/data/processed/games.jsonl`;
- game IDs 891153730–896651751 inclusive;
- 8,336 clean games;
- 204 resident occurrences with mean and median final roster exactly 2;
- prefix SHA-256
  `1f9e3855fad01f5ade6dd1ece17f0e6b20597d0b01889ef5240ee27700b68d40`;
- the v1 historical leaderboard and its SHA remain unchanged.

This is the primary `ANCHOR_MATCHING_RECONSTRUCTION`. It is stronger than an arbitrary
current-data rerun but is not the missing immutable original. The analyzer must report both
facts: the tracked 8,131-game provenance conflicts with the B4.4 output, while the 8,395
prefix is a unique output-anchor reconstruction.

The 8,131 documented-stats cut remains a required provenance sensitivity, using the v1
prefix SHA. The full 9,082-record current sensitivity and all other v1 source hashes remain
binding.

The exact exhaustive-prefix audit must be implemented and independently testable. Matching
only the occurrence total is insufficient: all cohort counts, rank spans, resident roster,
clean-game count, and game-ID boundaries must be reported. The 8,395 cut upgrades to
`ANCHOR_MATCHING_RECONSTRUCTION` only if required raw/trajectory decode coverage is 100%;
otherwise replay-dependent claims are retired individually.

## 5. Corrected provenance gates

- Failure of the 8,131 cut to reproduce B4.4 is a verified provenance discrepancy and must
  appear in C1; it does not automatically suppress the uniquely matching 8,395 audit.
- C1 can be no stronger than `CORRECTED`, because the original output and exact original
  input manifest are absent even if the inferred cut matches all published anchors.
- C2–C5 can be `VERIFIED` only as claims about the anchor-matching reconstruction and
  current sensitivity; their report text must not call the reconstruction the original.
- If no exact 8,395 raw/trajectory manifest or 100% decode exists, claims requiring those
  sources are `RETIRED_UNIDENTIFIABLE`.
- C6 current-code facts may be verified from byte-identified source, but any statement
  about what exact historical source generated the field behavior remains limited by
  missing source provenance.
- All denominator, per-agent, purpose, sensitivity, output, and Arena rules in v1 remain
  unchanged.
