#!/usr/bin/env python3
"""Build the writable union over the read-only archive mount (owner decision 2026-08-11).

The archive mount is read-only, so `artifacts/` could serve history but not accept new
output. Rather than an overlay filesystem (needs a package install and, for kernel
overlayfs, root), this composes the same effect out of symlinks: `artifacts/` becomes a
real LOCAL directory whose children are symlinks into the mount, so

  * reading an archived subtree follows a link into the mount, exactly as before;
  * creating a NEW subdirectory just works — it lands on local disk;
  * `upload_archive.py` later pushes those new directories into `archive/`, after which
    this script can replace them with links and reclaim the space.

Idempotent and conservative: it only ever creates links and only ever removes links it
would recreate. **A real directory is never deleted** — if a name exists locally as a real
directory and also in the archive, the local one wins and is reported, because that is the
"uploaded but not yet reclaimed" state and losing it would lose data.

Usage:
    python3 data/scripts/link_archive_roots.py            # report only
    python3 data/scripts/link_archive_roots.py --apply
"""
from __future__ import annotations

import argparse
from pathlib import Path

MOUNT = Path("/media/tarstars/medium_data/database/troll_farm")
LOCAL = Path("~/.cache/troll-farm/bulk").expanduser()
# Paths that must stay REAL local directories, with their archived children linked in.
# `artifacts/experiments` is here because that is where a new experiment directory is
# created: if it were a single link into the read-only mount, the write would still fail —
# which is exactly what the first dry run of this script revealed.
UNION_DIRS = (
    "artifacts",
    "artifacts/experiments",
    "outputs",
    "data/external",
)
# The repo-level symlinks that must point at the local union roots.
REPO_ROOTS = ("artifacts", "outputs", "data/external")


def union_dir(local: Path, archived: Path, apply: bool, report: list[str],
              skip: frozenset[str] = frozenset()) -> None:
    """Make `local` a real directory whose children link into `archived`.

    `skip` names children that are themselves union directories and so must not be
    replaced by a link to the read-only mount.
    """
    if local.is_symlink():
        if apply:
            local.unlink()
        report.append(f"unlink  {local} (was a whole-tree link; becoming a union dir)")
    if apply:
        local.mkdir(parents=True, exist_ok=True)
    if not archived.is_dir():
        report.append(f"absent  {archived} — nothing to link (empty in the archive)")
        return
    for child in sorted(archived.iterdir()):
        if child.name in skip:
            continue
        link = local / child.name
        if link.is_symlink():
            if link.resolve() == child.resolve():
                continue
            if apply:
                link.unlink()
            report.append(f"relink  {link}")
        elif link.exists():
            # A real directory shadowing an archived one: uploaded-but-not-reclaimed.
            report.append(f"LOCAL   {link} — real directory kept (never auto-deleted)")
            continue
        if apply:
            link.symlink_to(child)
        report.append(f"link    {link} -> {child}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--mount", type=Path, default=MOUNT)
    ap.add_argument("--local", type=Path, default=LOCAL)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    if not a.mount.is_dir():
        print(f"archive mount not present at {a.mount}; refusing to guess")
        return 2

    report: list[str] = []
    for relative in UNION_DIRS:
        nested = frozenset(
            Path(other).name for other in UNION_DIRS
            if other != relative and str(Path(other).parent) == relative
        )
        union_dir(a.local / relative, a.mount / relative, a.apply, report, nested)

    for relative in REPO_ROOTS:
        repo_link = a.repo / relative
        target = a.local / relative
        if repo_link.is_symlink() and repo_link.readlink() != target:
            if a.apply:
                repo_link.unlink()
                repo_link.symlink_to(target)
            report.append(f"repoint {repo_link} -> {target}")

    for line in report:
        print(line)
    print(f"\n{len(report)} action(s); {'APPLIED' if a.apply else 'dry run — pass --apply'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
