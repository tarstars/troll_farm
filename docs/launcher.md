# The agent launcher — wake-on-work for agent sessions (no-LLM doorbell)

What it is: a plain Python loop (`scripts/agent_launcher.py`) that polls git
bytes, computes each configured agent's actionable queue with the shared
`inbox_sweep` (run as a subprocess, per-agent seen-state materialized from
that agent's own canonical branch), and launches the agent's headless session
when — and only when — the queue is non-empty and changed since the last wake.
Zero LLM cost while idle. Design: the doorbell spec
(`docs/superpowers/specs/2026-08-19-doorbell-wake-on-work-design.md`, launcher
lane of the hybrid redirect).

Guards: per-agent wake cap per hour · single-flight lock (no second session
while one runs) · quiet-period debounce (one wake per burst) · pause file
(`LAUNCHER-PAUSED` in the launcher clone stops all launches instantly) ·
append-only JSONL wake log in the state dir. `--dry-run` = shadow mode (logs
would-wakes, launches nothing); `--once` = single tick.

Deployment (see `coordination/launcher/`): a DEDICATED clone (never an
agent's live worktree), the config template, and the systemd unit
(`Restart=on-abnormal` — a deliberate exit stays exited). Rollout per the
spec: shadow first, owner-visible log, then live.

What it deliberately does not do: no message-content interpretation, no
owner-decision automation, no Arena actions, no waking on unchanged stale
queues, no waking an agent whose previous session is still running.
