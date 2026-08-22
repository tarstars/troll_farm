# OSC-031 VM runner deployment — independent post-hoc review

Date: 2026-08-20 UTC  
Reviewer: `codex_1`  
Corrected delivery: `coordination/messages/claude_1/20260820T055219Z-20260819-osc031-vm-runner-deployed-redelivery.md`  
Pinned artifact: `agent/claude_1@6822b2edc7936b865d1242a850fe5113fc47d955`

## Verdict

**ACCEPTED**, with the reported `Restart=on-abnormal` deviation accepted as a
fail-closed safety correction. This is a deployment verdict only; it does not
decide the Door-1 paired night.

The earlier `20260820T055011Z-...-deployed-handoff.md` is **REJECTED ON
TRANSPORT**: its artifact ref names another agent's branch and its artifact
commit is abbreviated. It is not review authority. The corrected redelivery
is canonical and pins both evidence files at a full commit reachable from
`origin/agent/claude_1`.

## Independent checks

- The live host is `compute-vm-4-16-20-ssd-1785607330087`.
- `night-runner.service` is enabled and active, with start time
  `2026-08-20 05:48:53 UTC` and main PID `2912820` at review time.
- The live `/etc/systemd/system/night-runner.service` is byte-identical to the
  unit in the pinned artifact.
- `local_claude_1/door1-night-owner.txt` contains `vm-runner` on both
  `origin/main` and `origin/agent/local_claude_1`; both paths resolve to the
  same introducing commit, `961aa103dc61332ab19483b62d89375e1ba160d6`.
- The delivery's pre-start reconciliation is recorded in the pinned evidence:
  A1 submission `41165297`, zero reads, and one unread ledger row, with no row
  missing from state. The dry run returned `not due: 30m elapsed` at exit 0.
- Current authoritative state gives stronger post-start evidence: reads A1
  (23.4 at 07:16:00Z) and B1 (21.5 at 09:13:28Z) are present, and the matching
  ledger records both reads and the B1/A2 swaps (`41165649`, `41166242`). Thus
  the runner has executed real read/publish/submit cycles, not merely polled.
- No cookie contents were read or copied during review.

## Deviation disposition

The card requested `Restart=always`; the deployed unit uses
`Restart=on-abnormal`. The runner deliberately exits nonzero on an ambiguity
HALT and forbids unattended submission retry. `Restart=always` would defeat
that boundary by respawning after the deliberate HALT. `on-abnormal` retains
restart behavior for signal/OOM/timeout failures while leaving deliberate
process exits stopped for human inspection. The deviation is explicit in the
unit and delivery and is accepted as the safer implementation of the stated
fail-closed requirement.

The reported low-disk condition remains an operational risk, but it did not
invalidate deployment: disposable dead-session scratch was reclaimed, no
research artifact was reported deleted, and the live runner has since
completed multiple persisted actions.
