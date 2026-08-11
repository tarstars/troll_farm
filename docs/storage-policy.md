# Troll Farm Storage And Compute Policy

Date: 2026-07-23. **Amended 2026-08-11 (spec Phases 3–4): the USB is no longer live
infrastructure.** This adapts the proven `math_through_eml` external-storage policy to
Troll Farm. The normative short version is in `AGENTS.md`.

## Local bulk layout

The bulk roots are served by **whichever backend is present**, and both are legitimate:

| Backend | Identity | Writable | When |
| --- | --- | --- | --- |
| USB (ext4) | filesystem label `medium_data` | yes | only while the drive is attached |
| Cloud (GeeseFS) | mount source `troll-farm-data:archive` | **no** | the steady state since 2026-08-11 |

Both present the **same path**, which is why the repo's 2,346 absolute symlinks keep
working either way:

```text
/media/tarstars/medium_data/database/troll_farm
```

The USB is now an **offline backup**. Its contents were uploaded and verified on
2026-08-11 (3,483 files / 9.99 GiB, `VERIFY: PASS`, independently recounted) as a
**per-file mirror** under the bucket's `archive/` prefix — per-file, not packed,
precisely so the mount can serve these paths. Manifests live at `archive-manifest/`.
Note the drive also holds ~1.2 TB of unrelated personal data that this project does
**not** back up.

The following repository paths are the clean bulk boundary:

| Logical path | Purpose | Backing |
| --- | --- | --- |
| `artifacts` | Large experiment matrices, corpora, checkpoints, and raw telemetry | archive |
| `outputs` | Large run outputs and extracted bundles | archive |
| `data/external` | Downloaded or externally sourced datasets | archive |
| `yt_work` | YT payload staging and downloads | **local scratch** |
| `data/generated` | Regenerable generated datasets | **local scratch** |

The last two changed on 2026-08-11. Both held **zero files** on the USB — verified at the
Phase 3 upload, where the whole drive was 3,483 files and none were under either — and
both are *write* targets, which a read-only archive cannot host. They now point at
`~/.cache/troll-farm/`. Both symlinks were untracked, so no clone is affected.

These paths are ignored without trailing slashes so Git ignores either a
temporary real directory during a validated migration or the final symlink
object. In steady state, every **archive-backed** path must be a symlink resolving
beneath the physical Troll Farm root; the two scratch paths must be symlinks to
writable local directories and are deliberately *outside* it.

## Where new bulk output goes (owner decision, 2026-08-11)

**Local disk, then periodic upload** — the pattern collector v2 uses for games.

The mechanism is a **union by symlink**, not an overlay filesystem (which would have
needed a package install and, for kernel overlayfs, root). Each union root is a *real
local* directory under `~/.cache/troll-farm/bulk/` whose children link into the read-only
archive:

```
artifacts/                    real local dir
├── legacy-data-analysis  ->  mount   (history, read-only)
└── experiments/              real local dir
    ├── d175a-…           ->  mount   (history, read-only)
    └── <new experiment>      real local dir   <- new output lands here
```

History reads through the same paths as before, and a new experiment directory is simply
created. `artifacts/experiments` is itself a union dir rather than a link, because that is
the level at which new directories appear — a single link there would have left writes
failing, which is what the first dry run of the builder revealed.

- Refresh the layout: `python3 data/scripts/link_archive_roots.py --apply` — idempotent,
  manages only symlinks, and **never deletes a real directory**, because a real directory
  shadowing an archived name is the uploaded-but-not-yet-reclaimed state.
- Upload new output with `data/scripts/upload_archive.py` (idempotent head-and-skip on the
  recorded sha256, verifies what it wrote).
- Replace a local copy with a link to reclaim space **only after** its upload verifies —
  the same discipline by which collector v2 prunes staging only after re-downloading and
  re-hashing its pack.

The preflight enforces this: union roots are checked for **writability**, and
`--required-free-gib` is measured on the **local** filesystem where the bytes land. It is
deliberately not measured on the mount, which reports a fictitious 1 PiB free and would
have left the threshold silently unenforceable.

The existing `data/analysis`, `data/raw`, and `data/processed` directories are
mixed: they contain tracked or compact scientific records as well as legacy
bulk data. They are not a safe whole-directory migration boundary. Keep
compact protocols, manifests, hashes, aggregate JSON/TSV, and result Markdown
there. Route all new bulk output to the clean roots. Migrate historical large
files separately while preserving their old paths with links when a consumer
still needs them.

## Mandatory preflight

Before a write through any bulk root, run:

```bash
python3 cgauto/check_external_storage.py --required-free-gib <GiB>   # --intent write is the default
python3 cgauto/check_external_storage.py --intent read               # before a bulk READ
```

The command discovers whichever backend is present — USB by label first, else the
GeeseFS mount by source — and checks:

1. exactly one mount matches the backend's identity;
2. the physical project root exists on it;
3. every archive-backed repository path is a symlink resolving beneath that root, on the
   same backend;
4. every scratch path resolves to a writable local directory;
5. the requested free-space floor is available **when the backend is writable** — object
   storage reports a fictitious 1 PiB free, so the threshold is skipped rather than
   compared against a fiction; and
6. **the caller's intent is satisfiable**: `--intent write` fails closed on a read-only
   backend. This is the common case today, and it is correct — the write would fail
   anyway, later and messier.

The mount path is not the identity. If the device mounts elsewhere, the
preflight reports that observed path. If the backend or a link is absent, stop.
Never replace a missing link with a real directory on `/`, and never "fix" a
read-only failure by loosening the check.

## Safe migration procedure

Use the same copy-before-delete protocol as `math_through_eml`:

1. Resolve the mounted volume by label and confirm destination capacity.
2. Confirm no live writer and no recently modified file in the candidate
   boundary.
3. Copy with `rsync -aHXS`, retaining the source.
4. Compare source/destination regular-file counts and apparent bytes.
5. Require an itemized `rsync --dry-run --delete` to report zero changes.
6. Remove only the synchronized source, install the repo-relative symlink,
   and run the preflight.
7. Read representative artifacts through the repository path and flush the
   external filesystem with `sync -f`.
8. Record counts, bytes, checksums where useful, and measured free space.

Never migrate a mixed root wholesale merely to save time. Never delete an
artifact whose external copy has not passed the validation above.

## What stays where

Keep in the repository:

- Rust/Python source and tests;
- frozen submission sources;
- experiment protocols and decisions;
- compact configs, manifests, checksums, and operation metadata;
- aggregate metrics, analysis tables, figures, and result reports.

Keep on the bulk backend (the `archive/` prefix; historically `medium_data`):

- simulation arm/candidate matrices;
- replay-derived training corpora and raw trajectories;
- NumPy arrays, model weights, checkpoints, and profiler captures;
- raw prediction/episode dumps;
- YT payloads, runtime archives, and downloaded output bundles.

Treat `.venv`, `rust/target`, root `target`, pytest caches, and inactive
worktree environments as disposable local caches. They are not backups.

## YT policy

The canonical remote root is:

```text
//home/delivery_ml/research/tarstars/troll_farm
```

YT is compute and durable remote run storage, not a substitute for careless
local staging. Conserve Cypress nodes: prefer consolidated tables/archives,
canonical reusable inputs, compacted tables, and compact per-run metadata.
Run directories should reference shared data/runtime objects rather than
duplicating them.

Use YT for independent simulation/Monte Carlo shards, large evaluation
matrices, corpus construction, or neural training batches whose aggregate
local wall time is expected to exceed roughly one hour. Keep small controls
and smoke tests local. Neural workflows must pass their frozen local/YT
functional parity gate before backend results become selectable.

## Where heavy compute runs (owner rule, 2026-08-11)

YT (`//home/delivery_ml/...`) is reachable **only from `project_host`**. So:

- heavy batches launched from the workstation may use YT;
- anything cloud-side, or anything needed while the workstation is off, uses
  **preemptible** burst VMs — preemptible by default, never on-demand by habit;
- **no compute instances are created while the grant period is spent** (it was
  nearly exhausted at 2026-08-11; steady headroom is ~10,500 ₽/month). Storage
  costs tens of ₽/month and proceeds any time;
- quotas as measured 2026-08-11: **GPU is zero cloud-wide** — a support ticket and
  a grant-eligibility check come before ever requesting one — 28 free vCPU of 32,
  128 GiB RAM, 12 instances;
- every cloud mutation is announced before and after and logged like an Arena cycle.

## Adoption status on 2026-07-23

The first inspection found `medium_data` detached. The system filesystem had
about 96 MiB free, so safe cleanup removed the ignored, reproducible Cargo
targets from the main checkout and 22 clean registered worktrees. This
recovered roughly 50 GiB without changing source, branches, or research
artifacts.

After the volume was attached and the project root was provisioned with the
correct ownership, the five clean logical roots were installed as symlinks and
the live preflight passed. The first historical tranche is also complete:

- 34 untracked files larger than 50 MiB were frozen; none had a live writer,
  had changed within the preceding hour, or overlapped a Git-tracked file.
- Source count and apparent bytes were `34` and `5,121,892,121`.
- `rsync -aHXS` copied the path-preserving tree beneath
  `artifacts/legacy-data-analysis`.
- Destination count and apparent bytes matched exactly.
- Every per-file SHA-256 matched; the aggregate digest of the sorted checksum
  manifest is
  `4770c3bce6a51ba0c220396796056710505fa40a867fd77842332b9df5e707e0`.
- A checksum-enabled, itemized `rsync --dry-run --delete` reported zero
  changes before source replacement.
- All 34 local files were atomically replaced with links, then re-read through
  those links with identical hashes and verified `medium_data` targets.
- Final allocated size was `1,276,743,680` bytes for local `data/analysis` and
  `5,106,069,504` bytes for the external migration tree.
- Final measured free space was `311,745,933,312` bytes on `/` and
  `353,191,759,872` bytes on `medium_data`.

The durable per-file digest list is
`docs/storage-migration-2026-07-23.sha256`.

The post-cleanup local inventory was:

| Path | Apparent bytes | Regular files | Decision |
| --- | ---: | ---: | --- |
| `data/analysis` | `6,393,779,717` | `2,313` | Mixed root; migrate large files selectively |
| `data/raw` | `496,764,797` | `2,148` | Mixed tracked replay corpus; retain pending path split |
| `data/processed` | `74,638,547` | `1,698` | Mixed tracked/derived data; retain pending path split |
| `cgauto/profile` | `399,261,854` | `4,007` | Private browser/session state; never shared as an artifact |
| `.venv` | `863,077,844` | `18,718` | Reproducible local cache |
| `.claude/worktrees` | `8,175,556,231` | `59,221` | Registered branches retained after Cargo-cache cleanup |

The 34 files larger than 50 MiB accounted for `5,121,892,121` bytes and have
now been migrated. Compact sibling protocols/results remain local, and every
moved file retains its existing consumer path through a verified link.

The second historical tranche completed on 2026-07-24: 683 untracked regular files
(1,042,056,986 apparent bytes) from `data/analysis` and `data/panels` were copied to
`artifacts/legacy-data-analysis`, verified by count, bytes, and per-file SHA-256
(digest list: `docs/storage-migration-2026-07-24.sha256`), then replaced with
path-preserving symlinks and re-read through the repository paths. Free space after
`sync`: 456824188928 bytes on `medium_data`. A consolidated mirror of the whole
`legacy-data-analysis` tree was archived to YT as
`//home/delivery_ml/research/tarstars/troll_farm/mirrors/legacy-data-analysis-2026-07-24.tar.gz`
(SHA-256 in the adjacent `.sha256` sidecar node).

The third tranche completed on 2026-07-29 and is the first to migrate **tracked** files.
1,629 tracked bulk artifacts (232,647,112 bytes) — the ≥100 KB non-record payloads under
`data/analysis`, `data/candidates`, `data/panels`, plus all of `data/boss5_games`,
`data/arena_replays` and the legacy `data/raw/battles` — were copied to
`artifacts/legacy-tracked-migration`, verified by count, bytes and per-file SHA-256
(1,629/1,629 match; itemized checksum `rsync --dry-run` reported zero changes), then
replaced with path-preserving symlinks which are **committed to git**, so the repository
records what moved and where. Digest list:
`docs/storage-migration-2026-07-29-tracked.sha256`. Free space after `sync`: 454094581760
bytes on `medium_data`.

Deliberately retained in the repository, against the size-only heuristic:
`cgauto/submissions` (the frozen bot artifacts, including the live source),
`docs/plays` (input to `sim/validate_replay.py`), all experiment protocols, locks,
result documents and result JSONs (587 record files explicitly protected by the selection
filter), and **`data/raw/games`** — the live replay store, which the daily collection
cron writes to and whose QA would fail on a detached volume (the B5.3 re-scope decision).
