# The coordinator's fallback seat on the VM (2026-09-02)

Owner: "I want this research to move on without me pushing it." The coordinator (local_claude_1)
normally runs as a session on the owner's laptop and paces itself with scheduled wakes. If that
laptop is off (battery, sleep, closed lid), the bots on the VM finish their charters and then wait
for rulings that never come. This fallback closes the gap.

- `coordinator_watchdog.sh` — installed at `/home/tarstars/coordinator-watchdog.sh` on the VM
  (`ssh troll-vm`), run hourly by the user crontab at minute 20. It stays quiet while the board
  (`coordination/BOARD.md` on `origin/main`) was touched within the last three hours — the laptop
  coordinator is alive. When the board has been silent for three hours AND the inbox sweep finds
  mail for local_claude_1 (unseen or unacknowledged), it runs ONE headless coordinator wake on the
  VM: a worktree `/home/tarstars/prj/troll_farm-local_claude_1` reset to `origin/agent/local_claude_1`,
  `claude-proxy -p` with `coordinator-wake-prompt.txt`, at most once per three hours.
- `coordinator-wake-prompt.txt` — the standing wake routine for that seat (installed at
  `/home/tarstars/coordinator-wake-prompt.txt`): read the rules, the goal, the board and the cards;
  sweep the inbox; verify peers' claims by execution; rule, acknowledge, charter the next stage of
  Tracks P and E; ladder items only through the queue file after the panel and the reproduction;
  never touch the network line's trainings, the cluster or the laptop-only work; entries signed
  "— coordinator (VM fallback)".
- Logs on the VM: `/home/tarstars/launcher-state/coordinator-watchdog.log` (every decision),
  `local_claude_1.session.log` (the last fallback session's output),
  `local_claude_1.last-fallback-wake` (the stamp).
- Dry run: `WATCHDOG_DRY=1 WATCHDOG_SILENCE_SECONDS=0 /home/tarstars/coordinator-watchdog.sh`.
- Known limits: the fallback seat has no access to the owner's laptop (the network line's host
  arms and benches wait for it) and does not carry the laptop session's memory notes — the repo's
  handovers and cards are its memory. Two coordinators never act at once by construction (the
  three-hour silence rule), but both always rebase on `origin/main` before pushing.
