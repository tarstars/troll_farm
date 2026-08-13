---
schema_version: 2
type: handoff
task_id: 20260811-control-plane-self-review
from: local_claude_1
to: ["claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260811T052004Z-20260811-control-plane-self-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: faee8545634d788b0ae8c87eafed293d668dac52
artifact_paths: ["coordination/tasks/20260811-control-plane-self-review.md"]
created_utc: 2026-08-11T05:20:04Z
---

- To: claude_1
- CC: user
- Task: 20260811-control-plane-self-review
- Requires acknowledgement: yes

# Assignment: adversarial self-review of your control-plane implementation

Task record: `coordination/tasks/20260811-control-plane-self-review.md` (pinned above).
The owner will point you at this message and verify you processed it.

You implemented plan Tasks 2–17 (coordd, coordctl, mirror, guards, deploy). Your job
now is to ATTACK that work as a hostile reviewer. Assume you remember nothing:
re-derive everything from the repository, not from memory. You are the author, so
this review is a declared conflict of interest — say so in the report, and let it
make you harsher, not kinder.

## Setup

Work in your own checkout (never a shared one): `git fetch origin` and review the
code at `origin/main` (trunk `eaf9f8f2` or later). Note two things happened after
your implementation: a fix wave (`20216e5b`) already repaired HTTP error handling,
deploy-doc token ownership, XSS escaping, token comparison, fetch timeout, and
systemd `Wants=`; and `coordination/coordd-shadow-runbook.md` has a section
**"Known items the P2 plan must own"** listing every defect already on file
(including write-set prefix normalization and non-monotonic generations).
**Read that section first and do not re-report anything on it.** Your review's value
is measured by what you find that is NOT already known.

## Rules

Review-only: find problems, fix nothing. Every finding needs file:line, severity
(Critical/Important/Minor), and a repro command you RAN with its output — a claim
without executed evidence does not go in the report. No commits to
`session-2026-07-01` or `main` (the plan-execution grant has ended). No Arena or
platform actions. Do not touch other agents' namespaces.

## Attack surfaces, in priority order

1. Claim atomicity under REAL concurrency: the existing race test is 20 threads in
   one process. Attack a live `coordd serve` over HTTP with multiple OS processes
   claiming one task simultaneously. Exactly one winner, every time?
2. Fencing: bypass attempts through every endpoint — heartbeat/release/handoff with
   a stale generation after an expiry takeover; re-claim by the old owner; the
   expires == now boundary.
3. Auth and HTTP robustness beyond the fix wave: huge bodies, missing
   Content-Length, malformed JSON, slow-loris-ish partial requests, concurrent
   requests during a slow git verification, unauthenticated access to every route.
4. Idempotency and durability: concurrent same-key events from two processes;
   kill -9 the server mid-claim and restart — leases, generations, events intact?
5. Git verification: refs/paths/commits starting with '-', containing spaces or
   newlines; a ref that exists locally but not on origin; a repo_dir that is not a
   git repo at all.
6. Mutation-test the three guards (a guard is not finished until observed failing):
   in scratch repos, fabricate the condition each guard exists to catch and confirm
   exit 2; then break each guard's subject in a way it SHOULD catch but you suspect
   it will not.
7. The mirror: cursor corruption, a message file that appears then disappears
   between runs, concurrent mirror invocations.
8. The docs you wrote or touched: does anything in deploy/README.md or the runbook
   fail when actually pasted on this VM?

Also list explicitly what you did NOT test and why.

## Deliverables (per the task record)

Full report at `claude_1/control-plane-self-review-2026-08-11.md` committed on
`agent/claude_1`, plus a `progress` message from your namespace announcing it —
lint first, as its own command, and check `$?`. End the report with a verdict:
which findings must be fixed before shadow-mode deployment, and which wait for P2.
