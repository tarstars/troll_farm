---
schema_version: 2
type: progress
task_id: 20260811-coordd-shadow-deploy
from: claude_1
to: ["user"]
cc: ["local_claude_1"]
requires_ack: false
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260811T050233Z-20260811-coordd-shadow-deploy-progress.md
created_utc: 2026-08-11T05:02:33Z
---

- To: user
- CC: local_claude_1
- Task: 20260811-coordd-shadow-deploy
- Requires acknowledgement: no

# coordd deployed in SHADOW MODE on the VM (git remains authoritative)

Deployed per `deploy/README.md` + `coordination/coordd-shadow-runbook.md` on
`compute-vm` (this VM, hosts claude_1 and codex_1). Repos pinned to
`origin/session-2026-07-01` HEAD `21bd338d`. Git stays authoritative; coordd
only observes. No trunk commits, no public port, no Arena actions. The token
was never printed and is never in this message.

## systemctl status coordd (excerpt)

```
● coordd.service - coordd coordination control plane (Troll Farm)
     Loaded: loaded (/etc/systemd/system/coordd.service; enabled; preset: enabled)
     Active: active (running) since Tue 2026-08-11 04:59:31 UTC
   Main PID: 957863 (python3)
     Memory: 11.5M
     CGroup: /system.slice/coordd.service
             └─ /usr/bin/python3 /opt/troll_farm/scripts/coordd.py serve
                --db /var/lib/coordd/coordd.sqlite3 --repo /var/lib/coordd/repo.git
                --token-file /etc/coordd/token --host 127.0.0.1 --port 7077
```

`is-active` = active, `is-enabled` = enabled. Listener bound to
`127.0.0.1:7077` only (verified `ss -ltnp`) — no public port.

## /health

`curl -s http://127.0.0.1:7077/health` ->
`{"ok": true, "time": "2026-08-11T05:01:49.048858Z"}`

## Roster registered (runbook step 2)

- `register --agent local_claude_1 --role coordinator` -> `{"agent": "local_claude_1", "compatible": true}`
- `register --agent claude_1` -> `{"agent": "claude_1", "compatible": true}`
- `register --agent codex_1` -> `{"agent": "codex_1", "compatible": true}`

## Regression check (runbook step 7) — both 4xx JSON, no dropped connections

Duplicate task-create:
- create #1 `POST /task {regcheck-dup-20260811}` -> `HTTP 200 {"task_id": "regcheck-dup-20260811", "state": "open"}`
- create #2 (duplicate) -> `HTTP 409 {"error": "task 'regcheck-dup-20260811' already exists"}`

Claim conflict:
- `POST /task {regcheck-claim-20260811}` -> `HTTP 200 {"state": "open"}`
- `claim` by claude_1 -> `HTTP 200 {"generation": 1, "expires": ...}`
- `claim` by codex_1 (conflict) -> `HTTP 409 {"error": "task 'regcheck-claim-20260811' owned by claude_1 until ... (gen 1)"}`

Both error bodies parse as valid JSON (checked with `json.loads`). The two
`regcheck-*` tasks were left in the shadow DB as evidence; the claude_1 lease
self-expires and neither is a real work record.

## Daily dump cron (README closing note) — installed as coordd user

`sudo crontab -u coordd -l`:
```
17 5 * * * /usr/bin/python3 /opt/troll_farm/scripts/coordd.py dump \
  --db /var/lib/coordd/coordd.sqlite3 \
  --out /var/lib/coordd/backup-$(date -u +\%F).sqlite3
```
Dump command dry-run as coordd produced a valid 10-table sqlite backup, then
removed the test file. (README gave no time; 05:17 UTC chosen to echo the
project's historical collection slot.)

## Known-red, per instruction (step 6) — NOT chased

`coordctl doctor` against the agent's own checkout exits 2 by design:
`CRON HAZARD: .../collect_wide.log does not exist` (collector lives on
project_host). Everything else green: clock sane, ref census clean, sacred
source `fff6669b OK`, inbox_sweep digest vs origin/main match.

## Deviations from the README

1. **GitHub SSH auth (routing deviation).** The README's
   `sudo git clone git@github.com:...` and
   `sudo -u coordd git clone --mirror git@github.com:...` both fail on this VM:
   root gets `Host key verification failed` and the `coordd` service user has
   no SSH key/known_hosts. Only `tarstars` holds working GitHub SSH auth.
   Resolution: performed both clones as `tarstars`, then handed ownership —
   `/opt/troll_farm` to `root:root` (world-readable; coordd can read
   `scripts/coordd.py`) and the mirror to `coordd:coordd` at
   `/var/lib/coordd/repo.git`. Both keep the `git@github.com` remote and sit at
   `21bd338d`. End state is byte-identical to the README's intent; only the
   auth path differs. **Recommend README note that root/coordd need github
   known_hosts+key or that clones route through the authed user.**
2. **`coordctl doctor --repo /opt/troll_farm` crashes (exit 1), it does not
   exit 2.** Root-owned `/opt` + doctor running as `tarstars` trips git's
   "detected dubious ownership" guard, so `check_clock`'s `git for-each-ref`
   dies with 128 before the cron check is even reached. Ran doctor against the
   agent's tarstars-owned checkout instead (`~/prj/troll_farm-plan`), where it
   exits 2 as designed. **Recommend the runbook's "doctor outside a repo root"
   carry be widened to cover a root-owned service repo — either add
   `safe.directory` handling or document that agents run doctor against their
   own checkout, not `/opt/troll_farm`.**
3. Dump-cron time and `%`-escaping not specified by the README (noted above).

## Not done / out of scope (as instructed)

Token never printed; no public port; no Arena, storage, or CI actions; no
trunk commits. Weekly comparison (runbook step 5) and P2 proposal (step 6)
remain owner/coordinator-driven and were not started.
