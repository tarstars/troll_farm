#!/bin/bash
# The coordinator's fallback seat on the VM (2026-09-02, owner: "I want this research to move on
# without me pushing it"). Runs hourly by cron. It does nothing while the laptop coordinator is
# alive (the board was touched within the last 3 hours). When the laptop has been silent for 3 hours
# AND mail waits for local_claude_1, it runs ONE headless coordinator wake here, in a worktree of
# agent/local_claude_1 reset to the remote, with the standing wake prompt. At most one wake per
# 3 hours. Logs: /home/tarstars/launcher-state/coordinator-watchdog.log and
# local_claude_1.session.log. Dry run: WATCHDOG_DRY=1 (decide, launch nothing).
set -u
STATE=/home/tarstars/launcher-state
LOG=$STATE/coordinator-watchdog.log
STAMP=$STATE/local_claude_1.last-fallback-wake
PROMPT=/home/tarstars/coordinator-wake-prompt.txt
CHECKOUT=/home/tarstars/prj/troll_farm
WT=/home/tarstars/prj/troll_farm-local_claude_1
SILENCE=${WATCHDOG_SILENCE_SECONDS:-3600}
mkdir -p "$STATE"
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }

cd "$CHECKOUT" || { log "no checkout"; exit 2; }
git fetch -q origin || { log "fetch failed"; exit 2; }
last=$(git log -1 --format=%ct origin/main -- coordination/BOARD.md)
now=$(date +%s)
age=$(( now - last ))
if [ "$age" -lt "$SILENCE" ]; then
  log "quiet: the board was touched ${age}s ago (< ${SILENCE}s); the laptop coordinator is alive"
  exit 0
fi
if [ -f "$STAMP" ] && [ $(( now - $(stat -c %Y "$STAMP") )) -lt "$SILENCE" ]; then
  log "quiet: a fallback wake ran less than ${SILENCE}s ago"
  exit 0
fi

# the coordinator's worktree on the VM, always adopting the remote state
if [ ! -d "$WT" ]; then
  git worktree add -q "$WT" agent/local_claude_1 2>>"$LOG" || { log "worktree add failed"; exit 2; }
fi
cd "$WT" || exit 2
git fetch -q origin && git reset -q --hard origin/agent/local_claude_1 || { log "reset failed"; exit 2; }

# mail waiting? (the sweep prints 'new (unseen) (N):' and 'unacknowledged, ack required (N):')
sweep=$(python3 scripts/inbox_sweep.py --me local_claude_1 --fetch 2>&1)
unseen=$(printf '%s\n' "$sweep" | grep -oE '^new \(unseen\) \([0-9]+\)' | grep -oE '[0-9]+' | tail -1)
unacked=$(printf '%s\n' "$sweep" | grep -oE '^unacknowledged, ack required \([0-9]+\)' | grep -oE '[0-9]+' | tail -1)
unseen=${unseen:-0}; unacked=${unacked:-0}
if [ "$unseen" = "0" ] && [ "$unacked" = "0" ]; then
  log "silent ${age}s but no mail waits (unseen 0, unacked 0); nothing to do"
  exit 0
fi

log "FALLBACK WAKE: board silent ${age}s, unseen $unseen, unacked $unacked"
touch "$STAMP"
if [ "${WATCHDOG_DRY:-0}" = "1" ]; then log "dry run: would launch the headless coordinator now"; exit 0; fi
cd "$WT" && /home/tarstars/bin/claude-proxy -p "$(cat "$PROMPT")" --dangerously-skip-permissions \
  > "$STATE/local_claude_1.session.log" 2>&1
log "fallback wake finished with exit $?"
