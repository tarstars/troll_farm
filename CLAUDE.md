# Troll Farm — read this first (any agent, any harness)

1. **`coordination/WORKING-RULES.md`** — how work moves here (the board, task birth,
   two review rounds, stalls, the ladder queue, roles, the owner conversation). Short.
2. **`coordination/BOARD.md`** — what is in motion right now, one row per task.
3. **`AGENTS.md`** — operating policy: worktrees, branches, message transport, storage,
   the invariants that break other agents' work.
4. **`docs/STATE.md`** — live state (resident, goal, standing rules), then
   `docs/CONSTRAINTS.md` before proposing any experiment.

Every shell command `cd`s into your own worktree (`/home/tarstars/prj/troll_farm-<your-id>`);
the harness resets the cwd. Inbox: `python3 scripts/inbox_sweep.py --me <your-id> --fetch`.
Owner-facing text in plain words, every code explained at first use.
