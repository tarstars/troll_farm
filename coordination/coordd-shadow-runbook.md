# coordd shadow mode — runbook (P1)

While in shadow: **git is authoritative; coordd is being compared against it.**
Nothing about the existing protocol changes yet.

1. Deploy per `deploy/README.md`; verify `/health` from both machines.
2. Register the roster (from any machine):
   `coordctl register --agent local_claude_1 --role coordinator`
   `coordctl register --agent claude_1` · `coordctl register --agent codex_1`
3. Create coordd tasks for every currently-open task record you touch (id = the
   `coordination/tasks/` filename stem), and claim/release in coordd alongside the
   normal git flow.
4. Mirror messages after each fetch:
   `python3 scripts/coordd_mirror.py --root coordination/messages`
5. Weekly comparison, recorded in the task record for the migration:
   - `coordctl tasks --state claimed` vs actually-active work;
   - `coordctl events --since 0 | wc -l` vs new message count in git;
   - any disagreement is a bug in shadow wiring — fix before proposing P2.
6. Exit criteria to propose the P2 plan: two weeks (or three working sessions,
   whichever first) with zero unexplained disagreements, all Task 7–16 tests
   green, and the owner's go-ahead.
7. During shadow, deliberately trigger one duplicate task-create and one claim
   conflict and confirm the client sees a proper 4xx JSON error, not a dropped
   connection (regression check for the 2026-08-10 fix wave).

## Known items the P2 plan must own (from the 2026-08-10 final review + fix wave)

Two Important, reviewer-endorsed as named P2 tasks with tests — do not let P2
inherit them silently:

- **Write-set prefix normalization/validation** (`scripts/coordd.py` claim path):
  reject absolute paths and `..`, normalize `./`//`//`, require a non-empty list of
  strings (a bare string currently shreds into per-character prefixes), and match on
  path-component boundaries (`docs` currently blocks `docs2/`). P2's "overlapping
  prefixes cannot both be active" acceptance test exercises exactly this.
- **Monotonic per-task generation counter + idempotent claim retries**: generations
  restart at 1 after release (recur across tenures), and a same-idempotency-key claim
  retry bumps the lease while the deduplicated event records the old generation — so
  the audit export cannot faithfully reconstruct lease state. P2's "audit export
  reconciles against database state" acceptance test fails on these semantics.

Smaller carries: guard edge crashes (check_clock on a zero-commit repo; doctor
outside a repo root); export_audit partial-write duplicates (dedupe on seq or
temp-and-rename); mirror nits (glob is one level deep; CLI posts `--task ""` instead
of null); doctor additions — repo-freshness (behind-origin) check per spec §5,
host-awareness so the VM's structurally-red cron check doesn't train agents to
ignore red, and a bulk-storage-attached check (`cgauto/check_external_storage.py`)
after the 2026-08-10 post-reboot incident where an unplugged USB masqueraded as 20
test failures; auth polish (non-ASCII Authorization header returns 500 rather than
401 — contained, cosmetic; don't echo raw exception text in 500 bodies); HTTP-level
tests for the 403/422 paths; deploy README notes that remote `sudo cat` token
distribution assumes NOPASSWD sudo.

### From claude_1's adversarial self-review, 2026-08-11 (8 findings; F1 and F5 re-verified by the coordinator's own repros)

Important — named P2 tasks:
- **F1** `register_handoff`'s local-ref fallback verifies commits reachable from NO
  origin ref (unpushed work passes). Nuance for the fix: the VM's bare-mirror deploy
  NEEDS a non-`refs/remotes` lookup (`refs/heads/*` in a mirror) — distinguish mirror
  vs worktree clones instead of deleting the fallback; the committed
  `test_valid_handoff_verifies` fixture itself relies on the hole and must change.
- **F2** `set_state` is unfenced and ignores `leases`: a non-owner can drive any task's
  state, and a lease survives `done`, blocking overlapping write-sets indefinitely.
- **F3** `claim` has no terminal-state guard: `done`/`dropped` tasks silently reopen.
- **F5** `check_ref_census` only scans `refs/heads` — an unpushed commit on a detached
  HEAD (exactly what worktree/VM flows produce) reports clean.

Minor: **F4** negative Content-Length hangs a handler thread; **F6** cron guard
accepts future-dated markers; **F7** nothing owns fabricated frontmatter/filename
dates (check_clock covers only git dates — the 2026-08-09 incident surface); **F8**
mirror cursor write is non-atomic (truncated cursor bricks later runs).

Deployment deviations worth folding into deploy/README: root/coordd users need
GitHub known_hosts+keys or clones route through the authed user; `coordctl doctor`
against a root-owned repo dies on git's dubious-ownership guard (exit 1, not 2) —
add `safe.directory` handling or document running doctor against the agent's own
checkout. Attacks that HELD, for the record: multi-process HTTP claim race, fencing
after expiry takeover, auth on all 14 routes, git-verification injection, kill -9
durability + idempotency.
