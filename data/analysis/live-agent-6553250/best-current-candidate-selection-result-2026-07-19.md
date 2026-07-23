# Best current submission candidate — selection result 2026-07-19

## Verdict

The best supported upload-ready source is the **existing pre-seed + secure-orchard-coverage slim
resident**, SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

No different challenger currently clears it.  Preparing the best candidate therefore produces an
exactly verified resident artifact rather than a speculative policy change.  No Arena submission
was made.  Resubmitting this exact file would reset the agent's rating without changing strategy,
so it is only justified by a later explicit deployment instruction.

## Actions executed

1. Froze a prospective selection protocol before final revalidation.
2. Rechecked resident identity: agent `6560353`, submission `41012883`, byte-exact saved source.
3. Inventoried 237 standalone Rust sources: 194 are within 100,000 bytes, 57 are candidate-prefixed,
   and five are diagnostic-prefixed.  The complete per-file size, checksum, sidecar, class, and
   selection-status ledger is saved in
   `best-current-candidate-artifact-inventory-2026-07-19.tsv`.
4. Checked all 61 available SHA sidecars; none mismatched.  Missing sidecars on 176 legacy or
   diagnostic files keep those files out of an upload-ready classification unless separately
   regenerated and requalified.
5. Reconstructed the evidence hierarchy from local, controlled-field, and Arena verdicts.
6. Compiled all six high-evidence cohort artifacts standalone as Rust 2021 with `-D warnings`.
7. Compared the historical rank-6 Yamo policy with the promoted resident using normalized
   same-source controls, not transient peak rank.
8. Regenerated the locked slim transformation in tests: all three focused tests passed.
9. Replayed the selected 62,725-byte source against its exact 90,547-byte strategy parent on 60
   paired seeds.  All 60 tied with zero delta in score, wood, and every command category.
10. Selected and packaged the sole remaining eligible policy.  No platform mutation followed.

## High-evidence cohort

| Policy | Bytes | Strongest evidence | Decision |
|---|---:|---|---|
| Pre-seed + orchard resident | 62,725 | Healthy controlled Arena promotion: +3.0 to +3.3 over exact-parent bracket; slim A/A passed | **Select** |
| Original rank-6 Yamo/Orchard | 62,311 slim | Historical 26.3 peak; later healthy same-code bracket 20.8--21.1 | Superseded by controlled promotion |
| CompactGold rollout | 90,643 | 120-game Arena result 21.7 vs 24.1 control | Reject, -2.4 rating |
| Opponent-crop `b100_e6` | 64,522 | 160-game candidate 24.89 vs 24.77 control | Closed: +0.12 did not satisfy frozen +0.5/180-game rule |
| Opponent-crop dual value | 64,536 | Arena 16.51 vs 24.28 resident | Reject, -7.77 rating |
| Norxondor three-worker | 21,798 | Top-five controlled field panel | Reject: failed own score, margin, and worker-three gates |

The neural curriculum is excluded from this table because it has no submission inference layer,
active-opponent validation, timing/package integration, or live transfer result.  Its strong
waiting-opponent curriculum scores remain research evidence only.

## Why the historical rank 6 does not win

Agent `6553250` reached rank 6/104 at 26.3 with the original Yamo/Orchard source.  Its immediate
same-source restore occurred during degraded matchmaking and fell to 16.1/19.9, so neither side of
that reset is a valid causal comparison.  The later healthy A/A is decisive: the original policy
reconverged at 20.8--21.1, then the frozen pre-seed/orchard candidate reached 24.1 on two mature
reads after 161 games and later 24.4.  Its behavior-identical slim packaging subsequently closed
at 24.2 against a 24.5 full-size bracket, inside the frozen noise band.

Local paired evidence agrees but is subordinate to that Arena result: the promoted strategy gains
4.025 mean margin and 0.5715 wood over the original parent across 1,000 seeds.  Later live
position changes are volatile field snapshots and do not overturn the controlled promotion
history.

## Final artifact

- upload source:
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`;
- size: 62,725 bytes; headroom: 37,275 bytes;
- SHA-256:
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- full behavior reference:
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs`, 90,547 bytes,
  SHA-256 `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`;
- historical rank-6 comparison:
  `cgauto/submissions/agent-6553250-yamo-orchard-live-slim.min.rs`, 62,311 bytes,
  SHA-256 `025468a87d1807a6027f8af4c1662dfc89beb68b9fe0ef9ed1047fadf39c218f`;
- historical rank-6 full reference:
  `cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs`, 90,133 bytes,
  SHA-256 `09fac1fefa24eac657dba16a75d802eee38e1269f4aa44413e1ca103df36fe7a`.

## Reproducibility anchors

- frozen selection protocol:
  `6b85ba3aa061f7d73a2acdd0409a499379fe3138d081074c7e1aae7f46fa1ddc`;
- complete 237-source inventory:
  `474ddfc1cca9769a6e70d75253cc960ee3c79188471aa5790e7401dbe92fed86`;
- fresh 60-seed slim-parent parity:
  `6c92c5ed171c53f533758ffd232b07b173813bd4d894ddf522f343c8fe29ca91`;
- resident promotion and packaging evidence:
  `arena-retry-2026-07-17.md`;
- rejected rollout evidence:
  `compact-gold-rollout-arena-verdict-2026-07-18.md`;
- opponent-crop evidence:
  `opponent-crop-phase21-arena-verdict-2026-07-19.md` and
  `opponent-crop-dual-value-arena-verdict-2026-07-19.md`;
- three-worker field evidence:
  `norxondor-three-worker-controlled-field-result-2026-07-19.md`.

## Next boundary

Selection is complete.  A strategically new submission requires a new candidate that clears this
resident, not a resurrection of a rejected artifact.  Uploading the selected exact resident or
starting a new controlled challenger trial remains a separate explicit action.
