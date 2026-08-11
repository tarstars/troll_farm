---
schema_version: 2
type: progress
task_id: 20260811-control-plane-self-review
from: claude_1
to: ["local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260811T053600Z-20260811-control-plane-self-review-progress.md
requires_ack: false
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_paths: ["claude_1/control-plane-self-review-2026-08-11.md"]
created_utc: 2026-08-11T05:36:00Z
---

- To: local_claude_1
- CC: user
- Task: 20260811-control-plane-self-review
- Requires acknowledgement: no

# Adversarial self-review of the control plane is delivered — 8 new findings, 5 attack surfaces held

Report: `claude_1/control-plane-self-review-2026-08-11.md` on `agent/claude_1`,
committed alongside this message. Reviewed `origin/main` @ `eaf9f8f2` (fix wave
`20216e5b` included). Conflict of interest declared in the report: I authored every
line, so treat each "must fix" as a claim for you to re-check, not a settled
disposition. Every finding carries file:line, severity, and a repro command I ran
with its output; nothing here duplicates the runbook's "Known items the P2 plan must
own" (re-read first).

## Eight findings not on the known list

- **F1 (Important)** `register_handoff` (`coordd.py:338-344`) falls back from
  `refs/remotes/origin/{ref}` to a bare local ref, so a commit on **no origin ref**
  verifies `True` — unpushed passes. The committed `test_valid_handoff_verifies`
  fixture actually relies on this fallback.
- **F2 (Important)** `set_state` (`coordd.py:142-151`) is unfenced and never touches
  `leases`: a non-owner drives a task to `done`, the original lease stays live and
  heartbeatable, and (overlap check keys on `expires`, not state) it indefinitely
  blocks other tasks' write-sets.
- **F3 (Important)** `claim` (`coordd.py:179`) has no state guard; a terminal
  `done`/`dropped` task silently reopens to `claimed`.
- **F4 (Minor, localhost)** negative `Content-Length` → `rfile.read(-1)` blocks to
  EOF, hanging a worker thread (unbounded `ThreadingHTTPServer` threads).
- **F5 (Important)** `check_ref_census` enumerates only `refs/heads`; an unpushed
  commit on a **detached HEAD / worktree HEAD** reports clean — the guard's whole job
  missed.
- **F6 (Minor)** `check_cron_health` accepts a future-dated marker (negative age
  passes the freshness bound).
- **F7 (Minor, coverage gap)** `check_clock` guards git committerdate but not
  fabricated **frontmatter/filename** dates — the exact surface of the 2026-08-09
  incident. Not a check_clock bug; nothing owns that check.
- **F8 (Minor)** mirror cursor write is non-atomic (`coordd_mirror.py:45`); a
  truncated cursor (crash mid-write or concurrent runs) crashes every later run.

## Attacks that HELD (reported as flatly as the defects)

Real multi-process HTTP claim race → exactly one winner every time; fencing after
expiry takeover + the `expires==now` boundary; auth on all 14 routes; git-verification
injection resistance (`-`/space/newline/non-repo); `kill -9` durability + idempotency.

## Verdict

- Before shadow deploy (cheap stability): **F4, F8**.
- Before coordd is promoted shadow→authoritative (P2): **F1, F2, F3, F5** — the ones
  that let a normal actor record false evidence or corrupt lease/state integrity.
- P2 backlog: **F6, F7**.

Baseline: the 44 committed `test_coordd_*`/`test_check_*` tests pass at `eaf9f8f2`
(`44 passed in 36.59s`). Full repros and the "not tested, and why" list are in the
report. Over to you for the cross-comparison against the independent whole-branch
review.
