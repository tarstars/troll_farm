# 20260802-git-lfs-shared-artifact-pilot

- Status: active — Phase 1 uploaded; independent cloud parity pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Integrator: local_codex_1
- Area: shared research storage / Git LFS
- Base commit: ed29c27c12239760b98269ad7c46bd9e2129bde2
- Branch: agent/local_codex_1
- Created UTC: 2026-08-02T05:58:45Z
- Last updated UTC: 2026-08-02T06:19:18Z

## Owner directive

Test Git LFS status on the other agents, collect their answers, begin migration if remote
upload/download access exists, and preserve a durable migration plan.

## Outcome

Establish an environment-aware LFS capability matrix and, only after a remote agent proves
upload plus clean-checkout download, mirror one small immutable USB-backed dataset into a
new LFS namespace without rewriting Git history or deleting the authoritative USB copy.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- own immutable messages for this task and probe assignments;
- `local_codex_1/lfs-probe/` for one tiny host upload/download proof;
- `coordination/ENVIRONMENTS.md`;
- `docs/git-lfs-shared-artifact-migration-plan-2026-08-02.md`;
- a new `data/shared-lfs/` namespace and only its exact `.gitattributes`, manifests, and
  pilot files after the capability gate passes;
- compact migration evidence under `data/analysis/live-agent-6553250/`.

## Candidate pilot

The four immutable D172 option-corpus TSV shards total 82,824,259 bytes and 79,997 rows.
Their exact paths and hashes are frozen in
`data/analysis/live-agent-6553250/d172a-dense-counterfactual-option-policy-corpus-manifest.json`.
The `medium_data` preflight currently passes with 452,645,679,104 free bytes.

## Gates

1. At least one non-host agent must prove LFS upload and clean-checkout download with an
   identical probe SHA-256; version/endpoint inspection alone is insufficient.
2. The local host must prove the same capability before uploading the dataset.
3. Pilot size remains below 100 MB; stop without retry on quota, authentication, or pointer
   materialization ambiguity.
4. Preserve source count, apparent bytes, and every SHA-256 before and after copying.
5. Keep the USB source as authoritative; no source deletion or symlink replacement.
6. No `git lfs migrate`, force push, history rewrite, broad extension glob, or automatic
   smudge of unrelated LFS content.

## Prohibitions

No secrets or credential output, sealed data, raw-game mutation, Arena action, bulk
experiment, model fit, source change, USB deletion, or history rewrite.

## Plan checkpoint

- Durable plan: `docs/git-lfs-shared-artifact-migration-plan-2026-08-02.md`.
- Capability registry: `coordination/ENVIRONMENTS.md`.
- Project-host upload and independent clean-clone selective download PASS.
- Claude cloud upload and independent clean-clone selective download PASS at probe commit
  `d98dc4e`; Claude also downloaded the host probe with its published SHA-256.
- ChatGPT's probe remains assigned and unacknowledged; it no longer gates the pilot because
  the required non-host proof now exists.
- Source storage, four shard sizes, 79,997 data rows, and all four SHA-256 values were
  revalidated after a fresh `medium_data` preflight. Phase 1 copying may now begin.
- No research payload had been copied or uploaded at this checkpoint.

## Local capability result

- Git LFS 3.0.2 recognized the private probe as an index pointer.
- Push `61f1118` uploaded one 90-byte LFS object successfully.
- A standalone clean clone with smudge disabled selectively pulled the object from GitHub.
- Source/download SHA-256 is exact:
  `527b8d3e10cc776ba9bedb4ec4cd7751b5234eb2f178f64e0cfa8d404da5d4f2`.
- Verdict: `PROJECT_HOST_LFS_PASS`. The non-host gate is now cleared by Claude's PASS below.

## Non-host capability result

- Claude cloud installed Git LFS 3.4.1 and uploaded one 551-byte LFS object successfully.
- A separate smudge-disabled clone selectively pulled that object with source/download
  SHA-256 `6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a`.
- The same clean clone pulled the host object and reproduced SHA-256
  `527b8d3e10cc776ba9bedb4ec4cd7751b5234eb2f178f64e0cfa8d404da5d4f2`.
- Verdict: `CLAUDE_CLOUD_LFS_PASS`. The Phase-0 gate is open; ChatGPT remains a useful but
  non-blocking environment audit.

## Phase 1 upload checkpoint

- Four source and four copied files compare byte-for-byte and preserve the frozen hashes.
- The index contains four LFS pointers with OIDs equal to the four source SHA-256 values;
  `.gitattributes`, README, checksum list, and manifest remain ordinary Git blobs.
- Commit `bcbd5ca` uploaded exactly four objects, 83 MB reported, at 100% success in one
  push. Remote branch `agent/local_codex_1` resolves to that exact commit.
- The USB source is unchanged. Integration remains gated on a clean Claude-cloud selective
  pull and exact four-file/byte/hash parity.
