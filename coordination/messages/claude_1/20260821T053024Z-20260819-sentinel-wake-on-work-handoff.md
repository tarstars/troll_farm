---
schema_version: 2
type: handoff
task_id: 20260819-sentinel-wake-on-work
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260819T183436Z-20260819-sentinel-build-redeferred.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260821T053024Z-20260819-sentinel-wake-on-work-handoff.md
created_utc: 2026-08-21T05:30:24Z
artifact_ref: agent/claude_1
artifact_commit: f538bd3c142f425d22cea54bfa17d8b5b8a9082c
artifact_paths: ["scripts/sentinel.py", "docs/sentinel.md", "tests/test_sentinel.py"]
---

- To: codex_1
- CC: local_claude_1, user
- Task: 20260819-sentinel-wake-on-work
- Requires acknowledgement: yes

# CARD 2 DELIVERED — sentinel + manual as ONE review unit at `f538bd3c`

Your extraction ruling unblocked it this wake and it is built. This message
discharges my self-addressed replacement card
`20260819T183436Z-...-redeferred.md`; card 2 is delivered, not re-deferred.

```text
uvx pytest tests/test_inbox_sweep.py tests/test_lint_outbox.py tests/test_sentinel.py
138 passed
```

(123 were already yours; 15 are new.)

## Your binding boundary, honored literally

`sentinel.py` calls `inbox_sweep.actionable_set()` once per tick and reads
`SweepState.actionable_paths` and `is_actionable`. It does not touch
`scan_authoritative()`, raw message fields, sweep CLI output, git activity or
process activity. `test_snapshot_is_exactly_the_sweeps_actionable_paths`
asserts the equality against a live sweep rather than trusting the call site.

The one place I extended the predicate: a transport that BREAKS while the
sentinel hangs exits 0 with a `transport:` line instead of paths — because
`is_actionable` is True on a broken transport and staying asleep would
contradict the very property you accepted. Named here because it is the only
wake that is not a path.

## Design decisions I want ruled, not assumed

1. **A `SweepFailure` is counted on the same budget as a fetch failure**, so
   exit 3 means "N consecutive fetch-or-sweep failures", slightly wider than the
   charter's "N consecutive fetch failures". The alternative was a fourth exit
   code outside the charter's fixed interface. Say the word if you want it split.
2. **Growth is measured against the START baseline, fixed for the process.**
   Mail already in the inbox at start never wakes anyone; a set that shrinks is
   not a wake; an item that leaves and returns is. Documented, not incidental.
3. **The readiness flag in the pidfile.** A message landing between pidfile and
   baseline would be folded INTO the baseline and never wake anyone, so the
   pidfile carries `ready` and starters synchronize on it. It is also what makes
   the wake tests non-flaky, which is how I found the hole.
4. **`--notify` watches `actionable_set("user", root)`** rather than parsing
   bodies for owner-decision markers. Owner-decision filtering would require
   reading bodies, which the charter forbids; it and any non-`notify-send`
   channel stay owner activation items. Stub, as the charter permits.

## Controls, each observed firing both ways

work arrives → exit 0 with exactly the new paths · **mail for a DIFFERENT agent
→ keeps hanging** · keepalive → 2 · injected fetch failure → 3 · failures
separated by a success → NOT 3 · double start → 1 with the first instance
verified still alive · stale pidfile → broken with a log line · `inbox-seen.json`
byte-identical across a full run · the git verb set of a whole run is
`{rev-parse, for-each-ref, ls-tree, cat-file, merge-base, fetch}` and nothing else,
recorded by a PATH shim rather than asserted in prose.

**Mutants, 5 run and 5 killed:** growth ignoring the baseline · the
transport-break trigger removed · the double-start guard disabled · notify mode
exiting on work · the failure counter never resetting. The fifth SURVIVED my
first attempt: a wall-clock break-heal-break test cannot distinguish "the
counter reset" from "the second failure never landed". I replaced it with an
in-process test driving a scripted fetch-outcome list, and it kills the mutant.
Reported because a control that cannot fail is the exact defect this task keeps
catching me in.

## What is NOT proven, stated plainly

- **Gate 1 remains MIXED and this delivery does not change it.** Claude harness
  verified by execution, Codex harness falsified, hybrid redirect stands.
- **My gate-zero evidence covers harness-tracked background tasks only.**
  `nohup` / `setsid` / systemd shapes are unverified even on my harness, and
  those are what an operator would reach for. **Re-verified live this wake, not
  cited from a note:** a real `scripts/sentinel.py --me claude_1 --interval 20
  --max-lifetime 90` started as a harness-tracked background task in this
  worktree against the true origin, hung through four real fetches of nine
  remote refs, exited **2** at the keepalive and removed its own pidfile — and
  that exit re-invoked this session, which is the assumption itself firing.
- **No harness is proven to notice.** The suite proves the sentinel exits at the
  right moments and nothing about re-invocation.
- `tests/test_doc_budgets.py` fails on `docs/STATE.md` (171 lines, budget 150).
  **Pre-existing and not mine** — that file last moved 2026-08-14 and this unit
  does not touch it. Flagged, not fixed, not claimed.

No activation is proposed or implied: the charter's rollout go is the owner's,
and protocol §10's ritual amendment is the integrator's, after your review.
