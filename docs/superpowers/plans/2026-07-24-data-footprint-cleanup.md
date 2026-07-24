# Data-Footprint Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reclaim ~19.5 GB of local reproducible cache, migrate the remaining ~1.0 GB bulk tier to `medium_data` with verified symlinks, add a YT mirror of all migrated tranches, and remove one dead YT directory — with zero research-data loss.

**Architecture:** Five independent mechanical operations executed in a fixed order (worktrees → debug cache → migration → hygiene edits → YT), each with its own verification; one consolidated commit for the small file edits plus per-artifact commits.

**Tech Stack:** git worktree, rsync + sha256sum, `cgauto/check_external_storage.py`, `yt.wrapper` via `/home/tarstars/prj/math_through_eml/.venv/bin/python` (cluster `watt.yt.yandex.net`).

**Spec:** `docs/superpowers/specs/2026-07-24-data-footprint-cleanup-design.md` — authoritative for any ambiguity.

## Global Constraints

- Never delete the only verified copy of an artifact (`docs/storage-policy.md`). Symlink
  replacement happens only after count + bytes + per-file SHA-256 verification.
- `git worktree remove` without `--force`; any refusal stops that item and is reported.
- Keep `rust/target/release` (its `libtroll_farm.so` serves the Python ctypes tests),
  `cgauto/profile`, `.venv`, and all branches.
- YT writes are limited to: removing the dead D144 first-attempt directory, creating
  `mirrors/`, uploading two files. Nothing else under the YT root is touched.
- No arena, resident, or experiment-state interaction.
- Every commit message ends with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- `$SCRATCH` = the session scratchpad directory. `$DEST` =
  `/media/tarstars/medium_data/database/troll_farm/artifacts/legacy-data-analysis`.
  All repo commands run from `/home/tarstars/prj/troll_farm`.

---

### Task 1: Remove the 22 clean worktrees

**Files:** none in-repo (removes `.claude/worktrees/*` checkouts; `.git` refs untouched)

- [ ] **Step 1: Enumerate and record the baseline**

```bash
git worktree list --porcelain | grep '^worktree ' | cut -d' ' -f2 | grep -v '^/home/tarstars/prj/troll_farm$' > $SCRATCH/wt-list.txt
wc -l < $SCRATCH/wt-list.txt; git branch | wc -l > $SCRATCH/branch-count-before.txt; cat $SCRATCH/branch-count-before.txt
```
Expected: `22` worktrees; branch count recorded.

- [ ] **Step 2: Remove each worktree only if clean at removal time**

```bash
while read -r wt; do
  n=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l)
  if [ "$n" -eq 0 ]; then
    git worktree remove "$wt" && echo "REMOVED $wt" || echo "REFUSED $wt"
  else
    echo "SKIP-DIRTY $wt ($n)"
  fi
done < $SCRATCH/wt-list.txt
```
Expected: 22 `REMOVED` lines, zero `SKIP-DIRTY`/`REFUSED`. On any `REFUSED`: stop, inspect
that worktree, report to the user before continuing.

- [ ] **Step 3: Prune and verify**

```bash
git worktree prune; git worktree list | wc -l; git branch | wc -l; du -s --block-size=1M .claude/worktrees 2>/dev/null || echo "0 (gone)"
```
Expected: `1` worktree; branch count equals `$SCRATCH/branch-count-before.txt`; worktrees
dir ≤ 1 MB or gone. No commit (nothing tracked changed).

---

### Task 2: Clean debug cache + AGENTS.md cap rule

**Files:**
- Modify: `AGENTS.md` (append one bullet to "Local Bulk Storage Policy")

- [ ] **Step 1: Delete the debug profile only**

```bash
du -s --block-size=1M rust/target/debug; rm -rf rust/target/debug
ls -la rust/target/release/libtroll_farm.so
```
Expected: ~11,572 MB reported, then removed; the release `.so` still listed.

- [ ] **Step 2: Confirm the ctypes tests still pass**

Run: `.venv/bin/python -m pytest tests/test_rl_level5_env.py -q 2>&1 | tail -1`
Expected: all tests in the file pass (26 previously failing ones stay green).

- [ ] **Step 3: Append the cap rule to AGENTS.md**

Replace:

```markdown
- Build outputs and virtual environments are reproducible local caches, not
  research archives. They may remain local while useful, but clear stale
  Cargo targets and inactive-worktree environments before allowing them to
  crowd out research data.
```

with:

```markdown
- Build outputs and virtual environments are reproducible local caches, not
  research archives. They may remain local while useful, but clear stale
  Cargo targets and inactive-worktree environments before allowing them to
  crowd out research data.
- `rust/target` is a disposable cache. At session end, if it exceeds ~10 GB,
  delete `rust/target/debug`; keep `rust/target/release`, whose
  `libtroll_farm.so` serves the Python ctypes tests.
```

No commit yet — AGENTS.md commits together with the other small edits in Task 4.

---

### Task 3: Bulk migration tranche 2 (copy → verify → symlink)

**Files:**
- Create: `docs/storage-migration-2026-07-24.sha256`
- Replaces ~672 untracked regular files under `data/analysis` + `data/panels` with symlinks

- [ ] **Step 1: Preflight and boundary**

```bash
python3 cgauto/check_external_storage.py --required-free-gib 5
ps aux | grep -E 'cargo|analyze_d|train_d|run_d' | grep -v grep | wc -l
git ls-files --others --exclude-standard -- data/analysis data/panels > $SCRATCH/mig-candidates.txt
: > $SCRATCH/mig-files.txt
while read -r f; do
  [ -f "$f" ] && [ ! -L "$f" ] && [ -z "$(find "$f" -mmin -60 2>/dev/null)" ] && echo "$f" >> $SCRATCH/mig-files.txt
done < $SCRATCH/mig-candidates.txt
wc -l < $SCRATCH/mig-files.txt
```
Expected: preflight passes all five checks; `0` running writers; ~672 files listed
(tranche-1 symlinks and <1 h-old files excluded).

- [ ] **Step 2: Local manifest (count, bytes, hashes)**

```bash
xargs -d'\n' stat -c '%s' < $SCRATCH/mig-files.txt | awk '{s+=$1;n++} END{printf "local: %d files, %d bytes\n", n, s}' | tee $SCRATCH/mig-src-totals.txt
xargs -d'\n' sha256sum < $SCRATCH/mig-files.txt > $SCRATCH/mig-manifest-local.sha256
wc -l < $SCRATCH/mig-manifest-local.sha256
```
Expected: totals printed; manifest line count equals file count.

- [ ] **Step 3: Copy and verify (count, bytes, hashes, zero-diff dry run)**

```bash
DEST=/media/tarstars/medium_data/database/troll_farm/artifacts/legacy-data-analysis
rsync -aHXS --files-from=$SCRATCH/mig-files.txt /home/tarstars/prj/troll_farm/ "$DEST/"
(cd "$DEST" && xargs -d'\n' stat -c '%s' < $SCRATCH/mig-files.txt | awk '{s+=$1;n++} END{printf "dest: %d files, %d bytes\n", n, s}')
(cd "$DEST" && xargs -d'\n' sha256sum < $SCRATCH/mig-files.txt > $SCRATCH/mig-manifest-dest.sha256)
diff <(sort $SCRATCH/mig-manifest-local.sha256) <(sort $SCRATCH/mig-manifest-dest.sha256) && echo HASHES-MATCH
rsync -aHXScn --itemize-changes --files-from=$SCRATCH/mig-files.txt /home/tarstars/prj/troll_farm/ "$DEST/" | wc -l
```
Expected: dest totals identical to `mig-src-totals.txt`; `HASHES-MATCH`; final count `0`
(checksum dry run itemizes nothing). Any mismatch: STOP — do not proceed to Step 4.

- [ ] **Step 4: Atomic symlink swap + re-read verification**

```bash
DEST=/media/tarstars/medium_data/database/troll_farm/artifacts/legacy-data-analysis
while read -r f; do ln -s "$DEST/$f" "$f.linktmp" && mv -T "$f.linktmp" "$f"; done < $SCRATCH/mig-files.txt
find data/analysis data/panels -name '*.linktmp' | wc -l
shuf -n 32 $SCRATCH/mig-manifest-local.sha256 > $SCRATCH/mig-sample.sha256
sha256sum -c $SCRATCH/mig-sample.sha256 | grep -c ': OK$'
sync -f "$DEST"
```
Expected: `0` leftover temp links; `32` sample hashes read back OK through the symlinks.

- [ ] **Step 5: Durable manifest**

```bash
cp $SCRATCH/mig-manifest-local.sha256 docs/storage-migration-2026-07-24.sha256
wc -l docs/storage-migration-2026-07-24.sha256
```
Expected: line count equals the migrated file count. Commit happens in Task 4.

---

### Task 4: Hygiene edits + consolidated commit

**Files:**
- Modify: `data/.gitignore` (append 7 lines), `docs/storage-policy.md` (append adoption
  paragraph), plus the Task-2 `AGENTS.md` edit and Task-3 manifest

- [ ] **Step 1: Append bulk-extension ignores to `data/.gitignore`** (read it first, then
  append verbatim)

```gitignore
# bulk artifact tiers live on medium_data behind symlinks (storage-policy.md);
# compact md/json/sha256 records stay visible for commit
analysis/**/*.tsv
analysis/**/*.pt
analysis/**/*.npz
analysis/**/*.npy
analysis/**/*.bin
analysis/**/*.tar.gz
analysis/**/*.maps
```

Run: `git status --short | wc -l`
Expected: drops from ~672 to ≲60.

- [ ] **Step 2: Append the tranche-2 adoption paragraph to `docs/storage-policy.md`**

Append after the tranche-1 adoption section, filling the three measured values from
Task 3 outputs (file count, byte total, post-`sync` free space from `df --output=avail -B1
/media/tarstars/medium_data | tail -1`):

```markdown
The second historical tranche completed on 2026-07-24: <N> untracked regular files
(<BYTES> apparent bytes) from `data/analysis` and `data/panels` were copied to
`artifacts/legacy-data-analysis`, verified by count, bytes, and per-file SHA-256
(digest list: `docs/storage-migration-2026-07-24.sha256`), then replaced with
path-preserving symlinks and re-read through the repository paths. Free space after
`sync`: <FREE> bytes on `medium_data`. A consolidated mirror of the whole
`legacy-data-analysis` tree was archived to YT as
`//home/delivery_ml/research/tarstars/troll_farm/mirrors/legacy-data-analysis-2026-07-24.tar.gz`
(SHA-256 in the adjacent `.sha256` sidecar node).
```

- [ ] **Step 3: Commit the four small artifacts**

```bash
git add AGENTS.md data/.gitignore docs/storage-policy.md docs/storage-migration-2026-07-24.sha256
git commit -m "storage(tranche2): migrate ~1.0 GB untracked analysis bulk to medium_data; cargo cap rule; bulk-extension ignores; adoption record

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: YT operations (dead directory + tranche mirror)

**Files:**
- Create: `$SCRATCH/yt_cleanup_mirror.py` (scratch tooling, not committed)
- Staging: `/media/tarstars/medium_data/database/troll_farm/artifacts/mirror-staging/`

- [ ] **Step 1: Build the archive on the external drive (not /tmp — it may be tmpfs)**

```bash
STAGE=/media/tarstars/medium_data/database/troll_farm/artifacts/mirror-staging
mkdir -p "$STAGE"
tar -C /media/tarstars/medium_data/database/troll_farm/artifacts -czf "$STAGE/legacy-data-analysis-2026-07-24.tar.gz" legacy-data-analysis
sha256sum "$STAGE/legacy-data-analysis-2026-07-24.tar.gz" | tee "$STAGE/legacy-data-analysis-2026-07-24.tar.gz.sha256"
du -s --block-size=1M "$STAGE"
```
Expected: archive ~1.5–2.5 GB; sidecar written.

- [ ] **Step 2: Write and run the YT script** — `$SCRATCH/yt_cleanup_mirror.py`:

```python
"""Remove dead D144 first-attempt dir; upload tranche mirror. Idempotent."""
import hashlib, sys
import yt.wrapper as yt

yt.config["proxy"]["url"] = "watt.yt.yandex.net"
ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
DEAD = ROOT + "/dataset_builds/d144a_two_intervention_mc_9844128_9844135_20260722"
KEEP = ROOT + "/dataset_builds/d144a_two_intervention_mc_9844128_9844135_repair1_20260722"
STAGE = "/media/tarstars/medium_data/database/troll_farm/artifacts/mirror-staging"
NAME = "legacy-data-analysis-2026-07-24.tar.gz"

assert yt.exists(KEEP), "repair1 sibling missing — abort"
if yt.exists(DEAD):
    assert yt.get(DEAD + "/records/@row_count") == 0, "dead dir has rows — abort"
    yt.remove(DEAD, recursive=True)
print("dead dir removed:", not yt.exists(DEAD))

yt.create("map_node", ROOT + "/mirrors", ignore_existing=True)
local = f"{STAGE}/{NAME}"
md5 = hashlib.md5(open(local, "rb").read()).hexdigest()
with open(local, "rb") as f:
    yt.write_file(f"{ROOT}/mirrors/{NAME}", f, compute_md5=True)
with open(local + ".sha256", "rb") as f:
    yt.write_file(f"{ROOT}/mirrors/{NAME}.sha256", f)
remote_md5 = yt.get(f"{ROOT}/mirrors/{NAME}/@md5")
print("md5 match:", remote_md5 == md5)
print("mirror listing:", sorted(yt.list(ROOT + "/mirrors")))
sys.exit(0 if remote_md5 == md5 else 1)
```

Run: `/home/tarstars/prj/math_through_eml/.venv/bin/python $SCRATCH/yt_cleanup_mirror.py`
Expected: `dead dir removed: True`, `md5 match: True`, listing shows the archive + sidecar.
(Memory note for the md5 of a ~2 GB file is acceptable; if the host balks, hash in chunks.)

- [ ] **Step 3: Remove the staging copy** (the tree itself remains the USB copy; YT now
  holds the mirror)

```bash
rm -rf /media/tarstars/medium_data/database/troll_farm/artifacts/mirror-staging
```

---

### Task 6: Acceptance verification

- [ ] **Step 1: Whole-cleanup post-conditions**

```bash
df -h / | tail -1
du -xs --block-size=1M /home/tarstars/prj/troll_farm 2>/dev/null
git worktree list | wc -l; git status --short | wc -l
du -s --block-size=1M rust/target
```
Expected: `/` free space up by ≈19–20 GB vs the 277 GB baseline; repo ≈3.2 GB; 1 worktree;
status ≲60 lines; `rust/target` ≈180 MB.

- [ ] **Step 2: Suite regression check**

Run: `.venv/bin/python -m pytest tests/ -q 2>&1 | tail -1`
Expected: `3 failed, 1163 passed` — identical to the 2026-07-23 baseline (the 3 are
documented pre-existing failures).

- [ ] **Step 3: Report** — free-space delta, per-decision outcome, YT account usage delta
  (≈ +2 GiB disk, net +1 node).
