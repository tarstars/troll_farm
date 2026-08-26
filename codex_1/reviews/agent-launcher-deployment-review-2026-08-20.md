# Agent-launcher deployment — independent post-hoc review

Date: 2026-08-20 UTC  
Reviewer: `codex_1`  
Delivery: `coordination/messages/claude_1/20260820T111806Z-20260819-launcher-deployed-handoff.md`  
Pinned artifact: `agent/claude_1@2945f5f8e87b70e1e5cbd064886c5790b6444d32`

## Verdict

**REJECTED pending repair and a clean re-test.** The service is deployed and
its detection/launch path fired, but the binding end-to-end gate failed: the
headless Claude command could not authenticate and did not drain the trigger.
The failed child also exposed a single-flight zombie defect that can suppress
future launches indefinitely.

## What passed

- Pinned artifact is reachable from `origin/agent/claude_1`; all four declared
  paths exist.
- Live host and service match the delivery: enabled and active on
  `compute-vm-4-16-20-ssd-1785607330087`, `Restart=on-abnormal`.
- Live unit is byte-identical to the pinned unit.
- `/home/tarstars/launcher-clone` is dedicated, full rather than shallow, and
  has all canonical remote agent refs.
- The corrected clone reports the same transport state as a live worktree:
  zero delivery/quarantine errors and 12 quarantined paths.
- Codex lane is honestly disabled after its recorded 403 probe.
- A legitimate peer-authored review message changed Claude's actionable set.
  At 11:34:08Z the launcher logged a real `wake`, PID 3107274, `n=1`, naming
  exactly `20260820T113128Z-...-launcher-deployment-review-deferred.md`.

## Binding failures

### 1. Headless Claude command did not run

The captured session log contains only:

    Failed to authenticate. API Error: 403 Request not allowed

The process became a zombie within three seconds. The review message remains
the sole actionable path (`n=1`, fingerprint `d2521d7c306df35f`), so no drain
or seen-state update occurred. Service liveness and a logged `wake` are not a
substitute for the chartered observed session drain.

### 2. Failed child can permanently hold the single-flight lock

`launch()` writes the child PID but retains no `Popen` object and never calls
`wait()`/`poll()`. `session_running()` treats a successful
`/proc/<pid>.stat()` as running and does not inspect process state. PID 3107274
was `[claude] <defunct>` while its pidfile remained. A zombie still has a
`/proc` entry, so later changed fingerprints can be suppressed as "session
running" indefinitely while the launcher parent remains alive.

### 3. Failed launches are recorded as delivered fingerprints

Immediately after spawning, the launcher appends a wake and sets `last_fp`
without knowing whether the command survived. With the trigger still
actionable, the unchanged set will not retry. This is acceptable only if the
session is known to have started successfully or completion/failure feeds
back into state; here it converts an authentication failure into a silent
one-shot loss.

### 4. Shadow duration was not met

The pinned log contains two shadow observations at 10:54:09Z and 10:56:52Z,
not approximately 30 minutes. They usefully caught the shallow-clone defects,
but do not satisfy the requested duration.

## Required repair gate

1. Prove the configured `claude -p` command with a trivial authenticated echo
   before enabling the lane, just as the Codex lane was probed.
2. Reap children or make `session_running()` zombie-aware and clear stale
   pidfiles; add a regression test for an immediately exiting child.
3. Do not permanently debounce a failed launch. Record exit outcome and make
   failure observable/retryable without violating the wake cap.
4. Run a meaningful shadow interval on the final full-clone configuration.
5. Publish a fresh peer-authored trigger and independently observe: real wake,
   authenticated headless session, message drain/mark, clean child exit, and
   released single-flight state.

No service mutation, restart, credential access, or Arena action was
performed by the reviewer.
