# Data-footprint cleanup — design

Date: 2026-07-24
Status: approved design, pending implementation plan

## Problem and audit findings

Local repository footprint is ~23.5 GB, of which ~83% is reproducible cache, not research
data:

| Consumer | Size | Nature |
|---|---:|---|
| `rust/target/debug` | 11.6 GB | Cargo cache; rebuilt within hours of the 2026-07-23 cleanup by ~100+ D-series workspace bins |
| `.claude/worktrees` (22) | 7.9 GB | Stale agent worktrees, **all verified clean** (`status --porcelain` empty); one holds a 4.7 GB ignored `.venv` |
| `data/` | 1.85 GB | ~1.0 GB untracked bulk (5 KB–50 MB tier, 672 files) + 478 MB tracked replay corpus + 75 MB processed |
| `.venv` / `cgauto/profile` / `.git` | 0.87 / 0.38 / 0.10 GB | Active env; authenticated CG browser session (required for arena access); git history — all keep |

External `medium_data` = Seagate Backup Plus Portable 4.5 TB **USB** drive (label-addressed,
preflight-guarded per `docs/storage-policy.md`); holds the 4.9 GiB tranche-1 migration,
427 GB free. Migrated artifacts currently exist only on that one portable drive
(regenerable, but re-compute costs time).

YT (`watt`, `//home/delivery_ml/research/tarstars/troll_farm`): 0.94 GiB, 23 nodes,
142 chunks — seven closed-experiment corpora under `dataset_builds`, incl. one **empty dead
directory** (failed D144 first attempt). Account `delivery_ml`: 0.6% of 10 TiB disk,
21.9% of nodes. YT is healthy; no meaningful waste there.

## Decisions (user-approved 2026-07-24)

1. Remove all 22 clean worktrees (branches/refs untouched).
2. Delete `rust/target/debug` now; keep `release/`; add a standing ~10 GB cap rule to
   `AGENTS.md`.
3. Migrate the ~1.0 GB untracked `data/analysis` + `data/panels` bulk tier to
   `medium_data` now, by the established copy-verify-symlink protocol (tranche 2).
4. Add targeted bulk-extension ignore rules under `data/analysis` for git-status hygiene.
5. YT: remove the dead empty D144 first-attempt directory; **keep** the six real corpora as
   remote backup; **add** a consolidated tar mirror of the migrated USB tranches under the
   YT root.

Out of scope: `data/raw` path split (policy explicitly defers it); deleting worktree
branches; `cgauto/profile` and `.venv`; any arena or resident interaction.

## Design

### 1. Worktree removal (~7.9 GB)

For each of the 22 non-main worktrees, in one pass: re-verify `git -C <wt> status
--porcelain` is empty; if empty, `git worktree remove <wt>` (NO `--force` — git itself
re-refuses dirty trees; ignored caches like the stale `.venv` do not block and are deleted
with the tree). Any refusal: stop on that worktree, show the blocker, decide with the user.
Then `git worktree prune`. Post-conditions: `git worktree list` = main only;
`git branch --list 'worktree-agent-*' | wc -l` unchanged from before.

### 2. Debug-cache clean + cap rule (~11.4 GB)

`rm -rf rust/target/debug` only; `rust/target/release` (179 MB) stays because
`libtroll_farm.so` serves the Python ctypes/RL tests. Append to `AGENTS.md` storage
section:

> `rust/target` is a disposable cache. At session end, if it exceeds ~10 GB, delete
> `rust/target/debug`; keep `rust/target/release`, whose `libtroll_farm.so` serves the
> Python ctypes tests.

Post-conditions: `libtroll_farm.so` exists; one RL env test file passes.

### 3. Bulk migration tranche 2 (~1.0 GB → `medium_data`)

Boundary: `git ls-files --others --exclude-standard` under `data/analysis` and
`data/panels`, **regular files only** (excludes the 34 tranche-1 symlinks), excluding any
file modified in the last hour. Procedure per `docs/storage-policy.md`:

1. `python3 cgauto/check_external_storage.py --required-free-gib 5`; confirm no running
   experiment process.
2. Build the file list + local SHA-256 manifest.
3. `rsync -aHXS --files-from=<list>` into
   `/media/tarstars/medium_data/database/troll_farm/artifacts/legacy-data-analysis/`
   (path-preserving, same root as tranche 1).
4. Verify: file count and byte totals match; every destination SHA-256 matches; a second
   checksum `rsync --dry-run` reports zero transfers.
5. Atomically replace each local file with a symlink to its external path; re-read a
   sample (≥32 files) through the repo paths with matching hashes; `sync -f` the volume.
6. Durable digest list → `docs/storage-migration-2026-07-24.sha256`; append an adoption
   paragraph (counts, bytes, free space) to `docs/storage-policy.md`; commit both.

### 4. Git-status hygiene

Append to `data/.gitignore`: `analysis/**/*.tsv`, `analysis/**/*.pt`,
`analysis/**/*.npz`, `analysis/**/*.npy`, `analysis/**/*.bin`, `analysis/**/*.tar.gz`,
`analysis/**/*.maps`. Tracked files are unaffected by ignore rules; `*.json`/`*.md` stay
visible so new compact results still show up as untracked until committed. Expected:
`git status` noise drops from ~672 lines to ≲50.

### 5. YT operations

- Remove `//home/delivery_ml/research/tarstars/troll_farm/dataset_builds/`
  `d144a_two_intervention_mc_9844128_9844135_20260722` (recursive; contains only the empty
  first-attempt tables). Verify the `repair1` sibling remains.
- Mirror (after tranche 2 completes, so one archive covers both tranches): create
  `.../troll_farm/mirrors/`; build
  `legacy-data-analysis-2026-07-24.tar.gz` from the external
  `artifacts/legacy-data-analysis` tree (~6 GiB raw, TSV-heavy so ~1.5–2.5 GiB
  compressed); record its SHA-256; upload archive + `.sha256` sidecar with MD5-verified
  write; read back size/attributes. ~3 new nodes. Record the paths and digest in the
  `docs/storage-policy.md` adoption paragraph.

### 6. Verification (whole cleanup)

- `df /` gains ≈19–20 GB; local repo ≈3.2 GB.
- `git worktree list` = 1; branch count unchanged.
- `rust/target` ≈ release only; RL test passes.
- All migrated paths resolve through symlinks with matching hashes.
- YT: dead directory gone, `mirrors/` holds archive + sidecar, corpora untouched; account
  usage change ≈ +2 GiB disk, +3 nodes / −2 nodes.
- Suites: Python suite unchanged vs the 2026-07-23 baseline (1,163 passed / 3 known
  pre-existing failures); no Rust source touched.

Execution order: 1 → 2 → 3 → 4 → 5 → verification → commits (AGENTS.md + gitignore +
manifest + policy append can share one commit; spec/plan committed separately).
