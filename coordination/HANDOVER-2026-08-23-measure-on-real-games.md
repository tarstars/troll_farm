# HANDOVER 2026-08-23 — the ladder cannot see the cure programme, so the next job is the instrument

Entry: this file → `docs/STATE.md` (§1 rewritten, now true) →
`docs/DISCUSSION-architecture-over-score-2026-08-22.md` → `docs/BACKLOG.md` (re-ranked at the
top) → task records. Ritual unchanged: `python3 scripts/inbox_sweep.py --me local_claude_1
--fetch` → read ALL new → `--mark` as its own step.

Supersedes `coordination/HANDOVER-2026-08-21b-flush-delta.md`.

## The state in six lines

1. **The Arena is deliberately STOPPED** with the champion `547fa706…` resident.
   `NIGHT-HALT` is present on the VM and `night-runner.service` is `failed` **on purpose**
   (owner ruling: "let this block finish, then halt"). To resume: delete the file, start the
   service. `agent-launcher.service` is **active**; claude_1 and codex_1 are awake and working.
2. **The headline measurement: the cure programme is invisible on the ladder.** Ten pairs,
   champion vs the bot two generations back: **+0.17, ≈0.00 symmetrised** against a composed
   estimate of +1.24 (`local_claude_1/door1-vs-old-pooled-verdict-2026-08-22.md`).
3. **The second measurement: our evidence base is a biased sample** — 34 hand-picked fixtures on
   a retired bot. The owner raised this independently and it re-ranked the backlog.
4. **NARRATE is the new P0** (`coordination/tasks/20260823-narrate-real-game-telemetry.md`):
   the bot prints each troll's target every turn via `MSG`, and we grade real games instead of
   fixtures. The capability audit is done and verified. **Step 1 is one Arena submission and
   needs the owner's go.**
5. **The swap cure is verified and parked.** 32 of 34 healed events carry real progress
   (instrument accepted by codex_1, with P4 side-level: all 16 of its healings retain one
   non-progressing unit). It cannot advance — see §PEEK below.
6. **Owner queue: one item** — NARRATE step 1's go, which means putting an instrument on a
   ladder we just stopped. Nothing else waits on them.

## What changed in this session, by area

**Coordination, all deployed and verified**
- **The wake rule** (owner: *"claude shouldn't awake without incoming emails"*). The launcher was
  already mail-gated; **the mail was the agent's own**. Now an agent is woken only by mail from
  someone else: its own cards, `cc`-only mail, courtesy receipts and any `DEFERRED:` card wake
  nobody. One predicate in `inbox_sweep`, both consumers read it. Measured before/after:
  queues 1 and 6, wake sets 0 and 0. codex_1 re-ran the suite itself and accepted.
- **Protocol review, six further defects fixed**: §1 named a dead branch and a roster missing
  codex_1; §4 lacked the `update` kind and the `to`-only ack rule; §6 demanded a bar the owner
  removed nine days earlier; §7 had the cron at 05:17 (it is **02:17 UTC**); new §11 "rules about
  rules".
- **`docs/STATE.md` §1 rewritten** — it named the *retired* bot as resident with a restore target
  pointing at it. Also trimmed to exactly 150 lines; `tests/test_doc_budgets.py` was **already
  red** before this session (172 lines) and is now green.

**Measurement, and two real defects found**
- **Pairing:** blocks now run **ABBA** and the difference is taken **A−B by arm, never by
  position**. A fixed order put arm A in the earlier slot of every pair, so drift entered every
  difference with a fixed sign. `docs/METHODS-LEDGER.md`, `paired-order-carries-the-drift`.
- **The runner no longer restarts the block it just finished.** It did that twice, erasing both
  verdicts before they reached a commit and firing two unordered submissions. Also: the owner
  sheet no longer names arms it did not measure, nor composes a direct measurement with itself.
- **"Healed" now means healed WITH PROGRESS**, never detector-silent, on the cure's bar and any
  future one. Raised by `chatgpt_1`; the fixture grader already knew the difference and the
  acceptance rule I had proposed did not.

**Rulings made (do not re-litigate)**
- **extend-versus-replace: the idle fallback must EXTEND, not rebuild.** It re-seeds the WAIT and
  re-adds banking but forgets the replant PICKs; both flags are switched on two lines apart. An
  omission, not a design. Progress is **not** claimed and scope is locked to 101 turns in one game.
- **Corpus authoritative and pinned**: 21,496 games, 8,590 ours across 86 agent ids, complete
  through 08-22. `local_claude_1/corpus-identity-2026-08-22.md`.
- **`Target::None` may NOT be read as permission to displace** — see PEEK.
- **chatgpt_1 revived** as a fresh-eyes architecture partner, no verdict authority; its position
  is delivered and assessed; its publication gateway is **backlogged** with three conditions.

## PEEK — built, inert, and the finding is better than the fix

`coordination/tasks/20260822-peek-planner-target-map.md`. Rev 3 was built exactly as ruled and
**fires zero times in 34 fixtures**; claude_1 reported it as a G-1 failure rather than dressing a
vacuous zero as a pass, and codex_1 reproduced the negative.

Why, over **989 partner encounters**: 960 declines because a waiting troll carries
`Target::None` — the program never forms an intention for a standing unit — and 29 because a
working troll's target is its own cell, which is the contested square.

**The owner-requested intention measurement then inverted the design.** The want *does* exist one
step earlier and the selector discards it: of 2,605 benched turns, **2,245 (86 %) had a real
want**. Reading it: **2,010 wanted to stay and work**, **235 wanted the same square the partner
was taking**, and **0 wanted a different square** — the only shape displacement could serve. So
supplying the missing fact makes displacement **refuse**, not fire wisely.

**Limits, and they bound the conclusion:** that is the *retired* bot on the *benching* case set,
biased by construction. The confirming run is carded to claude_1 (champion, over the 989
encounters) — and NARRATE would answer it far better, on real games.

## Who owes what

| party | owes |
|---|---|
| **owner** | NARRATE step 1's go (one submission, ladder currently stopped). Nothing else. |
| **local_claude_1 next session** | the inbox (**32 unread, 7 unacked at flush**); the swap cure's residual-13 disposition and cure-arm basket criterion (both mine, both now parked behind NARRATE) |
| **claude_1** | the champion-side intention classification (carded); anti-benching Phase 3b build, queued |
| **codex_1** | Phase 3b design review round; standing deferrals |
| **chatgpt_1** | nothing; quiet since 2026-08-22T19:04Z |

## Traps — each cost something this session

- **Never count corpus membership with a text match.** JSON spacing varies; two greps gave 1,057
  and 1,549 for the same question, and parsing gave **8,590**.
- **The replay adapter's alignment trap:** 301 states against 300 command rows, and `Trace`
  truncates to the shorter list with only a note. A one-turn shift would silently mis-grade
  thousands of games.
- **Five reds in `claude_1/night-tree/test_post_b5_tree.py`** are ABBA order-pins in claude_1's
  namespace. Not a regression, and not mine to edit — carried to it as a note.
- **`docs/PROMOTION-RUNBOOK.md` must not be followed as it stands** — its abort path restores the
  wrong bot.
- **An instrumented bot can never be the champion.** It changes the command stream, so no
  byte-identical parity against the champion can pass; it is a measuring instrument, run and
  retired.

## Corrections of record I made this session, so they are not re-made

The widening was labelled **"owner-blocked" and the owner never had it** — the reviewer said
"coordinator *or* owner", a headline compressed it, and I repeated it twice. The structural
property I proposed as an architecture target **was already built and measured as insufficient**.
The "1.4 vs 3.64" comparison was **mine and invalid** — different units — and it sat in the brief
I wrote for chatgpt_1, which also reintroduced an argument I had withdrawn hours earlier. The
roster claimed 9 quarantined messages for chatgpt_1; it is **6**. `coordination/peer-prompt.md`
told every newcomer that `session-2026-07-01` tracks `main`; it has not moved since 08-17.
