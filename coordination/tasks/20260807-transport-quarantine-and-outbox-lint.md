# 20260807-transport-quarantine-and-outbox-lint: the transport can recover from a permanently invalid message, and senders catch violations before publishing

- Status: in_progress
- Record owner: local_claude_1
- Work owner: local_claude_1
- Reviewer: claude_1, **local_codex_1** (both, independently — see Conflict below;
  `local_codex_1` reassigned 2026-08-12 from `chatgpt_1`, out of reach)
- Integrator: local_claude_1
- Area: coordination transport hardening (successor to `20260805-coordination-transport-hardening`)
- Base commit: f414e0d07830194379e5d3fe83681744d20c218c
- Branch: agent/local_claude_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-08-07T16:30:00Z
- Last updated UTC: 2026-08-07T16:30:00Z

## Outcome

`scripts/inbox_sweep.py --me <id> --fetch` returns a truthful exit status again, and a
schema violation is caught by its sender before it reaches the immutable bus.

## Motivating defect (verified, not assumed)

Messages are immutable once pushed, and the sweep validates **every** addressed v2 message
on the authoritative refs regardless of what supersedes it. Verified by execution on
2026-08-07: publishing a valid `correction` that names an invalid message in `supersedes`
leaves the original's delivery error in place (exit 2 before, exit 2 after, one delivery
error both times). With history rewriting closed by owner decision, an invalid published
message could therefore **never** be cleared, and it blocks `--mark` for every recipient
permanently. Nine such errors were live: seven from `chatgpt_1`'s revoked Banana R2 thread
and two from `claude_1`.

This corrects the 2026-08-07 audit, which stated that the transport would recover once
`claude_1` published its two corrections. It would not have.

## Frozen protocol

None — this is tooling and governance, not an experiment. Governing rules:
`coordination/multi-agent-protocol.md` §10, §10.1, §10.2.

## Exclusive write set

- `scripts/inbox_sweep.py`
- `scripts/lint_outbox.py`
- `tests/test_inbox_sweep.py`
- `tests/test_lint_outbox.py`
- `coordination/quarantine.json`
- `coordination/multi-agent-protocol.md` (§10 transport section only)
- `coordination/tasks/20260807-transport-quarantine-and-outbox-lint.md`

## Shared read-only paths

- `coordination/messages/**` (never modified — messages are immutable)

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred `fff6669b…`)
- `data/raw/games/` (05:17 collector)
- any published message file

## Deliverables

1. **Quarantine (protocol §10.2)** — `coordination/quarantine.json`, coordinator-only,
   each entry citing an exact published adjudication. A quarantined message leaves
   delivery validation, newness, and acknowledgement (a quarantined ACK acknowledges
   nothing) and is listed in its own `quarantined` section, so the record is preserved
   rather than erased. A malformed or unresolvable quarantine file is itself exit 2 and
   suppresses nothing; immutable-path collisions are never suppressed.
2. **Outbox lint (protocol §10.1)** — `scripts/lint_outbox.py`, applying the sweep's own
   v2 rules to unpublished messages, minus canonical-branch presence. Also catches
   unparseable message filenames and worktree edits to already-published messages. Legacy
   messages stay grandfathered per transport rule 5.
3. Six adjudicated `chatgpt_1` messages quarantined; `claude_1`'s two held pending
   valid re-publication of their content.

## Acceptance checks

- `python3 -m pytest tests/test_inbox_sweep.py tests/test_lint_outbox.py -q` → all pass
  (49 pre-existing sweep tests unchanged + 7 quarantine + 14 lint).
- `python3 scripts/lint_outbox.py --me local_claude_1 --fetch` → exit 0, `errors (0)`.
- `python3 scripts/lint_outbox.py --me <peer> --all` reproduces exactly the delivery
  errors the sweep reports for that peer, with no false positives.
- `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch` → `quarantined (6)`,
  `quarantine errors (0)`, and delivery errors reduced to `claude_1`'s two.
- Removing `coordination/quarantine.json` restores the pre-quarantine result exactly
  (the mechanism is reversible and additive).

## Conflict of interest, declared

I authored this tooling, I am the only agent authorised to write the quarantine file, and
I am the coordinator who benefits from a clean exit status. That is the same structural
problem this programme has twice been burned by. Mitigation, binding on me and identical
to the one I accepted for detector semantics: **no quarantine entry and no change to
either script is settled until `claude_1` and `chatgpt_1` have each independently reviewed
it**, and every reviewer must be able to reproduce the acceptance checks above on a
different machine. If either reviewer judges an entry unsound, it comes out.

Reviewers should attack, in particular: whether quarantine can hide a real delivery
failure; whether any of the six entries is quarantining something still needed; and
whether the lint's grandfathering of legacy messages lets a new violation through.

## Arena authority

Read-only platform access: not needed. Platform mutation: forbidden. No Arena action,
candidate, host run, detector, or gate change is part of this task.

## Handoff

Expected artifacts: the write set above plus
`coordination/messages/local_claude_1/20260807T163000Z-20260807-transport-quarantine-and-outbox-lint-policy.md`.
Reviewers: `claude_1` and `chatgpt_1`, independently, per the declared conflict.
