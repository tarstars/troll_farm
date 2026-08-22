# Branch integration runbook — keeping a lean repository

Owner-directed standing procedure (2026-08-07): **periodically merge all agent branches into
`main`, then delete what has been absorbed.** Work that lives only on a side branch is
effectively invisible — the R2 programme spent a week re-deriving problems that D89a had already
measured, not because anything was lost, but because nobody looks at 36 branches.

Run this as the integrator, after a review cycle closes or whenever the branch count grows past
roughly a dozen.

## Invariants — do not violate these while integrating

1. **Keep the canonical agent branches.** `agent/claude_1`, `agent/chatgpt_1`,
   `agent/local_codex_1`, `agent/local_claude_1` carry the v2 message transport: a handoff's
   `artifact_ref` must be its sender's canonical branch. Deleting one breaks delivery validation
   for every message it carries. Merge them into `main`; never delete them.
2. **Strip agent-authored CI after every merge.** Merging restores deleted workflow files. Check
   `.github/workflows/` at the end of every integration and remove what reappears.
3. **Verify the hash-locked sources survived**: sacred `rust/src/bin/yamo_orchard_live.rs`
   `fff6669b…`, the live round-36 candidate `2caac7c6…`, the banana parent `a8eb3b2b…`.
4. **Never merge a rejected experiment branch that conflicts in engine sources.** Preserve it on
   its own ref instead. `abgate-selfplay-gate` (2026-07-11, Gold-era yann line, REJECT at −61.0,
   halted by owner stop-order) conflicts in `rust/src/game/engine.rs`, `botmain.rs`,
   `equality.rs`, `mod.rs`, `tests/end_condition.rs` and is deliberately left unmerged.
5. **Run the integration in a scratch worktree**, never in an agent's working worktree, and never
   `git add -A` while other agents are active.

## Procedure

```bash
# 1. scratch worktree from current main
git fetch origin --prune
git worktree add -B integ-main <scratch>/integ origin/main && cd <scratch>/integ

# 2. merge the most-integrated branch first (fewest downstream conflicts)
git merge --no-edit origin/agent/local_claude_1

# 3. merge everything else; skip anything already contained
for r in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin \
           | grep -v HEAD | grep -v 'origin/main$'); do
  git merge-base --is-ancestor $r HEAD 2>/dev/null && continue
  git merge --no-edit -q $r || { <resolve, see policy>; }
done

# 4. strip CI that the merges restored
git rm -r .github/workflows && git commit

# 5. verify, then publish main and the session branch together
sha256sum rust/src/bin/yamo_orchard_live.rs      # must be fff6669b…
python3 -m py_compile scripts/inbox_sweep.py claude_1/pipeline/fuzz_panel.py
git push origin HEAD:main
git push origin HEAD:session-2026-07-01
```

## Conflict policy

- **`coordination/status/*.md` → take ours.** These are point-in-time snapshots; the integrated
  side is newer, and merging an older task-branch snapshot over it regresses the record. This
  covered the large majority of conflicts in the 2026-08-07 run.
- **Generated docs, analysis results, task records → take ours.** Same reasoning: `main` after
  merging the canonical branches holds the current version; the side branch is older. Files that
  exist *only* on the side branch still merge in automatically and are not affected.
- **Anything under `rust/`, `sim/`, `cgauto/` → stop and inspect.** Never auto-resolve engine,
  simulator, or submission-tooling conflicts.
- **LFS smudge failures** (`smudge filter lfs failed` when an object is not fetchable): re-run the
  merge with `GIT_LFS_SKIP_SMUDGE=1`. The pointer file is what git tracks; content is unaffected.

## Cleanup

Delete a remote branch only when **all** hold: it is an ancestor of `main`; it is not a canonical
agent branch; it is not under `archive/`; it is not a deliberately-unmerged experiment. Deletion
is recoverable — the commits survive in `main`'s history.

## Record of the 2026-08-07 run

36 remote refs → 8. Merged 27 distinct branches; 12 needed only status-file resolution; 4 needed
the doc/analysis policy; 1 (`chatgpt_1-lfs-probe`) needed `GIT_LFS_SKIP_SMUDGE=1`; 1
(`abgate-selfplay-gate`) deliberately not merged. Three CI workflows reappeared and were stripped.
28 absorbed branches deleted. `main` and `session-2026-07-01` both at `caea9642`; 8,639 tracked
files; sacred/live/parent hashes verified; transport re-checked — 784 messages scanned, 0
immutable-path collisions.

Surviving refs: `main`, `session-2026-07-01`, the four canonical agent branches,
`archive/chatgpt_1-pre-backlog-20260729`, and `abgate-selfplay-gate`.
