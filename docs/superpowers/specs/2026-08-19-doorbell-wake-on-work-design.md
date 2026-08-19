# The Doorbell — wake-on-work for the three-agent system (design, 2026-08-19)

**AMENDED 2026-08-19 (owner design decision): the PRIMARY mechanism is the
owner's SENTINEL variant, not the launcher daemon.** Each agent starts a
blocking watcher (`scripts/sentinel.py --me <agent>`) in its own session
background as the last action of every turn-cycle; the process hangs at zero
LLM cost while nothing changes, and EXITS when the agent's actionable set
grows — the harness's background-task mechanism then re-invokes the agent,
warm, with the triggering paths on stdout. Exit codes: 0 = work; 2 =
max-lifetime keepalive (~6 h); 3 = persistent fetch failure. Pidfile guard
against double starts; metered-network backoff; `--notify` mode is the owner's
channel. The §1 launcher daemon is DEMOTED to a cold-start watchdog only
(dead-session detection after reboots); everything else below (actionable-set
definition, debounce rationale, guards, token accounting, rollout) applies to
the sentinel unchanged. Implementation chartered:
`coordination/tasks/20260819-sentinel-wake-on-work.md`.

**Status: DESIGN SAVED at owner request — implementation CHARTERED 2026-08-19
(sentinel variant); standing activation still a separate owner go.** Owner asked for the
description after ruling out LLM polling ("I don't like simple polling, it
wastes tokens"). Activation is a separate owner go; rollout begins in shadow
mode. Ties into the coordd promote-or-park decision dated 2026-08-31
(`coordination/coordd-shadow-runbook.md`).

## The problem, in one sentence

Every hand-off between the three agents currently travels through the owner
clicking "process your inbox" at each of three terminals — the owner is the
message pump, and the only alternative tried so far (an in-session LLM cron)
spends tokens on empty checks.

## The principle

**Poll bytes, not brains.** Git can be asked "anything new?" for ~1 KB and
zero tokens; an LLM session costs tokens the moment it wakes. So: a dumb
watcher polls the git transport as often as we like, and an agent's LLM runs
ONLY when its queue provably contains work. Empty inbox = the model never
runs. The owner's click disappears; the owner's judgment does not.

## Components

### 1. Watcher daemon (`coordd-doorbell`) — plain Python, no LLM

- Runs on the project host under a systemd timer (default every 3 min;
  configurable; backs off to 15 min when the metered-network flag file is
  present, per the standing mobile-internet rule).
- Each tick: `git fetch origin` (fail-soft; alert after 3 consecutive
  failures), then for each agent runs `inbox_sweep` AS A LIBRARY (the same
  code every agent already trusts — no reimplemented loop, per the
  shared-runners rule) and computes the agent's **actionable set**:
  1. new unseen messages addressed to the agent (to or cc);
  2. ack-required messages awaiting THAT agent's acknowledgement;
  3. the agent's own self-addressed `DEFERRED:` queue items still unacked.
- State file records the last-notified actionable set per agent; a wake fires
  only on a NON-EMPTY set that differs from the last-notified one (no re-wakes
  for the same stale item; re-wake happens only when the set changes).

### 2. Debounce — one wake per burst

Message traffic arrives in bursts (measured today: six messages in sixteen
minutes during review rounds). The watcher waits for a **quiet period
(default 60 s) after the newest push** before waking anyone, so one session
handles the whole burst. This is the main token economy over per-message
waking.

### 3. Launcher — one command per agent, lock-guarded

- Per-agent launch command in config, executed in that agent's own worktree:
  - `local_claude_1` / `claude_1`: `claude -p "<ritual prompt>"` headless;
  - `codex_1`: `codex exec "<ritual prompt>"`.
- The ritual prompt is fixed text: run the inbox ritual (sweep → read ALL new
  → act per charters → mark as its own step), obey all standing protocol
  rules, end the session when the queue is drained.
- **Lock file per agent** (with PID + heartbeat): if a session is already
  running, the watcher does NOT launch a second one — the running session's
  own final sweep picks up the delta. Stale locks (no heartbeat > 30 min) are
  broken with a log line.
- Fresh sessions are safe BY EXISTING DESIGN: every agent's re-entry ritual is
  stateless (memory files, task records, queue items) — proven repeatedly on
  2026-08-18/19 when fresh claude_1 sessions resumed mid-task within minutes.

### 4. The owner channel — judgment is never automated

Messages addressed to the OWNER (`user` in `to`/`cc` with an owner-decision
marker: ruling requests, KEEP/REVERT moments, escalations) never wake an
agent. The watcher sends the owner a notification (desktop notify-send and/or
Telegram — owner picks the channel at activation) with the message path and
its plain-words section. The owner stops being the pump but remains the only
judge; nothing in this design makes a decision.

### 5. Guards

- **Wake cap:** default 8 wakes per agent per hour. Two agents in a defective
  correction loop would otherwise burn tokens indefinitely; at the cap the
  lane pauses and the owner is notified. (Today's legitimate review ping-pong
  ran ~15 rounds over ~8 h — well under this cap.)
- **Wake log:** append-only `coordination/doorbell-log.md` — one line per wake
  (UTC, agent, triggering paths) and per suppressed wake (reason). The owner
  audits instead of pumping.
- **Pause file:** `coordination/DOORBELL-PAUSED` stops all wakes instantly;
  the watcher keeps logging what it WOULD have done.
- **Arena exclusion:** the doorbell never triggers Arena actions. Night-mark
  cadences (M-1 style) remain explicitly chartered session work; a doorbell
  wake that finds Arena work in a charter still runs it under that charter's
  own rules — the doorbell itself knows nothing of the Arena.
- **Runaway-content guard:** the watcher reads sweep OUTPUT only; it never
  parses message bodies beyond the sweep's own fields. No content
  interpretation, no prompt injection surface beyond what agents already face.

## What this system deliberately does NOT do

No owner-decision automation. No message-content routing cleverness. No
cloud dependency (runs on the host; GitHub Actions/webhook variant rejected
for now — it needs a public endpoint or a CI runner and adds an outage mode,
while transport-level fetch-polling is already token-free). No persistent
LLM daemon (each wake is a bounded session that drains the queue and exits).

## Failure modes, named

| failure | behavior |
|---|---|
| host offline / asleep | nothing lost — queues are durable git state; next tick catches up |
| fetch fails repeatedly | owner notified after 3 consecutive failures; no wakes on stale state |
| agent session crashes mid-queue | lock goes stale → broken after 30 min → next tick re-wakes on the still-nonempty set |
| correction ping-pong between agents | wake cap pauses the lane + owner notification |
| burst longer than quiet period | second wake after the next quiet gap; batching is best-effort, correctness unaffected |
| watcher itself dies | systemd restarts it; if disabled, the system degrades exactly to today's manual clicking |

## Token accounting

- Watcher: 0 tokens ever (pure Python + git).
- Agent wakes: tokens strictly proportional to real queue work — the same
  work the owner's clicks trigger today, minus repeated owner attention and
  minus any empty-check sessions.
- Compared to LLM cron polling at 10-min intervals: saves every empty check
  (~150 model invocations/day at quiet times) and removes wake latency at
  busy times.

## Rollout plan

1. **Shadow mode (day 1):** watcher runs, logs every would-wake decision,
   launches NOTHING. Owner reviews `doorbell-log.md` against what actually
   happened by hand.
2. **Live for agents (day 2, owner go):** launches enabled; owner channel on;
   caps active.
3. **Review at the coordd decision date (2026-08-31):** promote (fold into
   coordd properly), tune, or park — with two weeks of wake-log evidence.

## Open items for the owner at activation

- Notification channel for owner-items (desktop / Telegram / both).
- Tick interval and quiet period defaults (3 min / 60 s proposed).
- Wake cap value (8/agent/hour proposed).
- Whether claude_1 and codex_1 sessions launch with a token budget hint.

- Authority: owner request in session 2026-08-19 ("propose modification …
  automate this part", then "write down description of this system").
- Author: local_claude_1 (integrator). Implementation estimate: ~half a day
  including tests and shadow mode.
