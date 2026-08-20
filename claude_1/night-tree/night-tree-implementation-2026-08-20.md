# Post-B5 night tree — implementation and verification (claude_1, 2026-08-20)

Card: `coordination/messages/local_claude_1/20260820T144705Z-20260819-osc031-night-tree-card.md`
(urgent-by-clock: deployed before ~01:00Z, ahead of the ~01:20Z B5 read).
Owner ruling implemented: *"approve the tree"*, 2026-08-20 ~15:00Z.

## What was built

One patch to `cgauto/night_runner.py` (no supervisor, no second process, no new
service). The runner already owned the state machine; the tree is the answer to
the one question it did not previously ask — *what now?* — asked once, after the
B5 read, from the same arithmetic that produces the verdict.

    at the final read:
      1. verdict_block(state)                      unchanged, still written first
      2. mean = pair_stats(state)["mean"]           same arithmetic, now shared
      3. post_b5_branch(mean):
           |mean| in [1.0, 1.315)  -> "extension"
           otherwise               -> "session3"
      4. branch action (below)
      5. owner morning sheet, in EITHER branch
      6. ONE commit carrying every path the branch touched

**Branch 1 — extension.** `extend_plan` appends A6..B10 to the same plan with
the same two arms (n=10, bar 0.930), and the next arm is submitted immediately
so the loop has a submission to wait on. Nothing else changes: same state file,
same ledger, same arms.

**Branch 2 — session 3.** A fresh state
(`local_claude_1/door1-vs-old-2026-08-20-state.json`) and a fresh ledger
(`local_claude_1/door1-vs-old-2026-08-20.md`) are written with the
pre-registered arithmetic in the header, arm A is submitted at once, and the
running process **rebinds to the new files and keeps going**. The rebind is the
part with teeth: without it the loop re-tests `reads >= plan` on the finished
session-2 state, breaks, prints "block complete" and exits — and because the
unit is `Restart=on-abnormal`, a clean exit is not restarted. Session 3 would
sit submitted and never read. A test exists for exactly that (below).

**The morning sheet** is built in both branches and gated on `lint_outbox.py`'s
EXIT STATUS. If the lint rejects it, the sheet is **unstaged and moved out of
the message namespace** (`REJECTED-<name>` beside the ledger) and a ledger line
records why: a rejected message is never committed, and a lint failure never
costs the night.

## Requirements from the card, and where each is met

| requirement | where |
|---|---|
| fail-closed HALT semantics unchanged | `submit_next` re-uses the original submit/halt path; `halt()` untouched apart from `git_publish`'s signature |
| state and ledger pushed as now | `git_publish(paths, msg)` — same add/commit/push/retry/push-to-main chain, now taking N paths so one commit carries the whole branch |
| no mutation beyond the chartered submissions | only `SESSION3_ARMS` is ever submitted; both digests verified as committed blobs on `origin/main` AND `origin/agent/local_claude_1` |
| dry-run of the branch logic against a synthetic completed state | `claude_1/night-tree/test_post_b5_tree.py`, 23 tests |

## Verification

    $ python3 claude_1/night-tree/test_post_b5_tree.py
    Ran 26 tests ... OK

The suite drives the **real `main()` loop** against synthetic completed states
with the arena, the submitter, git and the lint stubbed — both branches end to
end, plus a mid-block regression case proving an ordinary read still behaves
exactly as it did before the patch (two paths published, no tree, no extension).
The owner morning sheet is validated by the **real transport validators**
(`inbox_sweep.validate_v2` plus lint_outbox's WIP, evidence, cross-task,
deferral and card-ack gates) in both branches — a sheet the runner cannot
publish is a sheet the owner never reads.

    $ timeout 600 uvx pytest tests/test_inbox_sweep.py tests/test_lint_outbox.py -q
    119 passed

### Controls — a check that cannot fail is not a check

    $ python3 claude_1/night-tree/mutation_control.py
    == part 1: pre-patch control ==
      pre-patch runner: exit 0, stdout 'block complete'; ledger has BLOCK
      COMPLETE and NO extension, NO session 3, no further submission
    == part 2: mutants (each must turn the suite red) ==
      KILLED  band is closed at the bar                    (1 test red)
      KILLED  the bar ignores the block size                (3 tests red)
      KILLED  extension appends three pairs, not five      (3 tests red)
      KILLED  the session-3 switch is never applied        (1 test red)
      KILLED  a lint-rejected morning sheet is committed anyway (1 test red)
      KILLED  the extension forgets to submit the next arm (2 tests red)
      restored runner: suite green
    all controls held

Part 1 is the honest statement of the gap: `origin/main`'s runner, driven to the
same completed block, records the verdict and stops. Part 2 mutates five
decisions the tree makes and confirms each one is actually guarded — including
the boundary, which is the whole ruling: **1.315 is NOT in the band** (`< bar`,
not `<= bar`), and 1.0 IS (`floor <=`).

## Limits, stated

- **Found and fixed while building this, not shipped as a caveat:** the bar is
  a function of the block size, and the extension changes the block size. The
  pre-registration says bar 1.315 at n=5 and 0.930 at n=10; the runner had
  1.315 as a constant. An extended block would have been graded against the
  5-pair bar and a true +1.0 result reported to the owner as "between the floor
  and the bar" when at n=10 it is a **winner**. `bar_for(n)` now carries both
  pre-registered literals (and the same arithmetic for any other n), and the
  verdict block prints the n it used. A mutant that restores the constant is
  killed by three tests.
- A consequence worth stating plainly: at n=10 the bar (0.930) sits BELOW the
  floor (1.0), so the band is empty and a **second extension can never fire** —
  every n=10 outcome is either immaterial or a winner. M-1 permits two
  extensions; the second is arithmetically unreachable. So the tree firing
  "once" is not a limitation, it is closure.
- The morning sheet's "progress so far" is what is true at ~04:20 MSK, minutes
  after the branch fires: one arm submitted, none read. That is the time the
  card fixed; the sheet says so in plain words rather than implying more.
- No arena action, no resident change, and no owner decision is taken by this
  patch. KEEP/REVERT remains the owner's, on the score with the named costs.

## The night was down when I arrived to deploy — incident 15:06:34Z

Deploying required a quiet window, so I waited for the A3 read to land before
touching the checkout. It landed at 15:06:19Z and the runner **died four
seconds later**, `Active: failed`, with a half-finished rebase in its working
tree. This was not caused by my patch — the crash is in `origin/main`'s runner —
but it would have recurred at the B5 read tonight, so it is fixed in the same
delivery.

**Cause, verified from the journal and the tree, not inferred.** The A3 read and
the B3 submission both succeeded. Publishing them did not: the coordinator had
pushed two commits to `agent/local_claude_1` (the composed-comparison addendum,
which appends to the same ledger, and the night-tree card) so the push was
non-fast-forward; the single `pull --rebase` retry conflicted on the ledger
(addendum-append vs row-append); the second push was rejected again; and
`git_publish`'s `RuntimeError` had nothing to catch it. Exit 1 with a live
rebase and **no HALT block anywhere**. `Restart=on-abnormal` correctly did not
restart it — a nonzero exit is not "abnormal" to systemd — which is why the
service sat dead rather than looping.

**Double-submission exposure: none, checked before touching anything.** One
traceback in the journal, six submissions in the state, no duplicate id. The
read happened once and the swap happened once.

**Recovery.** Conflict resolved keeping BOTH sides in append order,
`rebase --continue`, pushed to `agent/local_claude_1` and `main` as `0e4953b4`.
Nothing was discarded and no history was rewritten beyond the runner's own
unpushed commit, which is what a rebase is for.

**Three fixes so it cannot recur tonight:**

1. `merge=union` on `local_claude_1/door1-night-*.md` and `door1-vs-old-*.md`.
   The ledgers are append-only and have two writers; union is the correct
   driver and keeps both appends.
2. `git_publish` retries three times with a rebase between each, and **aborts
   any rebase it cannot settle** — the 15:06Z tree was left mid-rebase, which
   is what turned a failed push into a stuck checkout.
3. A publish failure now HALTs fail-closed — block written, committed locally,
   exit 2 — instead of raising through `main`. `halt(publish=False)` exists for
   exactly this case: pushing again when pushing is what failed only raises
   again.

    $ python3 claude_1/night-tree/test_publish_recovery.py
    Ran 9 tests ... OK

Nine tests, including the collision **reproduced against real git** in a scratch
repository — coordinator appends upstream, runner appends locally, runner
rebases — with the control that matters: **without** the union driver that
rebase conflicts and leaves `<<<<<<<` in the ledger; **with** it, both appends
survive. `git check-attr merge` is asserted on the real repository too, because
an attributes line that never resolved a real conflict is a claim, not a
defence.

## Deployment (VM `compute-vm-4-16-20-ssd-1785607330087`)

    checkout  /home/tarstars/prj/troll_farm-claude_1-lfs on agent/local_claude_1
    commit    3f189cad, pushed to agent/local_claude_1 AND main
    identity  sha256 f4f14c61...79816b9, byte-identical to the tested file
    attrs     git check-attr merge -> union, on BOTH ledger names, in the
              deployed tree
    suites    26/26 and 9/9 green run FROM the deployed checkout, not only mine
    dry-run   python3 cgauto/night_runner.py --state ... --ledger ... --once
              --dry-run  ->  "not due: 6m elapsed"  (exit 0)
    service   restarted 15:12:55Z, active (running), Main PID 3658317, unit
              unchanged (Restart=on-abnormal stands, for the reason above)
    next read B3 at ~17:01Z; B5, where the tree fires, at ~01:20Z

The restart was taken deliberately in the ~2 h gap immediately after a read and
its swap, when the state file is settled and no submission is in flight — a
restart mid-submit is the one thing that could cost the night.
