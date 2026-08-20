---
schema_version: 2
type: handoff
task_id: 20260819-osc031-forecast-fix-door1b
from: claude_1
to: ["local_claude_1", "user"]
cc: ["codex_1"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260820T144705Z-20260819-osc031-night-tree-card.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260820T151421Z-20260819-osc031-forecast-fix-door1b-handoff.md
created_utc: 2026-08-20T15:14:21Z
artifact_ref: agent/claude_1
artifact_commit: 84d3624b303923e13cd1424259f2335778083bc5
artifact_paths: ["cgauto/night_runner.py", ".gitattributes", "claude_1/night-tree/night-tree-implementation-2026-08-20.md", "claude_1/night-tree/test_post_b5_tree.py", "claude_1/night-tree/test_publish_recovery.py", "claude_1/night-tree/mutation_control.py"]
---

- To: local_claude_1, user
- CC: codex_1
- Task: 20260819-osc031-forecast-fix-door1b
- Requires acknowledgement: yes

# handoff: NIGHT TREE IMPLEMENTED AND DEPLOYED — and the night was down when I got there

Card discharged by delivery, ~10 h ahead of its clock deadline. The tree is
live in the VM night-runner lane, tested against synthetic completed states in
both branches, and running as PID 3658317 since 15:12:55Z.

## What is deployed

One patch to `cgauto/night_runner.py` — no supervisor, no second process, no
new unit. After the B5 read the verdict is computed exactly as before, and then:

- **|mean| in [1.0, bar)** -> M-1's own extension: pairs A6..B10 appended to the
  same plan with the same arms, next arm submitted at once.
- **otherwise** -> **session 3** opens immediately: fresh state
  `local_claude_1/door1-vs-old-2026-08-20-state.json`, fresh ledger
  `local_claude_1/door1-vs-old-2026-08-20.md` (arms, pre-registration and the
  nine named costs in its header), arm A submitted at once, and **the running
  process rebinds to the new files and keeps going**.
- **Either branch** publishes the OWNER MORNING SHEET as a coordination message,
  gated on `lint_outbox.py`'s exit status.

The rebind is the part with teeth. Without it the loop re-tests
`reads >= plan` on the finished session-2 state, breaks, prints "block
complete" and exits — and `Restart=on-abnormal` does not restart a clean exit.
Session 3 would sit submitted and never read. There is a test for exactly that.

## One thing I changed rather than flagged: the bar depends on the block size

The pre-registration says bar **1.315 at n=5** and **0.930 at n=10**. The runner
had 1.315 as a constant, so an extended block would have been graded against the
5-pair bar — a true +1.0 result reported to the owner as "between the floor and
the bar" when at n=10 it is a **winner**. `bar_for(n)` now carries both
pre-registered literals and the verdict block prints the n it used.

A consequence worth stating: at n=10 the bar (0.930) sits BELOW the floor (1.0),
so the band is empty and **a second extension can never fire** — every n=10
outcome is either immaterial or a winner. M-1 permits two; the second is
arithmetically unreachable. The tree firing once is closure, not a limitation.

## The night was dead when I arrived to deploy — 15:06:34Z, not my patch

I waited for the A3 read before touching the checkout, so I would restart in a
quiet window. It landed 15:06:19Z and the runner died four seconds later.

**The read and the swap both succeeded** (A3 = 23.4 @ 28/176; B3 submission
41168001). Publishing them did not: two coordinator commits had moved
`agent/local_claude_1` (the composed-comparison addendum — which appends to the
same ledger — and this card), the push was non-fast-forward, the single
`pull --rebase` retry conflicted ledger-append against ledger-append, the second
push was rejected again, and `git_publish`'s `RuntimeError` had nothing to catch
it. Exit 1, live rebase in the tree, **no HALT block anywhere**, service dead
for ten minutes. `Restart=on-abnormal` was right not to restart it.

**No double-submission exposure — checked before touching anything:** exactly
one traceback, six submissions, no duplicate id.

Recovered by keeping BOTH sides of the conflict in append order, continuing the
rebase, and pushing `0e4953b4` to `agent/local_claude_1` and `main`. The read
log continues below the addendum section from A3 onward. Full incident note is
in the ledger itself.

Fixed in the same delivery, because it would have recurred at the B5 read
tonight: `merge=union` on both night-ledger names; three publish attempts with
a rebase between each; **any rebase that cannot be settled is aborted** rather
than left behind; and a publish failure now HALTs fail-closed instead of
crashing. Reproduced against real git in a scratch repo, with the control that
matters — without the union driver that rebase conflicts, with it both appends
survive.

## Verification

    python3 claude_1/night-tree/test_post_b5_tree.py       26 tests OK
    python3 claude_1/night-tree/test_publish_recovery.py    9 tests OK
    uvx pytest tests/test_inbox_sweep.py tests/test_lint_outbox.py
                                                          119 passed
    python3 claude_1/night-tree/mutation_control.py        all controls held

The tree suite drives the **real main() loop** in both branches with the arena,
the submitter, git and the lint stubbed, plus a mid-block regression case
proving an ordinary read behaves exactly as before. The morning sheet is
validated by the **real transport validators** in both branches — a sheet the
runner cannot publish is a sheet the owner never reads — and if the lint ever
rejects it, the sheet is unstaged and preserved outside the message namespace
so no rejected message is ever committed and no lint failure costs the night.

Controls, because a check that cannot fail is not a check: `origin/main`'s
runner driven to the same completed block records the verdict and stops — that
is the gap, demonstrated. Six mutants (band closed at the bar; bar ignoring
block size; three pairs not five; switch never applied; rejected sheet committed
anyway; extension forgetting to submit) were each **killed**.

## Deployment

`3f189cad` on `agent/local_claude_1` and `main`; deployed file byte-identical
to the tested one (`sha256 f4f14c61...79816b9`); both suites re-run **from the
deployed checkout**; `--once --dry-run` against live state returns
"not due: 6m elapsed"; service restarted 15:12:55Z, active, unit unchanged. Next
read B3 ~17:01Z. The tree fires at the B5 read, ~01:20Z.

## For the owner, in plain words

It is armed, and it is honest about what it does not know. At about four in the
morning the machine grades the title fight; if the score demands overtime,
overtime starts by your own rule; otherwise the direct comparison you called the
gold standard begins at once. Either way a plain-words sheet will be waiting in
the record at 09:00 with the arithmetic, the composed three-generation distance
under both uncertainties, the nine named costs, and which branch fired. Nothing
is kept or reverted by the machine — that ruling stays yours.

One caveat I will not hide: the night lost ten minutes to a crash tonight, and
it lost them silently. It is fixed and tested, but the honest lesson is that the
unattended lane had one failure mode nobody had exercised, and it was found by
walking into it rather than by review.
