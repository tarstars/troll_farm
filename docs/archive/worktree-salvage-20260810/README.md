# Repository hygiene cleanup, 2026-08-10 — what was archived and how to restore it

Nothing was discarded. Every branch and worktree removed below is recoverable from a
tag or branch that is pushed to `origin`. This file exists so those archives are
findable; without it the tags are invisible.

## Restoring anything

```bash
git fetch origin --tags
git branch <new-name> archive/<name>        # from a tag
git checkout archive/local_codex_1-stranded-20260810   # from the branch
```

## Branches deleted, preserved as tags

All 17 tags are pushed to `origin`. Each points at the exact tip the branch had.

| tag | was | unique commits | content |
|---|---|---:|---|
| `archive/abgate-selfplay-gate` | local + `origin/abgate-selfplay-gate` | 20 | the `yann` alternative bot; V3 n=200 measured REJECT |
| `archive/worktree-agent-a1db44cecce56bca4` | local | 11 | `fellmission` C1/C2/C3 fixes |
| `archive/worktree-agent-a3371ee579c908bb9` | local | 9 | `trainfruit` — two CRITICAL funding-loop fixes |
| `archive/worktree-agent-a4a28cc4b0708f40c` | local | 8 | `chopharvest` turn-1 adaptive spec wiring |
| `archive/worktree-agent-a5a0b6adf1096dd10` | local | 4 | |
| `archive/worktree-agent-a21a743036949b693` | local | 1 | |
| `archive/worktree-agent-a4013449442c4c2d8` | local | 1 | |
| `archive/worktree-agent-a65e836640649f65e` | local | 1 | |
| `archive/worktree-agent-ae6f6732da5146bd5` | local | 1 | |
| `archive/evidence-current-20260731` | worktree HEAD `5f12c81e`, never on main | 11 | evidence-index semantic locator migration, 25 files |
| `archive/claude_1-banana-restoration-r2` | `origin/agent/claude_1-banana-restoration-r2` | 1 | session findings digest 08-07..08-11 |
| `archive/chatgpt_1-actions-trigger-20260809` | `origin/agent/…` | 0 | CI trigger experiment |
| `archive/chatgpt_1-remove-broken-lfs-probe-20260811` | `origin/agent/…` | 0 | |
| `archive/chatgpt_1-verify-20260811` | `origin/agent/…` | 0 | |
| `archive/chatgpt_1-write-probe-20260808` | `origin/agent/…` | 0 | |
| `archive/chatgpt_1-pre-backlog-20260729` | `origin/archive/…` | 0 | |
| `archive/check-session` | orphaned `refs/remotes/check-session` | 0 | |

**Canonical agent refs were deliberately NOT deleted** — `origin/agent/{local_claude_1,
claude_1, codex_1, chatgpt_1, chatgpt_2, local_codex_1}` all remain. The transport
validates that a v2 handoff is present on its sender's canonical branch, so deleting
one would permanently invalidate that sender's published messages. Verified after the
cleanup: remote refs dropped 15 → 9 and the sweep still reports `delivery errors (0)`.

## Worktrees removed (11)

Ten under `/tmp` plus `/home/tarstars/prj/troll_farm-local_codex_1`. Salvage first:

- **`troll_farm-local_codex_1`** — 222 uncommitted files (206 untracked, 16 modified),
  abandoned at the 2026-08-06 coordinator transfer on a branch already fully merged.
  Committed verbatim to branch **`archive/local_codex_1-stranded-20260810`** (`2bfc462a`),
  pushed. Mostly the e7a half-size simplification traces and the readable-manual working
  state. No claim is made that this work is correct or complete; it is salvage.
- **`troll-farm-evidence-review.0ndeYp`** (10 modified) and **`.kUCK9l`** (2) — working
  diffs captured as `*.patch` beside this file.
- **`troll-banana-r2-check`**, **`troll-banana-r3-check`** — 1 modified manifest each,
  captured as `*.patch`.
- **`troll-farm-n4-review.eaE6Ux`** — 133 dirty files. 127 were cargo build cache and
  were discarded. The other 6 were real artifacts: `generated_runner.rs`,
  `instrumented_resident.rs` and two `smoke-analysis*.json` are in `n4-host-gate/` here;
  the two 83 MB `smoke-threads*.tsv` traces exceed what belongs in Git and were moved,
  copy-then-verify with matching sha256, to
  `artifacts/worktree-salvage-20260810/n4-host-gate/`.

## Also reclaimed

`rust/target/debug` (1.6 GB), `cgauto/profile` (379 MB), `target/` (52 MB), 64
`__pycache__` directories, and 1.4 GB of unregistered `/tmp/troll-*` debris.
`rust/target/release/libtroll_farm.so` was kept — `AGENTS.md` records that the Python
ctypes tests depend on it.

## Verified unchanged after cleanup

- `rust/src/bin/yamo_orchard_live.rs` and `rust/src/d171a_control_resident_snapshot.rs`
  both still SHA-256 `fff6669b…`.
- `pytest`: 1623 passed, 3 failed — byte-identical to the pre-cleanup result. Those three
  failures are pre-existing and unrelated.
- `inbox_sweep.py --me local_claude_1 --fetch`: delivery errors 0, quarantine errors 0,
  immutable-path collisions 0, quarantined 9, unacknowledged 80.
