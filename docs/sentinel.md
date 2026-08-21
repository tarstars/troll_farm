# The sentinel — how an agent waits for work without spending a token

`scripts/sentinel.py` is the doorbell. An agent starts it in its session
background as the last action of a turn-cycle; it blocks, costing nothing,
while the inbox is quiet, and **exits the moment that agent's wake set grows**
— printing the triggering message paths. The wake set is news from someone
else, not the whole queue: see *What wakes it*, below. The harness sees a background
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

## What wakes it — and why that is not the whole queue

The sentinel does **not** decide what counts as work. It calls
`inbox_sweep.actionable_set()`, the same function the sweep's own report is
computed from, and reads `SweepState.wake_paths` — the **wake set**, printed by
the sweep CLI under `wake set (N):`.

Two different questions, one sweep. `actionable_paths` answers *what do I owe*:

1. unseen messages addressed to the agent (`to` or `cc`);
2. ack-required messages awaiting THAT agent's ack;
3. the agent's own self-addressed `DEFERRED:` queue items, still unacked;
4. a broken transport — a collision, delivery error or quarantine error means
   no inbox state above it can be trusted, which is itself work.

`wake_paths` answers *is there news*, and is always a **strict subset**: nothing
may wake an agent that the sweep would not also show it. Per the owner rule of
2026-08-21 (*"claude shouldn't awake without incoming emails"*, protocol §5.1),
`inbox_sweep.wakes_recipient()` drops four classes:

1. **anything the agent wrote itself.** Its own `DEFERRED:` cards stay in its
   queue as obligations and never ring its own bell. An obligation is not news.
2. **`cc`-only mail.** A `cc` recipient owes no ack (ruling 2026-08-20); waking
   it to read what it does not owe contradicts the same ruling. It reads the cc
   on its next real wake.
3. **an `ack` with `requires_ack: false`** — a courtesy receipt. A verdict,
   ruling or authorization changes the recipient's queue and must be published
   ack-required toward that party (the 2026-08-18 queue-changing rule); published
   that way it wakes. Published as a bare receipt it is read next wake, and peer
   receipt ping-pong terminates instead of sustaining itself.
4. **any shape-valid `DEFERRED:` card, for everyone**, including the peers it
   names in `to`. No peer can discharge another agent's card — only a later
   message of the same agent naming it in `ack_for` does — so the obligation such
   a card appears to place on a peer is one the peer cannot act on. The card
   stays fully visible to everyone as status. An assignment (`CARD:`) addressed
   to its assignee is a different shape and still wakes.

The defect this closes is a composition, not a broken rule. A postponed job must
be a self-addressed ack-required card (08-18); a card is discharged only by
delivering it or by a replacement card (08-19); self-addressed cards became
visible to the sweep (`8c531096`, 08-21). So the discharge of a card is another
card, which re-enters its author's own trigger set. While work is blocked that
set has no fixed point — measured as eight `claude_1` wakes in 102 minutes on
2026-08-21, every one of them legally mail-triggered by its own mail.

Both consumers take the same wake set from the same sweep — `snapshot()` here,
and the `wake set` section of the CLI in `scripts/agent_launcher.py` (which read
`new` + `unacknowledged` before `b6e771f3`). One predicate, so the doorbell, the
launcher and the queue cannot drift.

Reconstructing either set from `scan_authoritative()`, raw message fields,
sweep CLI output, git activity or process activity is forbidden (codex_1's
binding boundary, 2026-08-21). A second predicate that disagrees with the sweep
is worse than none: it wakes agents for work the sweep does not show, or stays
silent on work it does.

**Actionable item 3 is the one self-mail route that is open, and it was closed
until 2026-08-21.** It is a queue route, never a wake route — exclusion 1 above
keeps a card out of its own author's bell.

`inbox_sweep` built its addressed set with `m.sender != me`, so a message an
agent sent to itself never entered that agent's own actionable set.
Measured on a live card: authoritative on origin, `requires_ack: true`,
addressed to `claude_1`, sent by `claude_1` — and absent from
`actionable_set("claude_1").actionable_paths`. The deferral rule's "self-address
it so your own next sweep surfaces it" was prose, not mechanism, and two of my
wakes reported "queue drained" with live cards outstanding.

Repaired in the shared predicate, never in the sentinel (codex_1's card-2
review made both the defect and its location blocking). `inbox_sweep.is_deferral_card()`
admits a self-authored message only when it has the full shape the outbox lint
already enforces on publication — a line-start `DEFERRED:` marker,
`requires_ack: true`, and its own sender among `to`. Both sides now read one
definition of the marker so they cannot drift.

Two consequences worth knowing:

- **Ordinary self-mail stays inert.** An agent cannot put arbitrary work in its
  own queue by writing to itself; only the deferral shape opens the route. A
  negative-control test holds that line.
- **Your own card is never "new", only outstanding.** An agent has read what it
  wrote, so a self-authored message cannot enter the unseen set — otherwise one
  `--mark` would retire a job that is still undone. The card leaves the
  actionable set exactly when something of yours names it in `ack_for`: the
  delivery handoff, or the next `DEFERRED:` replacement card. It never enters
  the wake set at all, and since 2026-08-21 an unchanged standing card is left
  standing rather than re-issued per wake: a blocked card names its
  `UNBLOCK-SIGNAL:` and is replaced when that observable changes, when work
  starts, or once per 24 h.

**Growth, not presence.** The baseline is the wake set snapshotted at start;
the sentinel wakes only on paths that were not in it. Mail already sitting in the inbox when
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
| a stale pidfile from a killed sentinel | the lock died with its process, so the next start takes it; a log line on stderr names the pid that left it |
| two starts race | ownership is an exclusive `flock`, so the kernel picks exactly one winner; every loser exits 1 and touches nothing |
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

`tests/test_sentinel.py`, 18 tests, each control observed firing both ways
where the charter names both directions: work arrives → exit 0 with exactly
the new paths; **mail for a different agent → keeps hanging**; keepalive → 2;
injected fetch failure → 3; non-consecutive failures → *not* 3; double start →
1 with the first instance untouched; stale pidfile → broken with a log line;
`inbox-seen.json` byte-identical across a full run; the git verb set of a run
is read-only; `snapshot()` equals the sweep's own wake set.

Three of those are the card-2 review's blocking findings, and each was watched
failing against the unrepaired code before the repair existed:

- **my own `DEFERRED:` card enters my queue** — published after the baseline,
  observed in `actionable_paths` (against the old predicate: absent). It was
  also a wake until the owner rule of 2026-08-21 retired that half; the sweep
  tests now pin both directions, queue yes and bell no;
- **ordinary self-mail does not wake me** — the negative control that keeps the
  route narrow;
- **32 simultaneous starters leave exactly one owner** — forked from a warm
  interpreter and released from one barrier, because real interpreters cannot
  align on a microsecond window. The old check-then-write scored two winners
  and one crash (`W E W L L …`): every starter staged through the same
  `.pid.tmp` name, so one starter's `replace()` pulled the file out from under
  another.

The shared predicate's own route is covered in `tests/test_inbox_sweep.py`: the
card is actionable for its owner, is never merely "unseen", is discharged by the
delivery handoff naming it in `ack_for`, and a deferral addressed only to a peer
stays out of my queue. Six further tests pin the wake set against the four
exclusions, and `tests/test_agent_launcher.py` carries a regression pin that the
OLD parser sees a card and the new one does not.
