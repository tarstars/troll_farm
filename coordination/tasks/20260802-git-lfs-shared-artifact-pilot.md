# 20260802-git-lfs-shared-artifact-pilot

- Status: claimed — remote capability probes assigned; migration plan pending publication
- Record owner: local_codex_1
- Work owner: local_codex_1
- Integrator: local_codex_1
- Area: shared research storage / Git LFS
- Base commit: ed29c27c12239760b98269ad7c46bd9e2129bde2
- Branch: agent/local_codex_1
- Created UTC: 2026-08-02T05:58:45Z

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

