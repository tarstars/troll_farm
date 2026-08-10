# Handover — control-plane plan execution moves to the Yandex Cloud VM

**Written 2026-08-10** on `project_host`, immediately before the owner powers it off.
Author: `local_claude_1` (coordinator/integrator). Verified before writing: every local
branch has zero commits unreachable from `origin`; trunk = `main` = `session-2026-07-01`
= both origin refs at `464b5f08`; the agent worktree is clean and synced.

## What this thread is

The owner redirected the project to rebuild its coordination system. The approved design
is `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md` (control
plane `coordd` on the Yandex Cloud VM + git as evidence; no CI this iteration). The
implementation plan is `docs/superpowers/plans/2026-08-10-coordination-control-plane.md`
— 17 tasks, P0 cleanup + P1 build. Execution started on `project_host` under
subagent-driven development and now continues on the VM.

## Progress state (the SDD ledger, persisted)

- **Task 1: complete** (commits `404d5a92..464b5f08`, review clean). STATE.md dieted
  360 → 149 lines, budget enforced by `tests/test_doc_budgets.py`; pre-diet text
  archived byte-identical (blob-hash-verified) at
  `docs/archive/STATE-2026-08-10-pre-diet.md`.
- Task 1 deferred minors for the final whole-branch review (both artifacts of the
  plan's own literal text, no content loss):
  1. `docs/STATE.md` §3 — the noise-band replacement bullets sit at top level, so the
     following "Unchanged:" bullet nests under the σ bullet instead of the standing
     arena-authorization umbrella bullet.
  2. `docs/archive/INDEX.md` — the new pointer is a plain bullet appended after a
     pipe-table.
- **Resume at Task 2 of 17.** No other task started. No fix rounds pending.

## How to resume on the VM

1. Clone and set up (GitHub auth already works on the VM — `claude_1`/`codex_1` push
   from there):
   ```bash
   git clone git@github.com:tarstars/troll_farm.git && cd troll_farm
   git checkout session-2026-07-01
   python3 -m venv .venv && .venv/bin/pip install pytest
   ```
2. **Establish the VM test baseline before Task 2** and record it in the ledger:
   `.venv/bin/python3 -m pytest tests/ -q -p no:randomly 2>&1 | tail -3`. On
   `project_host` the only failures are the three pre-existing B7 tests; on the VM,
   tests needing `rust/target/release/libtroll_farm.so` (Python ctypes) or local-only
   data will also fail — that is environmental, not regression. Task 17's full-suite
   gate must be judged against the VM baseline recorded here, or run
   `cargo build --release` in `rust/` first to shrink the gap.
3. Start a Claude Code session in the clone and say: *"Resume executing
   docs/superpowers/plans/2026-08-10-coordination-control-plane.md per
   coordination/HANDOVER-2026-08-10-control-plane-execution-to-vm.md — Task 1 is
   complete, start at Task 2."* If the superpowers plugin is available, use
   subagent-driven-development (recreate the workspace with its `sdd-workspace` script
   and seed a fresh ledger whose first line names the plan file, then copy the
   Progress state above into it). Without the plugin: execute each task's steps
   exactly as written, in order, TDD included, with a review pass after each.
4. Identity: continue as **`local_claude_1`** — the roster
   (`coordination/roster.json` on `origin/main`) is unchanged and the id is not tied
   to a host. Task 6 publishes from the canonical branch; create the worktree first:
   `git worktree add ../troll_farm-local_claude_1 agent/local_claude_1` and follow the
   task's steps from there.
5. The plan's Global Constraints hold verbatim on the VM (venv pytest invocation,
   exact-path staging, commit trailer, push-and-sync `main` after every task).

## What does NOT move to the VM

- **The 05:17 collector cron and `data/raw/` store stay on `project_host`.** With the
  machine off, collection simply pauses — no data loss, a coverage gap. On the VM,
  `data/raw/collect_wide.log` is absent, so Task 4's `check_cron_health` will exit 2
  with "does not exist": that is the guard being honest, not a bug. Note it in the
  Task 4 report and move on.
- **Arena control.** The CodinGame session cookie (`cgauto/cg_session.txt`, untracked)
  stays on `project_host`. No Arena mutation of any kind from the VM. Nothing in this
  plan needs one.
- **Bulk storage.** `artifacts/`, `outputs/`, `data/external`, `data/generated` are
  symlinks to a local USB volume and will dangle on the VM. Per `AGENTS.md`: never
  replace them with real directories. Nothing in this plan writes to them.
- The local `.superpowers/sdd/` workspace (gitignored scratch) and this machine's
  Claude memory. This handover is the complete carrier of both.

## Convenience

`coordd` deploys to this same VM later (Task 17 writes `deploy/`), so once the plan
reaches Task 17 the service host is the machine you are already on — the SSH-tunnel
unit applies only when `project_host` returns.

## Hazards carried forward

- Verify dates against `git log`, never filenames (the repo contains a fabricated-clock
  session named "2026-08-12" committed 2026-08-09). `check_clock` lands in Task 3.
- Never pipe a guard's output (`lint | tail` disarmed a guard for a whole session);
  run guards as their own command and check `$?`.
- Stage exact paths; no `git add -A`; no formatters over `rust/src/bin/` or `cgauto/`;
  byte-sacred `rust/src/bin/yamo_orchard_live.rs` (SHA-256 prefix `fff6669b`).
