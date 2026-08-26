# claude_1 status — wake #120, 2026-08-26

**Both of the last card's waits resolved, and for the first time in this run neither produced
follow-on work.** The owner's ~11:30Z ceiling reached me as `local_claude_1@20260826T113907Z` and
codex_1's `114250Z` acked it the same minute: Candidate 3 got exactly one r5 and one review, the
review returned the allowed BLOCK, so **Candidate 3 is closed**. In the same sweep codex_1 delivered
`453c4c89`, the repair of the P4b v6 BLOCK I raised last wake. **The ceiling is accepted without
dispute and the P4b repair is ACCEPTED on evidence.** My queue is drained.

## The Candidate 3 close — accepted as written, and I opened nothing in its place

`114802Z`, ack-not-required, because nothing is owed back. The bound said a second BLOCK at r5 closes
the task with no r6 and no re-tuning; codex_1's r5 review returned that BLOCK. Three items my own
card `113820Z` had listed as *waiting* are therefore **closed rather than postponed**, and get no
replacement cards: the r6 ruling, the Candidate 3 build/panel/G-1, and the Candidate 2 re-run on top.

**r6 crossed the ceiling in flight** — published `113736Z`, about a minute before `113907Z` arrived.
It stays in the tree as a **record of the repair r5's BLOCK required** and is explicitly **not** a
review request. codex_1 is right that he did not review it and right that reviewing it would reopen
a closed task.

Two consequences written down so they are not later misremembered:

- **`RW_COUNTER` closes unruled.** r6 **struck** the `rw` field codex_1 recommended **adding**,
  because his own accepted §10 item 3 had already removed that always-zero counter under the name
  `rb=`, so requiring it reintroduces what he removed. Nobody ruled and nobody now will. I adopt
  codex_1's framing exactly: **a procedural close, not a technical verdict** for either side. I am
  not pressing it and I do not claim the closure vindicates me.
- **r5 §7's prediction is never tested.** "Plan-keeping needs no new machinery" was to be falsified
  by `m061`'s `PICK`↔`DROP` two-cycle surviving a Candidate 2 re-run that will not now happen.
  Recorded as **untested**, not as supported.

## The P4b repair — ACCEPT, proved old-versus-new rather than read off the diff

`114911Z`, artifact `claude_1/reviews/p4b-narrator-param-repair-verification-2026-08-26.md` at
`agent/claude_1@674f973a`. I extracted the **pre-repair** gate `cfcb9688` and the repaired
`453c4c89` into **separate** scratch trees so neither could shadow the other on `sys.path`, then put
the same inputs through both.

- **F1, the BLOCK — repaired.** `evaluate()` now indexes `unit[1], unit[2]`, which is what
  `decode_units()`'s `>= 4` contract actually guarantees. My own repro from the BLOCK, unchanged:
  the five-field v6 tuple gives `UNCAUGHT ValueError: too many values to unpack (expected 4)` on
  `cfcb9688` and **returns normally** on `453c4c89`, matching its own four-field control. I checked
  the surrounding level too, since the BLOCK was itself about checking the wrong level: `decode_units`
  is the only call site, it sits **inside** the `try/except` that appends to `errors`, and the loop
  below can no longer raise for any width `>= 4`. Short tuple → counted error; wide tuple → consumed.
  Neither is a traceback.
- **F2, the non-blocking finding — repaired.** Same two-arm all-`none` invocation through both gates:
  `all_applicable_arms_ready` is `true` on the old gate and **`false`** on the new one, and it is in
  `required`, so a non-evaluable run is no longer exit-code-indistinguishable from a `PASS`.
- **No regression, run in full rather than argued.** `reproduce_v5.py` rebuilt both 240-game archives
  from the hash-pinned configs in my own scratch (exit 0), then the **repaired** gate: **16 / 27**
  failed units, **7,137 / 8,839** all-available windows, **277 / 268** blind unit lives, 76,364
  transitions, 53,708 windows, 384 unit lives, `K3`/`K5`/`all_applicable_arms_ready` true,
  differential `PASS` with no added unit key, gate exit **0**, `verify_v5_counts.py` exit **0** with
  `matches: true` on both arms, 11 unit tests OK. Identical to the accepted row in **every** field,
  so the indexing change is behaviour-preserving **as executed**.

**Recorded in the ACCEPT, not raised as a finding:** the v6 arm is exercised **only by fixture** and
never by a real archive, because the ceiling closed the only v6 producer. Written down so the
instrument's coverage is not overclaimed later.

## The ladder and the owner's goals

Read and obeyed. Champion `547fa706…` is on the ladder as submission **`41197542`** by the
coordinator's hand, the NARRATE instrument is off it, and **nobody else touches the Arena** — I have
not and I propose nothing. Goal (c) noted: **≥ 25.40 stands but is not the only goal**; the readable
source / diffs-in-files / owner-reads-every-change line is wanted **for its own sake**; the **banana
farm is next**, with the coordinator's assessment going to the **owner** first and **no charter yet**.
I hold no banana-farm work and open none.

## This ritual, in whole

No code of my own, no build, no panel, no Candidate 2 stacking, no Arena action, no platform
measurement, no lock, no timer. Two acks and one replacement card published; one verification
artifact written; the v5 reproduction re-run end-to-end in scratch.

**Open and not mine to close:** the **23 of 34 fixtures `NOT_REPRODUCIBLE_ON_BASE`** on every arm and
the shipping-form question (both `local_claude_1`'s); `format_readable.py`'s header template being
wrong for any non-minified parent (recorded in `docs/readable-format.md`, generator still
unchartered); and the **residual walk-back the capacity middle does not close**, which rode on a
panel that will now not run and is therefore carried as an unmeasured property of **the base**, not
of any candidate. **Nothing measured says the candidate's C-5 = 5 is benign** — that STOP AND ASK
stands and is the owner's.

Standing card (wake #120): `20260826T115018Z-20260826-queue-drained-deferred.md`, which discharges
`20260826T113820Z`.
