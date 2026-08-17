---
schema_version: 2
type: policy
task_id: 20260816-h-starve-1-standing-troll-audit
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T074259Z-20260817-transport-gates-wip-evidence.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-17T07:42:59Z
---

- To: claude_1, codex_1
- CC: user
- Tasks: all (transport-level policy; filed under the audit task as the primary consumer)
- Requires acknowledgement: yes (both)

# policy: two transport gates are now MACHINE-ENFORCED (owner decision 2026-08-17) + coordd decision date set

Pool items 9–11 are implemented and live at trunk. What changes for you, concretely:

## 1. WIP limit — the lint now rejects a stacked handoff

One in-flight ack-requiring handoff per agent per task. `scripts/lint_outbox.py`
(which `publish_outbox.sh` already runs, armed) now REJECTS a NEW handoff while your
previous ack-requiring handoff for the same task has no published ack and no published
supersede. Corrections remain always publishable (their own kind, exempt). Applies to
NEW messages only — nothing published is flagged retroactively. Protocol §10 carries
the rule text. This mechanizes what yesterday cost us three crossed-message correction
rounds.

## 2. Evidence gate — cause labels travel only with their review

A handoff whose body asserts a chartered cause label (`GENERATOR_GAP`,
`NO_WORK_ON_MAP`, `UNIT_CANNOT_REACH_WORK`, `STUCK_COMMITMENT`,
`ALL_WAIT_CAUSE_UNDETERMINED` — the registered set is `CAUSE_LABEL_TOKENS` in the
lint) must carry a `review_ref:` front-matter field naming the review that ACCEPTED
the producing instrument, and that file must exist on an authoritative remote ref.
Raw-data and instrument handoffs need nothing. **claude_1:** your pool-#3 cause-table
handoff will need `review_ref:` pointing at codex_1's pool-#2 acceptance review — which
is exactly the order the pool already prescribes. **codex_1:** when a task charters new
cause vocabulary, extending `CAUSE_LABEL_TOKENS` is part of accepting its instrument.

Both gates: 31/31 transport lint tests green, each gate observed FIRING on a violating
fixture and RELEASING on a compliant one (standing rule honoured).

## 3. Pool status is computed, not maintained

`python3 scripts/pool_status.py` prints `Pool: N/M done`, the open items, and the
latest log line, straight from `coordination/ITERATION.md`. Use it instead of asking.

## 4. coordd: promote-or-park by 2026-08-31

The shadow's decision date is now in the runbook: by 2026-08-31 (or pool close if
later), coordd is proposed for P2 on its existing exit criteria or PARKED and torn
down. No standing dual coordination plane. Until then nothing changes: git is the only
authoritative transport.

## For the owner, in plain words

The two working-habit rules you approved are now enforced by the machinery itself, not
by anyone's discipline: an agent physically cannot publish a second unanswered piece of
work on the same task, and cannot publish a cause claim without attaching the review
that validated the measuring tool. Both rules were tested by deliberately breaking them
and watching the gate catch it. The pool now also reports its own progress with one
command, and the experimental coordination service has a firm use-it-or-lose-it date.

## Boundaries

No resident mutation, no Arena action. Pool unchanged except owner-added items 9–11,
now done.
