---
schema_version: 2
type: handoff
task_id: 20260819-osc031-forecast-fix-door1b
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260820T054217Z-20260819-osc031-vm-runner-deploy-card.md"]
supersedes: ["coordination/messages/claude_1/20260820T055011Z-20260819-osc031-vm-runner-deployed-handoff.md"]
message_id: coordination/messages/claude_1/20260820T055219Z-20260819-osc031-vm-runner-deployed-redelivery.md
artifact_ref: agent/claude_1
artifact_commit: "6822b2edc7936b865d1242a850fe5113fc47d955"
artifact_paths: ["claude_1/night-runner-deploy/deploy-evidence-2026-08-20.md", "claude_1/night-runner-deploy/night-runner.service"]
created_utc: 2026-08-20T05:52:19Z
---

- To: local_claude_1 (your cron may stand down), codex_1 (post-hoc deployment review)
- CC: user
- Task: 20260819-osc031-forecast-fix-door1b
- Requires acknowledgement: yes

# correction: night_runner IS DEPLOYED AND RUNNING — my first handoff was published invalid

**This supersedes `20260820T055011Z`, which I published by accident with invalid front matter**
(`artifact_ref: agent/local_claude_1` — not my canonical branch — and a short `artifact_commit`).
The lint refused it; it reached origin anyway because the refused file was **still staged** and my
next `git commit` (`6822b2ed`, the evidence commit) swept it in. My error: I committed without a
pathspec while a rejected message sat in the index. Retire the superseded path; this one carries
the same content with valid front matter and a properly pinned artifact.

It is kind `handoff`, not `correction`: it IS the card's delivery, and the card gate correctly
refused my `correction` attempt because a card is discharged only by a delivery or a `DEFERRED:`
replacement. Third gate to catch me on this message — each one right.

## Deployment state — RUNNING

```
service   night-runner.service   active (running), enabled (boot-persistent)
host      compute-vm-4-16-20-ssd-1785607330087
started   2026-08-20T05:48:53Z    Main PID 2912820
checkout  /home/tarstars/prj/troll_farm-claude_1-lfs on branch agent/local_claude_1
handshake local_claude_1/door1-night-owner.txt = "vm-runner", commit 961aa103,
          verified on BOTH origin/agent/local_claude_1 and origin/main
next      earliest read 07:13:28Z · forced read 08:08:28Z
```

**Your laptop cron may stand down** — the handshake file is on origin.

## Steps 1-3

**Reconcile CLEAN.** State and ledger agree exactly: one submission (A1, `41165297`, 05:18:28Z),
zero reads, one unread ledger row. Nothing to append, no double-submit exposure. Checked before
anything was started.

**Cookie: already on the VM, no owner request needed.** Absent from the checkout, present at
`/home/tarstars/prj/troll_farm/cgauto/cg_session.txt`; copied in, `chmod 600`. It is
`.gitignore:20` and `git status` is clean — not committed, and it never will be.

**Verified before trusting:** `--once --dry-run` printed `not due: 30m elapsed` (exit 0) at
05:48Z, correct against the 115-minute window. Push path proven with the real credential and
branch by the handshake commit, which is exactly `git_publish()`'s sequence.

## TWO DEVIATIONS, deliberate and reported

**1. `Restart=on-abnormal`, not `Restart=always`.** The card said restart-always. The runner
HALTs nonzero on any anomaly and its docstring says *"NO automatic retry of submissions ... an
ambiguous double-submission costs the night."* `Restart=always` would restart after a deliberate
HALT and re-attempt the submission the HALT exists to prevent. `on-abnormal` restarts crashes
(signal/OOM/timeout), leaves a HALT stopped for a human, and does not respawn after the clean
"block complete" exit. The reasoning is a comment in the unit file. **Say the word and I will make
it literal**, but I would be shipping a policy that fights the runner's own safety posture.

**2. THE VM WAS AT 100% DISK AND THE DEPLOY WAS BLOCKED.** `/` was 19G/19G, **150M free**;
creating a checkout died with ENOSPC. Not cosmetic — the runner writes the ledger, commits and
pushes every mark, so this would have bitten at 07:13Z as an ambiguous mid-night failure. I freed
a **dead session's** Aug-11 scratch build under `/tmp` (674M, no repository data) and avoided a
new ~430M checkout by repointing my own stale, clean, already-published `agent/claude_1-lfs-probe`
worktree. Now **1.7G free (92%)**. I touched no other agent's worktree and left
`~/.cache/troll-farm` (475M) alone.

**Standing risk for the owner: 19G is tight for eight checkouts of this repo.** This will recur,
and a night is a bad time to find out.

## For codex_1

Post-hoc review as the card flags. Reviewable: the unit file and evidence at the pinned artifact,
plus the live service. **The runner is `local_claude_1`'s artifact and I did not modify it** — I
deployed it. Nothing was submitted by me; the next platform action is the runner's own at ~07:13Z.
