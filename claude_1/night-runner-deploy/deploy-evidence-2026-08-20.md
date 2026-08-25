# night_runner VM deployment — evidence (claude_1, 2026-08-20)

Card: `local_claude_1/20260820T054217Z-...-vm-runner-deploy-card.md` (owner-directed).
The runner itself is `local_claude_1`'s artifact and was **not modified**; this records the
deployment only.

## Reconcile (step 1) — CLEAN

    state door1-night-state.json : submissions=[A1 41165297 @2026-08-20T05:18:28+00:00], reads=[]
    ledger door1-night-2026-08-20.md : one row "| A1 | A challenger | 05:18:28Z | 41165297 | (at read) ..."

State and ledger agree; no ledger row missing from state; nothing appended. No double-submit
exposure. Checked BEFORE the service was created.

## Cookie (step 2) — already on host, never committed

    absent from checkout; found at /home/tarstars/prj/troll_farm/cgauto/cg_session.txt
    copied to the runner checkout, chmod 600
    .gitignore:20 = cgauto/cg_session.txt ; `git status` clean after copy

No owner request was needed.

## Verification (step 3)

    $ python3 cgauto/night_runner.py --state local_claude_1/door1-night-state.json \
        --ledger local_claude_1/door1-night-2026-08-20.md --once --dry-run
    not due: 30m elapsed          (exit 0, at 05:48:00Z; A1 window is 115 min)

    earliest read 07:13:28Z · forced read 08:08:28Z

Push path proven with the real credential and branch: handshake commit 961aa103 pushed to
`agent/local_claude_1` then fast-forwarded to `main` — the same sequence `git_publish()` performs.

## Service

    unit      /etc/systemd/system/night-runner.service  (copy in this directory)
    state     active (running), enabled (boot-persistent)
    host      compute-vm-4-16-20-ssd-1785607330087
    started   2026-08-20T05:48:53Z, Main PID 2912820
    checkout  /home/tarstars/prj/troll_farm-claude_1-lfs on branch agent/local_claude_1

## Deviation: Restart=on-abnormal, not Restart=always

The card said restart-always. The runner HALTs nonzero on any anomaly and its docstring states
"NO automatic retry of submissions ... an ambiguous double-submission costs the night".
Restart=always would restart after a deliberate HALT and re-attempt the submission the HALT exists
to prevent. `on-abnormal` restarts crashes (signal/OOM/timeout), leaves a HALT stopped for a
human, and does not respawn after the clean "block complete" exit (the loop breaks when
reads >= plan, so a restart is also harmless).

## Disk: the VM was at 100% and the deploy was blocked

    before: /dev/vda1 19G size, 19G used, 150M avail (100%)  -> ENOSPC creating a checkout
    freed : /tmp/claude-1000/.../0cf0e1a1-.../ dead session scratch from Aug 11 (674M)
    avoided: a new ~430M checkout, by repointing my own stale clean agent/claude_1-lfs-probe
             worktree (last commit 2026-08-02, already published) to agent/local_claude_1
    after : 1.7G avail (92%)

Untouched: ~/.cache/troll-farm (475M) and every other agent's worktree. Standing risk: 19G is
tight for eight checkouts of this repository; this will recur.
