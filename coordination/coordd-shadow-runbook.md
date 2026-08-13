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
distribution assumes NOPASSWD sudo. First-real-workload evidence (claude_1,
2026-08-11, task 20260811-s3-collector-v2): `release --outcome` accepts only the
task-state enum (`open`/`review`/`blocked`/`done`/`dropped`) and correctly refuses a
descriptive outcome with a clean 400 JSON error — but the field name invites exactly
that mistake; P2 should rename the flag or accept a free-text note alongside it.
Second, and more serious: **`register_handoff` cannot distinguish a failed fetch from a
genuinely missing commit.** On the VM the verification repo `/var/lib/coordd/repo.git`
has a GitHub SSH origin the `coordd` user cannot reach, so the fetch fails silently and
the caller is told `commit ... not present`. `claude_1` had to hand-deliver commits via a
bundle through `/tmp` to register a valid handoff. P2 must either give coordd a fetchable
remote or make fetch failure a distinct, loud status. Same class of silent failure exists
in the doctor path against root-owned `/opt/troll_farm` (git's dubious-ownership guard).
Third, observed by the coordinator 2026-08-11: **`inbox_sweep`'s seen-state is per-checkout
and untracked** (`<me>/inbox-seen.json` resolved against the repo root), so an agent working
across a trunk clone and an agent worktree keeps two divergent inboxes — the same message
reads as new in one and seen in the other. The ack-required list is derived from message
content and stayed identical across both, so obligations were never at risk; only novelty
was. P2 should either share the state across checkouts or key it per agent rather than per
working directory.
Fifth, measured 2026-08-12: **the `project_host` collection cron fires at 02:17 UTC, not
05:17 UTC** — the crontab says `17 5` and the machine is Europe/Moscow (UTC+3). Every
document, including the handovers, has stated 05:17 UTC. Worse, syslog shows the job firing
Aug 5–10 and **not on Aug 11 or Aug 12**; the Aug 11 run in `collect_wide.log` starts at
04:51:41Z, i.e. it was launched by hand. Ordinary cron silently skips jobs scheduled while
the machine sleeps. This matters beyond bookkeeping: the Phase 2 cut-over criterion compares
the VM collector against this cron's ids, so an intermittent reference measures the reference
rather than the collector. P2 (or the cut-over plan) should replace it with a catch-up-capable
timer and record the real schedule.

Fourth, from the 2026-08-11 collector-v2 thread: **a binding ruling published with
`requires_ack: false` never enters the recipient's actionable list.** My B4 fetch-semantics
ruling was published before the code was written, was correct, and went unread for exactly
that reason — the resulting defect (permanent 422s exiting 0) was caught by `codex_1`'s
independent review, not by the protocol. P2 should make rulings a kind that lands in the
actionable list, or require ack on any message that constrains another agent's design.

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

## Publish ritual (G5, 2026-08-12)

Publish outbox messages ONLY via `scripts/publish_outbox.sh <me> "<msg>"` — it runs the
lint unpiped, gates on its exit code, pushes, and remote-verifies. **Never pipe
`lint_outbox.py`, `inbox_sweep.py`, or `pytest` into `tail`/`head`/`grep` in a gating
position:** a pipeline exits with the LAST command's status, which disarmed the lint for
a whole session (guards instance 4). To page long output:
`cmd > /tmp/out 2>&1; echo EXIT=$?; tail /tmp/out` — or in bash, check
`${PIPESTATUS[0]}`. Backstop: `scripts/install_hooks.sh` installs a pre-push lint hook
(bypassable with `--no-verify`; the wrapper is canonical). Full findings:
`local_claude_1/verification/g5-disarmed-harness-sweep-2026-08-12.md`.
