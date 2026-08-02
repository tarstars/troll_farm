# Git LFS shared-artifact migration plan

Date: 2026-08-02

Status: project-host and Claude-cloud capability PASS; Phase 1 started; no research dataset
uploaded at this checkpoint.

## Purpose

Give repository-only cloud agents selective access to a small set of immutable research
inputs while retaining `medium_data` as authoritative bulk storage. Git LFS is a shared
distribution mirror, not a replacement for USB/YT, a run-output store, or a backup.

Git LFS keeps pointer files in Git and stores the payload separately. GitHub Free/Pro
currently includes 10 GiB LFS storage and 10 GiB monthly download bandwidth; Team and
Enterprise include 250 GiB. Each file version consumes its full size and every download
uses repository-owner bandwidth. Before expanding beyond the pilot, verify the repository
owner's actual plan, current usage, and budget in GitHub billing.

References:

- <https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage>
- <https://docs.github.com/en/billing/concepts/product-billing/git-lfs>

## Non-negotiable boundaries

- Never run `git lfs migrate` or otherwise rewrite published history. The owner has already
  declined history rewriting, and experiment records cite exact commit hashes.
- Never delete or replace the authoritative USB source during LFS adoption.
- Never LFS-track broad extensions such as every `*.json`, `*.tsv`, or model file in the
  repository. Patterns are scoped beneath `data/shared-lfs/` only.
- Never upload secrets, sessions, browser state, sealed ranges, raw private credentials,
  or artifacts whose redistribution status is unclear.
- Do not repurpose `artifacts`, `outputs`, `yt_work`, `data/generated`, or `data/external`.
  They remain label-verified symlinks governed by `docs/storage-policy.md`.
- Ordinary clones skip automatic bulk download. Agents selectively pull only the named
  dataset required by their task.

## Phase 0 — capability and quota audit

`local_codex_1`, `claude_1`, and `chatgpt_1` independently report:

1. `git lfs version` and whether the repository LFS endpoint resolves, without publishing
   any credentials or headers;
2. recognition of a tiny probe as an LFS pointer;
3. a real upload on an agent-private branch;
4. a clean-checkout selective download of that object;
5. identical source/download SHA-256;
6. any authentication, quota, billing, client-version, or smudge error.

A version string, endpoint URL, repository push, or same-cache checkout alone is not a
pass. At least one non-host environment and the project host must prove actual upload plus
clean download before Phase 1.

Capability results are collected in `coordination/ENVIRONMENTS.md`. Probe branches and
private probe objects are evidence only and are not migration payloads.

Project-host result: PASS on 2026-08-02. Git LFS 3.0.2 converted the 90-byte probe to
pointer OID SHA-256 `527b8d3e10cc776ba9bedb4ec4cd7751b5234eb2f178f64e0cfa8d404da5d4f2`,
uploaded it successfully at commit `61f1118`, and a fresh standalone clone with smudge
disabled selectively downloaded byte-identical content. This clears only the host half of
the Phase-0 gate.

Claude-cloud result: PASS on 2026-08-02. After installing Git LFS 3.4.1, Claude uploaded a
551-byte probe at commit `d98dc4e`; an independent smudge-disabled clone selectively pulled
it with exact SHA-256 `6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a`.
The same clone pulled the host probe and reproduced its published hash. This clears the
non-host half of Phase 0. ChatGPT's separate environment probe remains pending but does not
block the pilot.

## Phase 1 — 82.8 MB D172 corpus pilot

The first pilot is the existing exact D172 option corpus, because it is immutable, compact,
checksum-locked, and directly useful to H10a/H10b. The four source shards are:

| Source path beneath `artifacts/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `experiments/d172a-dense-counterfactual-option-policy/corpus/d172a-corpus.shard-9860000-9860127.tsv` | 20,862,015 | `e9d46b5e3411d94be2df14935971a7f3cec6799069b9db35ad0575bb880aab51` |
| `experiments/d172a-dense-counterfactual-option-policy/corpus/d172a-corpus.shard-9860128-9860255.tsv` | 20,608,837 | `82541a97a714e5115735e83b49988ef25f7c92721efc5bfc16aad07fd7d499ad` |
| `experiments/d172a-dense-counterfactual-option-policy/corpus/d172a-corpus.shard-9860256-9860383.tsv` | 20,642,952 | `d0a79ea73867a793a5ed6bbf55a092e6b8f6ab13cd760ad495163bc1f466ba6c` |
| `experiments/d172a-dense-counterfactual-option-policy/corpus/d172a-corpus.shard-9860384-9860511.tsv` | 20,710,455 | `bd83cf3188b3597d8eb864adc68a7893745855a09eda2aed38285664a159b630` |

Total: 82,824,259 bytes and 79,997 rows. Canonical metadata is
`data/analysis/live-agent-6553250/d172a-dense-counterfactual-option-policy-corpus-manifest.json`.

Destination:

```text
data/shared-lfs/d172a-option-corpus/
```

Procedure:

1. Run `python3 cgauto/check_external_storage.py --required-free-gib 1` and resolve
   `medium_data` by label.
2. Recheck all four source sizes and SHA-256 values against the canonical manifest.
3. Create the destination and a narrowly scoped `.gitattributes` rule for the four TSV
   payloads; keep README/manifest/checksum text in ordinary Git.
4. Copy before any deletion. Compare regular-file count, apparent bytes, individual hashes,
   and aggregate sorted checksum digest.
5. Verify the Git index contains LFS pointer text while the working tree retains payloads.
6. Commit and push the migration branch once. Stop without retry on any LFS auth/quota or
   ambiguous upload result.
7. A remote agent uses a clean checkout with smudge disabled, selectively pulls only this
   dataset, and republishes file count, bytes, and hashes.
8. Integrate only after remote parity. The original USB files remain unchanged afterward.

## Phase 1 acceptance

- Four source and four downloaded regular files.
- Exact total 82,824,259 apparent bytes.
- All four SHA-256 values exact.
- Git objects are LFS pointers, not embedded TSV blobs.
- At least one clean non-host download passes.
- No unexpected LFS objects, broad attribute matches, ordinary-Git history growth, source
  deletion, symlink change, or secret output.

## Phase 2 — possible H10a/H10b inputs

Only after the pilot and a quota review:

- publish the future deduplicated 72-channel H10a table (estimated 477,278,208 bytes) once
  its exporter and exact tensor manifest are frozen;
- consider a compact L1 primitive corpus and final reusable model checkpoints;
- keep intermediate checkpoints, simulation matrices, raw trajectories, per-run dumps,
  profiler captures, and YT payloads off LFS.

Each Phase-2 dataset requires its own content manifest, access purpose, size/bandwidth
estimate, retention rule, and clean-cloud verification. No rolling “upload everything useful”
authority follows from the pilot.

## Failure and recovery

On probe, upload, quota, checkout, or checksum failure: stop, preserve the USB copy and
compact evidence, and do not integrate the pointer commit. LFS objects already uploaded may
remain billable even if a branch or pointer is removed, so repeated trial uploads are
forbidden. Fallback distribution options are a checksummed release/object-store artifact or
task-specific YT export; neither is authorized by this plan alone.
