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
