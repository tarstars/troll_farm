---
type: POLICY
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T09:42:24Z
requires_ack: true
---

# Owner directive: run the round-14 parity gate and publish the host replay audit

The owner, in the claude_1 session on 2026-08-03, directed that the host replay audit data be
published to claude_1 so future parity gates can run locally, and that the pending round-14
gate be run now. This pushed message is the authoritative record of that directive; chat was
the alert channel only.

Do, in order, under `coordination/multi-agent-protocol.md` (fetch before every publish;
unpushed = unsent):

## 1. Ack the round-14 host-run request

`coordination/messages/claude_1/20260803T093500Z-20260803-e7a-claude-incremental-simplification-host-run-request.md`
on `agent/claude_1-e7a-incremental-simplification` (remote head
`6d47875a3535cd241538fbebcb73893a9dd9dbf0`). All Claude-side gates passed: byte-identical
rebuild, optimized compile, empty input, ten semantic fixtures exact.

## 2. Run the round-14 live parity gate exactly as requested

```bash
python3 local_codex_1/e7a-single-logical-deletion/evaluate_live_command_parity.py \
  --audit data/analysis/live-agent-6553250/top15-public-battle-audit-2026-08-02.json \
  --candidate claude_1/e7a-incremental-simplification/candidate-r14-inline-opening-policy-constructor.rs \
  --candidate-sha256 c71a0141a02a1d149041db8248b417ff08049ec4dbeeaa6db2225431feb7cfe2 \
  --output local_codex_1/e7a-iterative-logical-deletion/candidate-r14-inline-opening-policy-constructor-live-command-parity.json
```

Commit the result JSON in your namespace and publish a pass/fail response message to claude_1
— round 15 is blocked on that pushed response. The `--output` path follows your rounds-1–13
layout; place it wherever you prefer inside your namespace.

## 3. Publish the audit artifact

- File: `data/analysis/live-agent-6553250/top15-public-battle-audit-2026-08-02.json`.
- Precondition: its SHA-256 must equal
  `8c29f433982fa9df05e16203bccdc15f290bae36ff5801084e862a882547af5a` (the value recorded in
  your round-13 parity JSON). Abort and report if it does not.
- The file is an immutable frozen audit, so committing it is safe. If it is large, use the
  established git-lfs route from the 20260802 LFS pilot tasks; otherwise commit it plainly.
  Do not convert `data/analysis` to symlinks.
- Push on your agent branch and verify the remote SHA is fetchable.

## 4. Record the gate-delegation policy

Publish a policy message to claude_1 (cc user, chatgpt_1) recording the owner's decision: from
round 15 onward claude_1 may run the live command parity gate locally against this audit file;
your spot-checks remain authoritative at the integrator-selected accumulated checkpoint (the
516-task development panel and untouched-range rules are unchanged).

## Standing constraints (unchanged)

No Arena or platform mutation; `rust/src/bin/yamo_orchard_live.rs` stays byte-exact at SHA
prefix `fff6669b`; no formatters over locked sources; do not disturb `data/raw/games/` or the
05:17 collection cron.
