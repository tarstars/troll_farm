# S3 cold archive (spec Phase 3) — execution and verification record

- Date (real UTC): 2026-08-11, upload window 11:44–12:40Z
- Operator: `local_claude_1` (coordinator), on `project_host`
- Spec: `docs/superpowers/specs/2026-08-11-cloud-storage-migration-design.md` Phase 3
- Activation: owner go-ahead this session, after asking whether the `medium_data` USB
  still had to stay plugged in. The drive was attached, which Phase 3 requires.
- Network gate: the owner's WiFi confirmation earlier this session (same connection,
  same session) — the metered-network rule still governs any future upload.
- Tool: `data/scripts/upload_archive.py` (new, this session)

## What was archived

Every regular file under `/media/tarstars/medium_data/database/troll_farm` —
**3,483 files, 9.99 GiB** — uploaded to `s3://troll-farm-data/archive/<path>`, the object
key mirroring the on-USB path exactly.

| Tree | Objects | Size | Class |
|---|---:|---:|---|
| `artifacts/legacy-data-analysis` | 717 | 5.74 GiB | COLD |
| `artifacts/experiments` | 133 | 3.64 GiB | STANDARD |
| `artifacts/legacy-tracked-migration` | 1,629 | 0.22 GiB | COLD |
| `artifacts/worktree-salvage-20260810` | 2 | 0.16 GiB | COLD |
| `artifacts/git-history-backup` | 2 | 0.04 GiB | COLD |
| `data` (`generated` + `external`) | 999 | 0.18 GiB | STANDARD |
| `outputs` | 1 | 0.01 GiB | COLD |
| `yt_work` | 0 | — | (empty) |

Per-file manifests at `archive-manifest/<tree>.jsonl`, lines
`{"path","sha256","size","key","storage_class"}`.

## Two design decisions worth stating

**Per-file objects, not packs.** The backfill corpus was packed 1,000 games to a pack
because it is scanned in batch. This archive is the opposite case: 2,346 repo symlinks
point at these files by **absolute** path, so the spec's Phase 4 GeeseFS mount can only
make them resolve if each file is its own object at the mirrored key. Packing would have
saved requests and broken the read layer.

**Manifests live outside `archive/`.** `archive/` is a pure mirror of the tree; putting
manifests inside it would materialise a phantom `manifest/` directory in any future mount.

Storage classes follow the spec's inventory table: frozen legacy trees cold, warm
experiment rows standard. **One deviation:** `data/` (generated + external, 191 MB) is not
in that table; it is a symlink target read by analysis code, so it was treated as warm and
uploaded STANDARD.

## Verification — VERIFY: PASS, exit 0

```
head-check: 3483/3483 objects match manifest size+sha256
spot-check data/external/banana-r2-host-gates/empty.stderr (0.0 MiB): sha256 MATCH
spot-check artifacts/legacy-tracked-migration/data/boss5_games/boss/game_895276104.log (0.0 MiB): sha256 MATCH
spot-check artifacts/legacy-data-analysis/data/analysis/live-agent-6553250/local-model-rollouts-0-119.tsv (0.0 MiB): sha256 MATCH
spot-check artifacts/legacy-tracked-migration/data/boss5_games/boss/game_895354825.raw (0.1 MiB): sha256 MATCH
spot-check data/external/r36-agent-6594200/games/898013302.json (0.2 MiB): sha256 MATCH
spot-check artifacts/legacy-data-analysis/data/analysis/live-agent-6553250/d18-resident-residual-observations-train372000-373919.npy (728.5 MiB): sha256 MATCH
remote objects across 8 tree prefixes: 3483 (expect 3483)
remote objects under archive/: 3483 (expect 3483)
archived: 3483 files, 9.99 GiB
VERIFY: PASS
```

**Independent cross-check, run after the fact and not by the uploader:** a fresh walk of
the USB counts **3,483 files / 10,723,508,326 bytes (9.99 GiB)** — equal to the remote
object count and size. Whole-bucket census: `archive/` 3,483 objects 9.99 GiB,
`archive-manifest/` 7, `games/` 40 objects 0.68 GiB; total 10.67 GiB against a 50 GiB cap.

**What the verification does and does not prove.** The head-check confirms all 3,483
objects exist with the manifest's size and recorded digest; the sha256 in metadata is
self-reported at upload time, so it proves bookkeeping, not bytes. Byte integrity is
proven by the six full re-downloads, deliberately including the largest object so
multipart reassembly is covered. A full 10 GiB re-download was judged not worth the
retrieval cost; that is a stated limit, not an oversight.

## A bug the smoke test caught before the real run

The first smoke run reported `head-check: 0/3` while every byte-level spot check matched.
Cause: Yandex echoes user metadata **title-cased** (`Sha256`), unlike AWS's lowercase, so
the digest lookup never matched. Beyond the false FAIL, this would have defeated the
head-and-skip resume path and re-uploaded all 10 GiB on any retry. Fixed with a
case-insensitive lookup; the re-run then reported the objects as `already present`,
proving idempotency. Smoke-testing on the two smallest trees cost about a minute.

## Known gap: `yt_work` is empty

It holds no regular files, so it produced no objects — S3 has no directories. Any future
mount will lack `yt_work/` until something is written there. Harmless today, noted so it
is not mistaken later for a failed upload.

## What this does and does not change about the USB

**Does:** the project's 10 GiB is no longer single-copy on a portable drive. Unplugging it
now loses no data.

**Does not:** the 2,346 absolute symlinks still point at `/media/tarstars/medium_data/...`,
so with the drive detached they dangle exactly as before — about 20 frozen-analysis seal
tests fail, and `cgauto/check_external_storage.py` fails closed on bulk writes (the good
failure mode: it refuses rather than silently filling the NVMe). **Demotion to offline
backup is therefore not yet complete**; it needs the spec's Phase 4 read layer.

Phase 4 recon done here: **`geesefs` 0.35.0 is packaged in the Yandex apt repo**, so
installation is routine (needs sudo). The mount must land on `/media/tarstars/medium_data`
for the absolute symlinks to resolve, and that directory is root-owned and created by
udisks2 on attach — so the cut-over needs sudo and is cleanest with the drive detached.
Cost note for Phase 4: the frozen trees are COLD, which trades cheap storage for
per-retrieval charges; if the seal tests read them on every run through the mount, that
should be measured before it becomes routine.

## B9 revisit (Phase 3 owed a decision): DEFER, with a trigger

The 325 tracked files inside gitignored `data/raw/` (ignore rule `data/.gitignore:1:raw/`;
tracked files override it) break down as 290 game dumps, 31 **symlinks** into the USB
under `data/raw/battles/`, and 4 loose files (`players.json`, `leaderboard.json`,
`fetch_log.json`, `collect_run1.log`).

**Decision: do not untrack yet.** The spec conditions the decision on S3 being "the
canonical home for all raw dumps", and it is not: Phase 2 collector v2 is mid-build
(`claude_1` at B2 of B1–B6) and cut-over needs seven days of manifest parity plus the
owner's nod. The `project_host` cron remains the producer of record.

**New finding that de-risks the eventual removal:** nothing in the test suite reads these
paths. The only `tests/` mention of `data/raw` is a docstring in
`tests/test_waste_sweep.py` stating that no test touches the corpus; the real consumers
are manually-run `cgauto/` analysis scripts working against the full local corpus. So the
untracking is low-risk whenever the precondition is met — and as of today durability is no
longer an argument either way: the 290 games are inside the verified backfill packs and the
31 battle symlink targets are in this archive.

**Trigger: revisit at Phase 2 cut-over**, not at some later date chosen by hand.
