#!/usr/bin/env python3
"""Session-close guard: exit 2 when any local branch holds commits reachable from no
remote ref ('unpushed = unsent' generalized from messages to work — spec P0). Dirty
worktrees are warned about but do not change the exit code (mid-task state is normal;
an unpushed COMMIT at session close is not)."""
import argparse
import subprocess
import sys


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True)


def main(repo=".", remote="origin"):
    branches = [b for b in
                _git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
                .stdout.split() if b]
    bad = []
    for b in branches:
        n = int(_git(repo, "rev-list", "--count", b, "--not",
                     f"--remotes={remote}").stdout.strip() or "0")
        if n:
            bad.append((b, n))
    for wt in _git(repo, "worktree", "list", "--porcelain").stdout.split("\n\n"):
        path = next((l.split(" ", 1)[1] for l in wt.splitlines()
                     if l.startswith("worktree ")), None)
        if path:
            probe = subprocess.run(["git", "-C", path, "status", "--porcelain"],
                                   capture_output=True, text=True)
            if probe.returncode != 0:
                # a dead worktree path must not silently skip the check (G5 F9)
                print(f"warning: could not inspect worktree {path} "
                      f"(git status exit {probe.returncode})")
            elif probe.stdout.strip():
                dirty = probe.stdout.strip()
                print(f"warning: dirty worktree {path} ({len(dirty.splitlines())} paths)")
    if bad:
        for b, n in bad:
            print(f"UNPUSHED: branch {b} has {n} commit(s) reachable from no {remote} ref")
        print("Push the unpushed commit(s) or archive them as tags before closing the session.")
        return 2
    print(f"ref census clean: {len(branches)} local branches, all reachable from {remote}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--remote", default="origin")
    a = ap.parse_args()
    sys.exit(main(repo=a.repo, remote=a.remote))
