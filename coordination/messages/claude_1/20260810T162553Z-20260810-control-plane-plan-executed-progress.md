---
schema_version: 2
type: progress
task_id: 20260810-control-plane-plan-executed
from: claude_1
to: ["user"]
cc: []
message_id: coordination/messages/claude_1/20260810T162553Z-20260810-control-plane-plan-executed-progress.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-10T16:25:53Z
---

- To: user
- CC: none
- Task: 20260810-control-plane-plan-executed
- Requires acknowledgement: no

# Control-plane plan executed: Tasks 2-17 complete on the VM

Executed by claude_1 under the owner delegation recorded in
`coordination/HANDOVER-2026-08-10-control-plane-execution-to-vm.md` item 4
(owner grant: direct commits to `session-2026-07-01`, `main` kept equal and
pushed after every task; no coordinator role, no Arena authority exercised).
Kind note: sent as `progress`, not v2 `handoff`, because the deliverables are
already on trunk under the owner grant and the transport correctly requires a
v2 handoff to pin the sender's canonical branch — nothing awaits integration.

## Commits (one per task; session-2026-07-01 = main = 21bf33c1)

9fa42c7e T2 authority docs · d2449111 T3 check_clock · 449a2d95 T4 cron
watchdog · 8b900382 T5 ref census · 6ad8d0fa T7 Store · 7451e83a T8 register ·
73fb3065 T9 atomic claim · ba341d7b T10 leases/fencing · 82789735 T11 events/
acks · 64e3a85d T12 git-verified handoffs · b934cfa0 T13 HTTP/auth · 0d56d648
T14 dashboard/audit/restart · cd546179 T15 coordctl/doctor · 7150f80a T16
shadow mirror · 21bf33c1 T17 deploy+runbook. Deliverable paths at 21bf33c1:
scripts/{coordd,coordctl,coordd_mirror,check_clock,check_cron_health,
check_ref_census}.py, matching tests/, deploy/, and
coordination/coordd-shadow-runbook.md (all 18 verified present via cat-file).
Task 6 published separately on `agent/claude_1`: f7eb61d5 (ack amnesty
policy, adapted to my namespace per the delegation). Task 1 was complete
before delegation (464b5f08).

## Test results

Every task's TDD cycle ran red then green; 32 new tests, all passing. Task 17
gate judged against the VM baseline recorded before Task 2 (handover §2):
baseline 25 failed / 1010 passed / 4 skipped / 219 collection errors ->
final 25 failed / 1042 passed / 4 skipped / 219 errors; failed and error
name-sets byte-identical (diff empty). Baseline failures are the B7 trio plus
VM-environmental missing-data/missing-.so items; rust
`target/release/libtroll_farm.so` was built (toolchain at ~/.cargo/bin) and
did not change the counts - the binding constraint is absent local data.
20-thread claim race: exactly 1 winner / 19 conflicts, stable across 5 reruns.
Sacred source verified fff6669b before and throughout.

## Deviations (full detail in commit bodies)

1. venv via `uv sync` (python3-venv/ensurepip broken on this VM); the plan's
   `.venv/bin/python3 -m pytest` invocation works unchanged.
2. Task 5 plan defect, minimally fixed: verbatim test asserts lowercase
   'unpushed' while verbatim impl printed only 'UNPUSHED:'; kept the test as
   contract, reworded one advisory line in the script. OWNER REVIEW REQUESTED.
3. Task 6 executed from a new durable worktree of the plan clone
   (`/home/tarstars/prj/troll_farm-plan-agent`) because `agent/claude_1` was
   checked out only in a dead session's /tmp scratch dir; tooling refreshed
   from origin/main and left uncommitted, message linted clean (errors 0,
   exit 0), delivery state of claude_1/codex_1 unchanged (both sweeps exit 1
   legacy-backlog, delivery errors 0, quarantine errors 0).
4. Task 4/15 honest VM results: `data/raw/collect_wide.log` absent -> cron
   guard and doctor exit 2 by design (collector stays on project_host).
5. Commit identity: repo-local `tarstars <142857@mai.ru>` (matches all VM
   repos); trailer exactly as the plan specifies.
6. First handoff-kind attempt correctly rejected by the lint (artifact_ref
   must be the sender's canonical branch); republished as this progress
   message - transport working as designed, nothing was pushed in between.

## Next steps (owner)

- Review deviation 2 (one-line wording choice in check_ref_census.py).
- Deploy shadow mode per `deploy/README.md` on this VM when ready; runbook at
  `coordination/coordd-shadow-runbook.md`. No Arena, storage, or CI actions
  were taken; none are pending.
