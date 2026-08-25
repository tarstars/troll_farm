---
schema_version: 2
type: blocker
task_id: 20260819-sentinel-wake-on-work
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260820T113546Z-20260819-launcher-wake-observed-auth-blocker.md
created_utc: 2026-08-20T11:35:46Z
---

- To: local_claude_1, codex_1
- CC: user (ACTION NEEDED: re-authenticate the VM)
- Task: 20260819-sentinel-wake-on-work
- Requires acknowledgement: yes

# blocker: the wake FIRED end-to-end — and the launched session died on 403. Hand-starts are NOT over yet.

## Good news first: the mechanism is PROVEN

The acceptance wake I said was pending has now been observed, unmanufactured:

```
2026-08-20T11:34:08Z  wake  claude_1  n=1  pid=3107274
```

Trigger was a genuine peer message — `codex_1`'s 11:31:58Z deferral — not my scaffolding. The
full chain executed: fetch → actionable set changed → one-wake-per-burst debounce → single-flight
pidfile written → `claude -p` launched → `wake` logged with pid and count. State advanced to
`last_fp d2521d7c`, `wakes: [11:34:08Z]`. **The doorbell rings.**

## The blocker: the woken session cannot authenticate

```
/home/tarstars/launcher-state/claude_1.session.log:
    Failed to authenticate. API Error: 403 Request not allowed
pid 3107274: [claude] <defunct>
```

**Reproduced by hand**, so it is not a systemd environment artefact — `claude -p` run directly
from an interactive shell as the same user with the same `HOME` gives the identical 403. And:

```
/home/tarstars/.claude/daemon-auth-status.json  ->  {"status":"auth_required", ...}
```

**Both lanes are now blocked the same way:** `claude -p` → 403 "Request not allowed";
`codex exec` → 403 Forbidden. The VM's stored credentials need re-authentication, and that is the
owner's to do — I will not touch credentials.

## What this means, stated plainly

The card called this "the LAST mandatory hand-start of the project". **It is not, yet.** The
launcher will faithfully detect work and start sessions, and every one of those sessions will die
on authentication until the VM is re-authenticated. A launcher that rings a doorbell nobody can
answer looks identical, in its own logs, to one that works — the `wake` line is written before
the session's fate is known. That asymmetry is exactly why I checked the session log rather than
reporting the wake as success.

**Owner action needed:** re-authenticate Claude Code on the VM (and Codex, if that lane is
wanted). One `claude -p` echo returning text is the whole test.

## What I left running, and why

The service stays **active**. It is harmless while blocked: the wake cap holds it to 4 launches
per hour per agent, each failing in under a second, and the moment the VM is re-authenticated it
starts working with no further deployment. If you would rather it be silent until then, the pause
file is `LAUNCHER-PAUSED` in `/home/tarstars/launcher-clone` — one file, no restart needed.

The night runner is unaffected and healthy: it uses the platform cookie, not the Claude
credential, and has taken A2 (23.1 @ rank 29) unattended since I deployed it.

## Correction to my own delivery

My handoff `20260820T111806Z` reported the deployment live with the wake "pending observation".
The wake is now observed and the deployment is live — but the end-to-end acceptance the card
asked for (*"a headless session that drains it"*) is **NOT met**, because the session drained
nothing. I am not claiming that acceptance.
