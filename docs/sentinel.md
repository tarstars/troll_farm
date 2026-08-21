# The sentinel — how an agent waits for work without spending a token

`scripts/sentinel.py` is the doorbell. An agent starts it in its session
background as the last action of a turn-cycle; it blocks, costing nothing,
while the inbox is quiet, and **exits the moment that agent's actionable set
grows** — printing the triggering message paths. The harness sees a background
process finish and re-invokes the agent, warm, with the paths already on
stdout.

No model runs while there is no mail. That is the whole point: **poll bytes,
not brains.**

Charter: `coordination/tasks/20260819-sentinel-wake-on-work.md`.
Design: `docs/superpowers/specs/2026-08-19-doorbell-wake-on-work-design.md`.

## Starting it

```bash
scripts/sentinel.py --me claude_1
```

Run it from anywhere inside the worktree; it locates the repository root
itself and works from there. Defaults: a tick every **45 s**, keepalive at
**6 h**, exit 3 after **5** consecutive transport failures, pidfile at
`<root>/<me>/.sentinel.pid`.

| flag | meaning |
|---|---|
| `--me AGENT` | required; whose inbox is being watched |
| `--interval SECONDS` | seconds between fetch-and-recompute ticks (45) |
| `--metered-flag PATH` | repo-relative flag file (`coordination/METERED-NETWORK`) |
| `--metered-interval SECONDS` | tick length while that file exists (600) |
| `--max-lifetime SECONDS` | keepalive exit 2 (21600) |
| `--max-fetch-failures N` | consecutive failures before exit 3 (5) |
| `--pidfile PATH` | override the pidfile location |
| `--notify` | owner channel: notify, never exit on work |

## Exit codes are the entire interface

| code | meaning | what the agent does |
|---|---|---|
| **0** | work arrived. stdout lists the triggering paths, one per line. A `transport: ...` line instead means the sweep can no longer trust its own inbox state. | run the inbox ritual |
| **1** | refused to start: a live sibling already holds the pidfile. Nothing was touched. | leave the running one alone |
| **2** | keepalive: `--max-lifetime` elapsed with nothing new. | do a liveness sweep, restart the sentinel |
| **3** | N consecutive fetch-or-sweep failures. | report transport trouble; do **not** guess at stale state |

## The restart ritual

The sentinel is single-shot by design — it exits, and it is the agent's job to
start a fresh one. At the end of every turn-cycle, after `--mark` and after
the push:

```bash
scripts/sentinel.py --me <me> &     # or the harness's background-task mechanism
```

On exit 2, sweep first (the keepalive proves nothing arrived, not that
nothing is owed), then restart. On exit 3, do not restart blindly: find out
what is wrong with the transport first.

## What "actionable" means — and why it is not defined here

The sentinel does **not** decide what counts as work. It calls
`inbox_sweep.actionable_set()`, the same function the sweep's own report is
computed from, and reads `SweepState.actionable_paths` / `is_actionable`. That
set is:

1. unseen messages addressed to the agent (`to` or `cc`);
2. ack-required messages awaiting THAT agent's ack;
3. the agent's own self-addressed `DEFERRED:` queue items, still unacked;
4. a broken transport — a collision, delivery error or quarantine error means
   no inbox state above it can be trusted, which is itself work.

Reconstructing this from `scan_authoritative()`, raw message fields, sweep CLI
output, git activity or process activity is forbidden (codex_1's binding
boundary, 2026-08-21). A second predicate that disagrees with the sweep is
worse than none: it wakes agents for work the sweep does not show, or stays
silent on work it does.

**Growth, not presence.** The baseline is snapshotted at start; the sentinel
wakes only on paths that were not in it. Mail already sitting in the inbox when
the sentinel starts never wakes anyone — the agent was already looking at it.
A set that *shrinks* is not a wake either.

## What it deliberately does not do

- **No LLM, anywhere.** Pure Python and git.
- **No message-body interpretation** beyond the fields the sweep itself parses.
  There is no new prompt-injection surface.
- **Read-only.** It fetches; it never merges, never marks, never writes any
  agent's `inbox-seen.json`. A test asserts the git verb set of a whole run.
- **No decisions.** Owner rulings go to the owner. See `--notify`.
- **No Arena action, ever.**
- **Not self-activating.** Adoption into the standing ritual is a separate
  owner go (design §Rollout); until then this tool is run by hand.

## `--notify` — the owner channel, deliberately a stub

`--notify` watches mail addressed to `user` and, on growth, fires
`notify-send` with the paths (logging to stderr when `notify-send` is absent).
It **never exits on work** — the owner is not a process to be woken, and no
agent is launched by it. Keepalive and transport exits still apply.

Two things are consciously *not* implemented and are owner activation items:
distinguishing owner-DECISION mail from ordinary owner mail (that would require
reading bodies, which this tool will not do), and any channel other than
`notify-send` — Telegram in particular.

## Failure modes, named

| situation | behaviour |
|---|---|
| host offline, or asleep | nothing is lost; queues are durable git state and the next tick catches up |
| fetch fails repeatedly | exit 3 after N; the agent reports rather than acting on stale state |
| the sweep itself cannot compute | counted on the same budget as a fetch failure; exit 3 |
| a stale pidfile from a killed sentinel | broken with a log line on stderr, then start proceeds |
| two starts race | the loser exits 1 and touches nothing |
| killed with SIGTERM/SIGINT | pidfile removed; safe to kill at any moment |
| transport breaks while hanging | exit 0 with a `transport:` line — that is work |
| metered network | tick backs off to 10 min while `coordination/METERED-NETWORK` exists |

## The load-bearing assumption, and where it is only half proven

The design rests on one thing: **a background process exiting causes the
harness to re-invoke the agent.** That is verified BY EXECUTION on the Claude
Code harness (`claude_1`, 2026-08-19, active and idle) for
*harness-tracked background tasks exiting 0*. It is **falsified on the Codex
harness** — `codex_1` does not get re-invoked, which is why that lane runs the
launcher daemon instead (`scripts/agent_launcher.py`) and the charter's gate 1
stands answered **MIXED**.

Two limits are still open, and this manual states them rather than letting a
green test suite imply otherwise:

- Survival and wake behaviour under detached shapes — `nohup`, `setsid`,
  systemd — is **unverified even on the Claude harness**, and those are exactly
  the shapes an operator would reach for.
- The controls below prove the sentinel exits at the right moments. They do
  not prove any harness notices.

## Test evidence

`tests/test_sentinel.py`, 15 tests, each control observed firing both ways
where the charter names both directions: work arrives → exit 0 with exactly
the new paths; **mail for a different agent → keeps hanging**; keepalive → 2;
injected fetch failure → 3; non-consecutive failures → *not* 3; double start →
1 with the first instance untouched; stale pidfile → broken with a log line;
`inbox-seen.json` byte-identical across a full run; the git verb set of a run
is read-only; `snapshot()` equals the sweep's own `actionable_paths`.
