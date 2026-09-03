#!/bin/bash
# The laptop's battery guard (2026-09-02; the owner's rules of 2026-09-03 added).
#   Rule 1 (09-02): no host training or bench on battery — stop them within a minute of the mains going away.
#   Rule 2 (09-03, owner): "don't run heavy computational tasks when battery is not fully charged when laptop is
#            connected to power grid" — stop them too while the battery is charging below full.
# Heavy work on this laptop is allowed only when AC is on AND the battery is full (capacity 100, or status
# Full / Not charging). `host_ready` below is the same test for launchers: exit 0 = go.
# Deployed copy: /home/tarstars/nn-data/battery-guard.sh (pid file beside it); log battery-guard.log.
AC=/sys/class/power_supply/AC/online
BAT=/sys/class/power_supply/BAT0
LOG=/home/tarstars/nn-data/battery-guard.log

host_ready() {
  [ "$(cat $AC)" = "1" ] || return 1
  local cap status
  cap=$(cat $BAT/capacity 2>/dev/null || echo 0); status=$(cat $BAT/status 2>/dev/null || echo Unknown)
  [ "$cap" -ge 100 ] && return 0
  case "$status" in Full|"Not charging") return 0;; esac
  return 1
}

if [ "${1:-}" = "--check" ]; then
  if host_ready; then echo "ready: AC on, battery $(cat $BAT/capacity)% $(cat $BAT/status)"; exit 0
  else echo "NOT ready: AC=$(cat $AC), battery $(cat $BAT/capacity)% $(cat $BAT/status)"; exit 1; fi
fi

while sleep 60; do
  if ! host_ready; then
    if pgrep -f "train_ppo_full.py|nn-bot/bench.py|bench_ages.py" > /dev/null; then
      pkill -f "train_ppo_full.py|nn-bot/bench.py|bench_ages.py"
      echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) not ready (AC=$(cat $AC), battery $(cat $BAT/capacity)% $(cat $BAT/status)): host trainings and benches stopped" >> $LOG
    fi
  fi
done
