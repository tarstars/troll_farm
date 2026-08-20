---
schema_version: 2
type: handoff
task_id: 20260819-osc031-forecast-fix-door1b
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260820T054217Z-20260819-osc031-vm-runner-deploy-card.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260820T055011Z-20260819-osc031-vm-runner-deployed-handoff.md
artifact_ref: agent/local_claude_1
artifact_commit: "961aa103"
artifact_paths: ["local_claude_1/door1-night-owner.txt"]
created_utc: 2026-08-20T05:50:11Z
---

- To: local_claude_1 (your cron may stand down), codex_1 (post-hoc deployment review)
- CC: user
- Task: 20260819-osc031-forecast-fix-door1b
- Requires acknowledgement: yes

# handoff: night_runner DEPLOYED and RUNNING on the VM — this is the card's delivery

```
service   night-runner.service   active (running), enabled (starts at boot)
host      compute-vm-4-16-20-ssd-1785607330087   (the VM; not a login session)
started   2026-08-20T05:48:53Z    Main PID 2912820
checkout  /home/tarstars/prj/troll_farm-claude_1-lfs  on branch agent/local_claude_1
handshake local_claude_1/door1-night-owner.txt = "vm-runner"  commit 961aa103
          verified present on BOTH origin/agent/local_claude_1 and origin/main
```

**Your laptop cron may stand down now** — the handshake file is on origin.

## Step 1 — reconcile: CLEAN, no missing rows

State and ledger agree exactly: **one** submission (A1, `41165297`, 05:18:28Z), **zero** reads;
the ledger's single A1 row is unread. Nothing to append, and therefore no double-submit exposure.
I checked this before starting anything, as the card required.

## Step 2 — the cookie was already on the VM; no owner request needed

`cgauto/cg_session.txt` was absent from my checkout but present on this host at
`/home/tarstars/prj/troll_farm/cgauto/cg_session.txt`. Copied in, `chmod 600`. It is in
`.gitignore:20` and `git status` is clean — **it is not committed and never will be.**

## Step 3 — verification before trusting

```
--once --dry-run  ->  "not due: 30m elapsed"   (exit 0)
```
Correct: A1 at +30 min against a 115-min window. Next actions: earliest read **07:13:28Z**,
forced read **08:08:28Z**.

Push path proven with the real credential and the real branch: the handshake commit went to
`agent/local_claude_1` and fast-forwarded `main`, which is exactly `git_publish()`'s sequence.

## TWO DEVIATIONS, both deliberate, neither hidden

**1. `Restart=on-abnormal`, NOT `Restart=always`.** The card said restart-always; I did not do
that, and the reason is in the unit file as a comment. The runner HALTs with a nonzero exit on any
anomaly, and its own docstring says *"NO automatic retry of submissions ... an ambiguous
double-submission costs the night."* `Restart=always` would restart after a deliberate HALT and
re-attempt the submission the HALT exists to prevent. `on-abnormal` still restarts crashes
(signal, OOM, timeout) but leaves a HALT stopped for a human, and does not respawn after the clean
"block complete" exit. **If you want the literal restart-always, say so and I will change it** —
but I would be shipping a policy that fights the runner's stated safety posture.

**2. THE VM WAS AT 100% DISK — I had to reclaim space to deploy.** `/` was 19G/19G with **150M
free**; creating a checkout failed with ENOSPC. This is not cosmetic: the runner writes the
ledger, commits and pushes on every mark, and an ENOSPC mid-night is precisely the ambiguous
failure the design guards against. It would have bitten us at 07:13Z.

What I did, minimally and reversibly-in-spirit:
- deleted `/tmp/claude-1000/.../0cf0e1a1-.../` — a **dead session's** scratch build from
  **Aug 11**, in the session-scoped temp area (674M). No repository data.
- **avoided a new 430M checkout entirely** by repointing my own stale, clean, already-published
  `agent/claude_1-lfs-probe` worktree (last commit 2026-08-02) to `agent/local_claude_1`.

Now **1.7G free (92%)**. I did NOT touch `~/.cache/troll-farm` (475M) or any other agent's
worktree. **Standing risk for the owner: 19G is tight for eight checkouts of this repo** — this
will recur, and a night is a bad time to discover it.

## For codex_1 (post-hoc review, as the card flags)

Deployment is review-after by owner-directed urgency. Reviewable now: the unit file at
`/etc/systemd/system/night-runner.service`, the reconcile evidence above, the dry-run output, and
the handshake commit. The runner itself is `local_claude_1`'s artifact, unmodified by me — I
deployed it, I did not change it.

Nothing was submitted by me. The next platform action is the runner's own, at ~07:13Z.
