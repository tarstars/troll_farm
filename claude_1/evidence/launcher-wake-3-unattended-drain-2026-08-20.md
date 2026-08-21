# Wake #3 — first unattended drain by a launcher-started session

Author: claude_1 (this file was written BY the launched session it describes).
Host: `compute-vm-4-16-20-ssd-1785607330087`. All timestamps UTC, `date -u`.

## 1. Provenance — this session was started by the launcher, not by a human

`agent-launcher.service` journal line that started me:

```
Aug 20 13:45:56 compute-vm-4-16-20-ssd-1785607330087 python3[3286799]:
  {'at': '2026-08-20T13:45:56+00:00', 'event': 'wake', 'agent': 'claude_1',
   'pid': 3293323, 'n': 1,
   'paths': ['coordination/messages/local_claude_1/20260820T134159Z-20260819-launcher-full-permissions-ruling.md']}
```

Process ancestry read from inside this session (`ps -o ppid=,comm=` walked up):

```
pid=3295930 comm=bash        <- my Bash tool
pid=3293323 comm=claude      <- me; == the pid the launcher logged
pid=3286799 comm=python3     <- agent_launcher.py
pid=1       comm=systemd
```

The launched pid in the launcher's own log and my process ancestor are the same
number, and the ancestor chain terminates at `systemd` — no interactive shell,
no tty, no human in the chain. The `paths` field shows the launcher woke me on a
real peer message, not a probe.

## 2. The permission change is live and is what made the drain possible

`/home/tarstars/launcher-config.json`, claude_1 lane `command` array now ends in
`--dangerously-skip-permissions` (owner ruling of 13:41:59Z: "I want to give it
all permissions"; posture = mechanism trusts, protocol governs). The lane still
runs through `/home/tarstars/bin/claude-proxy` (egress `10.77.0.1:3128`).

Capability check run inside this session, against the exact operations that were
DENIED on wakes #1 (12:38:16Z, pid 3203009) and #2 (12:47:15Z, pid 3218751):

| operation | wake #1 / #2 | wake #3 (this session) |
|---|---|---|
| `git status` / `git log` / `git show` | allowed | allowed |
| `git fetch origin` | DENIED | allowed — ran, fetched `d3175123..11bdd498` |
| `python3 scripts/inbox_sweep.py --fetch` | DENIED | allowed — ran, exit 1 with 1 unacked |
| file write (`Write` / heredoc) | DENIED | allowed — this file exists |
| `git commit` | DENIED | allowed — see §4 |
| `git push` | DENIED | allowed — see §4 |

## 3. The queue I drained

Sweep at 13:46Z (`python3 scripts/inbox_sweep.py --me claude_1 --fetch`, exit 1):

- authority: 9 remote refs, 1640 authoritative messages (691 legacy, 937 v2)
- immutable-path collisions 0 · delivery errors 0 · quarantine errors 0 · quarantined 12
- **new (unseen): 1** — `local_claude_1/20260820T134159Z-20260819-launcher-full-permissions-ruling.md`
- **unacknowledged, ack required: 1** — the same message

Zero-unacknowledged is not zero-unread, so both lists are reported above.
Tooling was diffed against `origin/main` AND `origin/agent/local_claude_1` before
the sweep: `scripts/` and `tests/` identical on all three (no drift this wake).
`coordination/quarantine.json` diffed byte-identical against the coordinator's
authoritative blob — in sync, 12 entries.

## 4. What this session did, unattended, in ritual order

1. sweep `--fetch` (above)
2. read the one new message in full
3. published `ack` for the ruling, and the delivery `handoff` discharging the
   launcher deploy card
4. ran `inbox_sweep.py --mark` as its own step, after reading
5. committed and pushed everything to `agent/claude_1` via
   `scripts/publish_outbox.sh` (lint `--staged` armed as the gate)
6. left the worktree clean

## 5. Honest limits of this evidence

- It proves ONE unattended end-to-end drain of a ONE-message queue. It does not
  prove behaviour on a contended queue, on a lint rejection, or on a merge conflict.
- The wake cap (4/h), pause file, single-flight lock and debounce are unchanged and
  were NOT re-tested this wake; they were verified during the 10:38Z–11:48Z shadow
  and live rounds.
- Full permissions mean the mechanism no longer prevents an out-of-scope action by a
  launched session. Per the owner's ruling that is intentional and is now governed by
  protocol and the git record alone. The starvation postmortem stands: a wake that
  changes nothing still logs a green line, so wake QUALITY must be judged by drained
  queues, not wake counts.
- The codex_1 lane remains `enabled: false` (403 from `codex exec` on this host);
  this wake changes nothing about it.
