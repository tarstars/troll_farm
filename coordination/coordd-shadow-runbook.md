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
