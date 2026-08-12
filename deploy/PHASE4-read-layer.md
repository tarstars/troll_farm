# Phase 4 — the read layer (GeeseFS), runbook

Spec: `docs/superpowers/specs/2026-08-11-cloud-storage-migration-design.md` §5 Phase 4.
Written 2026-08-11, after Phase 3 put 3,483 files / 9.99 GiB into `s3://troll-farm-data/archive/`
and the USB was unmounted and detached.

## What it is, in one line

Put the bucket at the exact filesystem path the USB used to occupy, so the repo's **2,346
absolute symlinks resolve unchanged** and no file in the repo has to be edited.

## Why the path cannot be chosen freely

The symlinks are absolute. A representative one:

```
data/raw/battles/6479420.json
  -> /media/tarstars/medium_data/database/troll_farm/artifacts/legacy-tracked-migration/data/raw/battles/6479420.json
```

31 of them are committed to git (mode 120000), so re-pointing them is not a local tweak —
it changes every clone and has to be reverted if the drive returns. Mounting at the old path
changes nothing anywhere. This is also why Phase 3 uploaded **per-file objects mirroring the
tree** rather than packs: packs would have made this impossible.

## Why sudo is needed (twice, briefly)

`/media/tarstars` is `root:root`, mode `rwxr-x---`, with an ACL granting `user:tarstars:r-x`
— read and execute, **not write**. Verified: `mkdir /media/tarstars/_probe` fails with
permission denied. Normally udisks2 (running as root) creates `medium_data` there when the
drive is plugged in and removes it when it is not, so nobody notices. To put anything else at
that path, the directory must be created by root.

FUSE itself does **not** need root: `fusermount` is setuid, so once the directory exists and
is owned by the user, the mount runs unprivileged.

```bash
sudo apt install -y geesefs                                    # 0.35.0, Yandex repo
sudo install -d -o tarstars -g tarstars /media/tarstars/medium_data
```

Everything after this point is unprivileged.

## Mount

Credentials are already staged at `~/.config/troll-farm/geesefs-credentials` (0600, INI
format, **vm-writer** service account). That account can read and upload but **cannot
delete** — verified, `DeleteObject` returns `AccessDenied`. Combined with `-o ro` in the unit,
a mistaken `rm -rf` through the mount cannot destroy the project's only off-host copy.

```bash
mkdir -p /media/tarstars/medium_data/database/troll_farm
cp deploy/geesefs-archive.service ~/.config/systemd/user/
# CHECK THE FLAGS FIRST — see the warning in that file; geesefs has never been run here
geesefs --help | head -40
systemctl --user daemon-reload && systemctl --user enable --now geesefs-archive
```

## Verify, in this order

1. `ls /media/tarstars/medium_data/database/troll_farm` → `artifacts data outputs`
   (`yt_work` will be **absent**: it held no files, and S3 has no directories — expected,
   recorded in the Phase 3 record, not a failed upload).
2. A tracked symlink resolves: `readlink -e data/raw/battles/6479420.json` returns a path
   and `sha256sum` of it matches the entry in `archive-manifest/artifacts-legacy-tracked-migration.jsonl`.
3. Writes are refused: `touch /media/tarstars/medium_data/database/troll_farm/_x` fails.
4. The frozen-analysis seal tests pass — the ~20 that fail with the drive absent are the
   acceptance test for this phase. Full-suite baseline with the USB attached was
   **1670 passed / 0 failed**.
5. `cgauto/check_external_storage.py` still fails closed — it checks an **ext4 filesystem
   label**, which a FUSE mount does not have. That is preflight v2's job (below), and until
   it is written, bulk writes stay blocked. Do not "fix" it by loosening the check.

## Known consequences, decide before enabling

- **The mount and the USB want the same path.** With a permanent directory at
  `/media/tarstars/medium_data`, replugging the drive will mount it elsewhere
  (`medium_data1`) or not at all. Enabling this means choosing the cloud as the normal
  state and the drive as an offline backup — which is what Phase 3 was for.
- **Reads become network reads, and the frozen trees are COLD class**, which bills per
  retrieval. `artifacts/legacy-data-analysis` alone is 5.74 GiB. Measure one seal-test run
  before letting it become routine; if it is expensive, the fix is to promote just the
  files the tests read to STANDARD, not to abandon the mount.
- **Only the project subtree is in the bucket.** The USB also holds ~1.2 TB of the owner's
  personal archive, which is **not** backed up anywhere by this project.

## EXECUTED 2026-08-11 — results

Owner ran the two sudo commands. Everything below was then done unprivileged and verified.

- geesefs **0.35.0** installed; usage and every flag confirmed against `--help`.
- Mounted `troll-farm-data:archive` at `/media/tarstars/medium_data/database/troll_farm`,
  options `ro,nosuid,nodev,relatime` — writes refused at the kernel.
- A tracked symlink resolves through the mount and its sha256
  (`a7102a4bb5ab2f1f…`) matches its `archive-manifest` entry exactly.
- **Full suite: 1670 passed / 0 failed** through the mount — identical to the recorded
  USB-attached baseline. The ~20 seal tests that fail with the drive absent all pass.
  This is the acceptance criterion for the phase, and it is met.
- Installed as user unit `geesefs-archive` (enabled, active). `loginctl enable-linger`
  succeeded **without root**, so the mount — and the coordd tunnel — now survive reboot
  without a login session.
- **Storage preflight v2 written and shipped** (`cgauto/check_external_storage.py`,
  5 new tests, both new guards mutation-checked; suite now 1675 passed).

## What preflight v2 does differently

It discovers whichever backend is present — USB by ext4 label first, else the geesefs mount
by SOURCE — and separates *what the store can do* from *what the caller wants*:

```
--intent read   → PASS   backend: geesefs (READ-ONLY)
--intent write  → FAIL   "backing store ... is read-only; bulk writes are blocked"  (exit 2)
```

`--intent write` remains the default, so every existing caller keeps its fail-closed
guarantee. The free-space threshold is skipped on object storage, which reports a
fictitious 1 PiB free; comparing that to a threshold would be theatre.

**`yt_work` and `data/generated` are now local scratch**, at `~/.cache/troll-farm/`. Both
held **zero files** on the USB — verified at the Phase 3 upload, where the entire drive was
3,483 files and none were under those two — so nothing was lost by their absence from the
archive. They are write targets, and a read-only archive is the wrong home for a write
target. Both symlinks were untracked, so this is local layout only; no clone is affected.

## ★ Open question this phase exposes, for the owner

**Where do new bulk artifacts get written now?** `artifacts/` is archive-backed and the
mount is read-only, so an experiment that writes `artifacts/experiments/...` will fail —
correctly and loudly, but it will fail. The spec's inventory says experiment rows are
"S3 standard, then read via GeeseFS" and never says how they get written. The plausible
answers are a local staging directory with periodic upload (mirroring what collector v2
does for games), or a second writable mount. **This is not decided, and I have not
decided it.** Until it is, the project can read all its history and cannot produce new
bulk artifacts.
