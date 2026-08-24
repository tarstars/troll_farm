# claude_1 Status

- Updated UTC: 2026-08-24T16:39:00Z (REAL clock, `date -u`)

## WAKE #83 (2026-08-24T16:34Z) — G-1 came back REVISION_REQUIRED and both blockers were real; r2 published, still nothing counted

Two new messages. I published two, marked, and pushed.

- **`codex_1` ruled `REVISION_REQUIRED` on my r1 definitions, and I verified both blockers against
  the code before repairing them.** Both are correct. R1: `build_oscillation_library.py:198` is
  `for p in st0.own_units()` — peers alive at `turn_start`, not "alive in the window" as r1 claimed;
  two names for one fact domain, my error. R2: `classify` returns `M3` only under `if not peers`,
  and peers-present-with-no-blocker is a **fourth** output, `UNCLASSIFIED`, which r1's crosswalk
  silently merged into `M3`. r1's sentence "M3 maps to no blocker" is withdrawn as wrong in those
  words.
- **r2 is published at `claude_1/dance1/definitions-g1-r2-2026-08-24.md`, `agent/claude_1@fa5a5b8c`,
  handed to `codex_1` at `20260824T163700Z`.** F3 narrowed to the imported function's own
  population; later-appearing peers become **F3b**, marked NEW and explicitly not claiming import,
  entering no class predicate and *sized* in a required report table rather than dropped. A
  mechanism layer `mech` (five values, F3 only) with a **total** crosswalk over all four frozen
  outputs; K2 passes only on exact equality over all 38 episodes, with telemetry structurally
  locked out of that control. All four of the reviewer's non-blocking requirements adopted.
- **Found while making the population exact, not asked for:** `measure_blocker` filters `None` from
  `cells_win` and counts a dead peer's absent command as a wait, so a peer that **dies mid-window**
  can read as a single-cell idle blocker. I did **not** change the accepted function. Added one
  observable (`turns_alive_in_window`) that enters no criterion, and a cross-tab; if it is material
  the report names it as a limitation of the inherited criterion rather than re-ruling the episodes.
- **I moved a boundary after the review and said so in the handoff rather than burying it.** r1
  ranked `SWAP_FLAP` first, justified by the charter's swap-origin hypothesis. The coordinator's
  `20260824T162800Z` refutes that hypothesis: the champion has **no swap rule** and dances at
  **16.8 %** against the very-old bot's **17.4 %**, **+0.00 pts over 2,268 games**. So r2 puts the
  mechanism classes first and `SWAP_FLAP` third. **No class distribution exists under either
  ordering** — nothing has been graded — and the mandatory swap × blocker cross-tab makes r1's
  counts reconstructable cell for cell. I invited `codex_1` to rule on the reordering itself.
- **The real-game dance rate is ≈ 17 % of games, not 11 %.** The 08-23 figure was one batch of the
  lowest-reading bot. The instrument's 14.6 % vs the champion's 16.8 % is **not established** as a
  difference (446 games, p = 0.25, confounded by day) and I will not report it as one.
- **The second pass is triggered and has not begun.** 306 champion games / 382 episodes at
  `agent/local_claude_1@4b9bd563`, received and acked at `20260824T163500Z`. No battle listing
  exists for those agents; **none is claimed and I will not reconstruct one.** No telemetry, so r2
  makes the comparison exact: `mech` and classes 1–3 are literally the same function on both
  corpora; classes 4–6 collapse to `NO_TELEMETRY`. Grading begins only after G-1 is accepted.
- **I built nothing and measured nothing this wake, again, and that is still the assignment.** No
  batch graded, no fact table, no episode inspected, in r1, in the review, or in r2.
- The coordinator's `k = 3` question (159 of 382 episodes) is adopted as a **required report table**,
  not as a new criterion — evidence for whether the inherited criterion is load-bearing at short
  windows, with no count adjusted by it.
- **Posture unchanged:** no Arena action, submission, TestSession, fetch, sealed-data access or
  resident mutation, in this wake or in any phase of this task. Next wake gated on `codex_1`'s
  second G-1 ruling — a queue item, not a card.
- Deferrals: none.

## WAKE #82 (2026-08-24T16:16Z) — chartered again, as builder; definitions published before any count exists

Five new messages. I published two, marked, and pushed.

- **I have a live card again: `20260824-real-game-dance-attribution`, builder.** The coordinator
  chartered it at `20260824T160300Z` on the owner's "do it". The question is the owner's, in plain
  words: real ladder games show trolls blocking each other **0 times in 469 games**, yet dancing in
  **~11 %** — 22 episodes in 17 of the first 149 — and those 22 are counted, not explained.
- **My standing card is discharged, not carried.** The charter is the "new charter addressed to me"
  unblock signal its return condition named; discharged by `ack_for` at `20260824T161700Z`, as the
  charter instructed. The cross-task `ack_for` is deliberate and is noted in the message.
- **I built nothing and measured nothing this wake, and that is the assignment.** Step 1 is
  definitions-first: `claude_1/dance1/definitions-g1-2026-08-24.md` at `3c87ab0b`, handed to
  `codex_1` for gate G-1 at `20260824T161800Z`. No batch graded, no fact table, no class assigned.
  A boundary chosen with the counts in view is not a measurement.
- **What is inherited and what is mine, stated before the ruling.** Inherited by *import*, not
  restatement: `detect_d1`, the adapter, and the library's IDLE (`≥0.95` wait, 1 distinct cell) and
  blocker (1 cell + orthogonal adjacency, lowest id on ties) criteria. Mine and marked NEW: the F4
  telemetry summary labels and the F5 swap-tick predicate.
- **One correction to my own card, published before the run.** The card cites `RULES-LEDGER` R-1 for
  "the 290 replays' bot never generates swaps". R-1 actually says *"today's resident never generates
  them"*, written 2026-08-16 about that date's resident — not a verified property of agents
  6536563 / 6536359. K3's negative side is therefore a **joint** test of detector and premise, and
  if it fires the report will name which is in doubt rather than picking the convenient one.
- **One instrument that does not exist yet, raised now rather than at G-2.** There is no standalone
  v3 replay decoder; v3 decoding lives inside `run_gp3_parity.py:67`. I will lift it into
  `claude_1/dance1/` behaviour-unchanged and prove equivalence on the gp3 parity corpus first.
- **Quarantine synced, not adjudicated.** My local copy differed from the authority on
  `agent/local_claude_1` in `adjudicated_by` and nothing else — the role-fragility defect both
  coordinators have now recorded. I copied the authoritative blob; I assert no adjudication.
- **Posture unchanged:** no Arena action, submission, TestSession, fetch, sealed-data access or
  resident mutation, in this wake or in any phase of this task. Next wake is gated on codex_1's G-1
  ruling — a queue item, not a card.
- Deferrals: none.

## WAKE #81 (2026-08-24T11:27Z) — my queue is empty because the owner emptied it; the lease I broke, and the falsifier that found me anyway

Fourteen messages had accumulated since 2026-08-23T15:56Z. I published four, marked, and pushed.

- **I built nothing and measured nothing this wake.** The only number-bearing artifact I published
  compares an old local run against an already-published result.
- **I breached the 16:52Z activation lease and I say so without softening.** My G-d driver finished
  locally at 16:11Z; the acknowledgement of the PROCEED ruling was still uncommitted in my worktree
  when the session ended. `local_codex_1`'s blocker at `20260823T165223Z` is correct: from every
  peer's side `origin/agent/claude_1` was still `e6cb7523…` and the panel was correctly treated as
  unstarted. Unpushed work does not exist. Acked at `20260824T113600Z`.
- **The drafted proceed-ack was deleted, not published.** It promised a handoff that the 17:11Z
  transfer made impossible. It never reached an authoritative ref, so nothing was retracted.
- **All three of my live cards were transferred to `codex_1`** by owner instruction
  (`20260823T171116Z`), accepted at `20260823T172247Z`. I hold **zero live cards** and carry one
  card only — the return condition for any of the three — re-issued at `20260824T114200Z`.
- **G-d is dead on the science, not merely reassigned.** `codex_1` built it and returned BLOCKED at
  the first falsifier: 115 blocking against 35, 80 de-novo, zero healed, failing P3-clean,
  no-new-P4 and blocking-totals. Anti-benching r2 is rejected.
- **Independent corroboration, published at `20260824T113800Z`.** My unpublished run and
  `codex_1`'s authoritative one agree on every headline count and the **80 de-novo games are
  set-identical** by direct `(map_id, seat)` comparison — symmetric difference empty both ways. Two
  analyzers written without sight of each other name the same games; the falsifier is not an
  artifact of one implementation. One definitional discrepancy, 86 vs 85 changed games: `codex_1`
  sees `m004 s0` losing P3 where my floor panel's P3 column is `0` by construction and cannot see a
  loss (its base column is the better one); I see `m061 s0/s1` moving only detector totals where the
  authoritative decomposition counts property and flag changes only. Neither touches any R-3 clause.
- The scratch is committed at `claude_1/gd1/` with a README declaring it inert on its first line.
  Kept rather than deleted because it is a genuine second implementation; publishable as
  corroboration only, never as a package.
- **`local_claude_1` is coordinator, integrator and sole Arena controller again**
  (`20260824T112055Z`), acked at `20260824T114000Z` — verified in
  `origin/main:coordination/roster.json@85689d80…` and in my own sweep's authority line, not taken
  on trust.
- **The quarantine is healthy this wake for a reason that is not a fix.** 12 quarantined, 0 errors,
  `--mark` operable — because the twelve entries were adjudicated by `local_claude_1` and
  `local_claude_1` holds the role again. `inbox_sweep.py` still validates `adjudicated_by` against
  the *live* roster, so the next transfer to a different coordinator voids all twelve again.
  Recorded, not repaired: the file is coordinator-owned. My branch's local `quarantine.json`
  (`43f699c4…`) differs from the authoritative blob (`0921f135c3dd`); the authoritative copy
  governs and I left the stale local copy alone rather than hand-edit a file I do not own.
- **Correct posture until a new charter arrives:** run the ritual, re-open nothing, shadow no
  `codex_1` lane, write into no other namespace.

## WAKE #79 (2026-08-23T14:36Z) — transport only: `local_codex_1`'s assumption is live, and `codex_1`'s split digest confirms the panel-digest defect by measurement

Five messages arrived: `local_codex_1`'s handover ack and **assumption policy**
(`20260823T143030Z`, requires_ack), and three `codex_1` acks. I published three messages, marked,
and pushed.

- **I built nothing, measured nothing, ran no instrument this wake.** Stated plainly because a
  cards re-issue that reads like a delivery is a failure mode I have hit before.
- **`local_codex_1` is now coordinator, integrator and sole Arena controller**, effective on its
  published assumption. Acked at `20260823T143621Z`. The coordinator of record my cards name is
  therefore a live role-holder rather than a pending one — **a transport fact, not a ruling.** Its
  policy explicitly declines to open the G-d gate and says it will rule separately after reading the
  evidence; **a stated intention to rule is not a ruling.**
- **One open question closed by measurement.** `codex_1` returned
  `split_digest_sha256` = `7c2898ee…` against my `581392e4…`. Two independent executions,
  **byte-identical episode JSON**, identical reported results, **different panel digest** — the
  run-local split-basename dependence in `run_reach_panel.py` is now **demonstrated**, not merely
  localized. Acked at `20260823T143639Z`. The **defect is unfixed**; only the diagnosis is settled,
  and no delivered number moves.
- **Three cards carried, none discharged**, re-issued at `20260823T143705Z`: G-d (blocked — and the
  new lead's assumption policy is now a *third* thing that is not its unblock signal, alongside
  `codex_1`'s `METHOD_ACCEPTED` and the outgoing lead's described-pending correction);
  v3-on-real-games (advanced, waiting on the coordinator's mature corpus and identity pin, which I
  have not asked either lead for); panel-digest determinism (unblocks only on a charter that re-runs
  the instrument, fix first).
- I handed the incoming lead the caveat it would otherwise have had to discover: the v3 package's
  forbidden-key sweep was **not a clean zero** — `codingamer` present 320 times with
  `{"pseudo": "PLAYER_n"}`, reported as present-and-scrubbed, never as a pass.
- **Found by the ritual, not looked for: the transfer voided the whole quarantine.**
  `scripts/inbox_sweep.py:1030` validates each `adjudicated_by` against the coordinator **in the
  live roster**; all 12 entries were adjudicated by `local_claude_1`, so at the moment
  `origin/main:coordination/roster.json` named `local_codex_1` every entry errored and
  **quarantined went 12 → 0** with the blob byte-identical (`0921f135c3dd`). 7 permanently-invalid
  messages are live in my inbox again, 8 delivery errors resurfaced, 3 of them are wake-capable.
  Reported to the new coordinator at `20260823T143929Z` with two candidate repairs (ratify now;
  make adjudications durable against a roster history). **Not repaired by me** — `quarantine.json`
  is coordinator-owned. **And I could not even mute them locally:** `--mark` is fail-closed on
  delivery errors with no override, so it now exits 2 and refuses to advance seen-state. Step 4 of
  the inbox ritual is inoperable **fleet-wide** until the quarantine is restored; my seen-state is
  frozen at the 14:37Z mark, before the report itself. No card opened; none of my three cards is
  blocked by it, and I did not appoint myself the builder of the fix.
- **Independently corroborated.** `codex_1` published BLOCKER `20260823T143924Z` five seconds
  before my report, on a different branch and a different queue; neither of us saw the other's
  first. Same blob, same 12 → 0, same cause. His delivery-error count is 4 against my 8 because
  that count is queue-relative, not because either is wrong. Cross-reference published at
  `20260823T144118Z`, saying plainly that two reports of one defect are not two defects. What mine
  adds: `--mark` is fail-closed with no override, so the ritual's step 4 is inoperable fleet-wide.
- **The coordinator had already found it.** `local_codex_1`'s policy `20260823T143913Z` re-authorizes
  exactly the twelve inherited entries under its own name — authority only, no new path, reasons and
  `target_blob` pins untouched, no ack quarantined. Acked at `20260823T144235Z`, recording two facts:
  it is **not yet in effect** (`quarantine.json` still blob `0921f135c3dd`, sweep still 12 errors / 0
  quarantined, `--mark` still exit 2 — verified after fetch, so this ack is not evidence of health),
  and the **durability hazard survives the fix** — the next transfer voids it again unless
  adjudications validate against the coordinator *at adjudication time*. On the one entry that is
  mine to speak to, `local_claude_1`'s declared conflict, I do not request removal. Five of the
  twelve are my own messages; I contest none.
- **Resolved within the wake.** The coordinator pushed the repoint of all twelve `adjudicated_by`
  fields to its own policy path. Verified after fetch: **delivery errors 0, quarantine errors 0,
  quarantined 12**, and `--mark` succeeded (1,161 paths). Step 4 of the ritual is operable again and
  my seen-state is current. The **durability hazard is untouched** — the next transfer voids the
  quarantine again unless adjudications validate against the coordinator at adjudication time. Not
  my card; I build it if chartered.

## WAKE #78 (2026-08-23T14:24Z) — transport only: the lead passes to `local_codex_1`; three cards carried with the coordinator's name corrected, nothing built

`local_claude_1` published the owner's transfer (`20260823T142000Z`): **`local_codex_1` becomes
coordinator, integrator and sole Arena controller** on its own assumption message. Acked at
`20260823T142403Z`; cards re-issued at `20260823T142438Z`.

- **I built nothing, measured nothing, ran no instrument this wake.** Two messages, a mark and a
  push. Recorded plainly because a cards re-issue that reads like a delivery is a failure mode I
  have hit before.
- **Only a name moved.** Every unblock signal that read "a pushed ruling from `local_claude_1`" now
  reads **the coordinator of record (`local_codex_1`)**. Substance unchanged; a rename is not a
  discharge. Done as the instructed natural re-issue, not a special pass.
- **G-d stays DEFERRED and blocked.** Two things are still not its unblock signal: `codex_1`'s
  `METHOD_ACCEPTED` (a review opens no gate), and the outgoing lead's written statement that his
  13:14 ruling was too quick and its correction is his successor's — **a described pending
  correction is not a correction**. I will act on the written form, not on that paragraph.
- **v3-on-real-games stays advanced-not-discharged.** The mature corpus and its identity pin remain
  the coordinator's to publish. **I did not ask the incoming lead for them**, as I did not ask the
  outgoing one.
- **panel-digest determinism** carried: `split_digest_sha256` is computed from run-local filenames,
  which is the localized cause of `codex_1`'s panel digest differing from mine. Not re-run on an
  unchartered wake; no result changes if it is — the episode JSON is already byte-identical.
- Noted without acting on it: **18 messages unread on the outgoing lead's side at transfer**. I do
  not read silence as acceptance of any delivery of mine, and I did not re-send to force a reply.

## WAKE #76 (2026-08-23T13:34Z) — CHARTERED and delivered: Phase 3b's reach on real games is **339 turns / 34 episodes**, against **882**, not against 2,903

`local_claude_1`'s RULING `20260823T131400Z` chartered one targeted comparison. Panel **PASS 8/8**,
artifacts `agent/claude_1@d0fdcc62`, handoff `20260823T133206Z`, report
`claude_1/reach1/phase3b-reach-report-2026-08-23.md`.

- **The answer is not zero.** On the **49 of 160** games that pass the re-execution parity gate
  (111 REFUSED, contributing nothing) there are **882** nothing/nothing rows. The un-discarded
  options make the unit's `available` concrete on **339** of them — and make its `chosen` concrete
  on the same **339**. RESTORED = SELECTED here is a finding, not a tautology: the two columns are
  computed independently and the **poisoned control arm separates them (458 vs 443)**.
- **339 turns are 34 episodes**, over 23 (game, unit) pairs in **14 of 49** games; episode length
  1 / 6 / 9.97 / 35. Per game: **35 of 49 are zero**, median 0, max 74, worst decile 180 of 339.
  Neither number travels alone.
- Every one of the 339 is one shape: the best discarded candidate is a **replant `PICK`** (target
  `Cell`); base issues `WAIT`, EXTEND issues `PICK <id> <FRUIT>`. 255 turns differ in command vector.
- **The load-bearing control is telemetry identity**: 24,906/24,906 base-arm `(chosen, available)`
  rows equal the NARRATE v3 rows the bot **printed on the wire**, 0 mismatches — the base arm is the
  bot that played, checked rather than asserted. The **null fork is flat** (reach 0, 0 command
  differences, nothing/nothing unchanged at 882), which is what makes 339 a measurement; the
  **poison fork moves**, which is what stops the null fork's zero being vacuous.
- **I told the reviewer his own check cannot pass, before the review.** `codex_1` asked that the
  denominator be exactly 2,903; it is 882 and cannot be 2,903 by re-execution without dropping the
  parity gate. Note published at `20260823T133428Z` rather than left for the review to find.
- **Not established, stated in the delivery:** not "339 of 2,903" and not extrapolated; the verified
  49 are a **selected** set and the correlation between that selection and reach is unmeasured; one
  tick deep, divergence not simulated; no score; not the benched troll (615/166 is a different
  class); **nothing graded, no G-d, no cost decomposition, no Arena action.**
- **`20260821-swap-r1-cure` — DISCHARGED by the coordinator's `20260823T131600Z`**, which retires the
  residual 13 re-swaps and the cure-arm basket criterion on 0 contention episodes in 469 real games
  (detector live at 206/240 on control). The ruling says my card is discharged **by it, not carried**;
  acked at `20260823T133219Z`, not re-issued, nothing built toward it. Carried boundaries: not
  attribution, not score (+0.17 stands), not a theorem — one episode in a graded batch reopens it.
- **Forbidden-key sweep on the v3 package, run and NOT a clean zero:** `avatar`, `publicHandle`,
  `testSessionHandle`, `userId` absent (0 hits); the **`codingamer` block is present 320 times**,
  carrying only `{"pseudo": "PLAYER_n"}`. Reported as present-and-scrubbed, not as a pass.
- Cards after this wake: **G-d still blocked** on the discarded-want live measurement plus the
  coordinator's written ruling (**the reach measurement is NOT that signal**); **v3-on-real-games
  still advanced-not-discharged**, waiting on the mature corpus and its identity pin, which are the
  coordinator's to publish and which I will not ask for.

## WAKE #71b (2026-08-23T11:22Z) — the mid-wake idleness charter, delivered: 109 wanted-and-silent rows, and the class where the rest would hide is invisible to v2

`local_claude_1`'s charter `20260823T110000Z` arrived after my G-b messages were written, so it was
read and executed in the same wake. Panel **PASS**, 8/8 controls, `agent/claude_1@c563e449`, handoff
`20260823T112215Z`.

**Six classes, exhaustive, summing to 76,305 exactly.** `WANT_COMMANDED` 72,681 ·
`NO_WANT_SILENT_PARTIAL` 1,786 · `NO_WANT_SILENT_TEAM` 1,718 · **`WANT_SILENT_TEAM` 98** ·
**`WANT_SILENT_PARTIAL` 11** · `NO_WANT_COMMANDED` 11. **Wanted something real, achieved nothing =
109 rows, 0.14 %.** The 3,613 null-verb rows are classified, never dropped.

**I refused to define "serves the want"** inside `WANT_COMMANDED`, leaving 95 % of the corpus in one
class deliberately: every honest version of that boundary reads the observed joint table first, and
a boundary chosen with the counts in view is not a measurement. The joint table is published
unjudged instead.

**The 120 divergences are adjudicated by OBSERVATION.** A probe from the source that played the
corpus prints the command vector after `select_recording` and again after `resolve_move_conflicts`,
under the same whole-game parity gate. **54 of 54 adjudicable rows are post-selection rewrites and
none is anything else**: 45 rewritten to `WAIT` (38 `no-progress`, 7 `blocked-no-detour`), 9
manufactured by the swap branch, 0 unchanged. 66 rows sit in parity-refused games and are not
counted or extrapolated from. The 7 blocked rows are **not** a contention measurement.

**The finding that bounds the card is the instrument's.** v2 records the target of the candidate
that WON selection, so a troll idle with a discarded intention is recorded exactly like a troll with
nothing to want. That class is `NO_WANT_SILENT_*` — 3,504 rows, 4.6 %. The join measures
overruled-after-selection idleness completely and discarded-before-selection idleness not at all.
Carded as a v3 that is **not to be built unasked**.

**Published:** 2 more — idleness handoff `20260823T112215Z` (10 artifact paths) and standing cards
`20260823T112257Z`. The 120-row card is **discharged**, not carried. Every remaining card of mine is
blocked on a ruling, a charter, or host reach.

## WAKE #71 (2026-08-23T11:00Z) — G-b run on real games: **one** admissible Δ-B state in 149 ladder games, and the number is the finding

**Inbound (3):** codex_1's decoder review `20260823T104836Z` — **ACCEPTED**, 149/149 reproduced
independently, the seat ruling positive, fail-closed opponent-instrument refusal retained; their
`20260823T104945Z` ack; and `local_claude_1`'s G1 grading `20260823T105300Z` — contention 0 of 149
in our current bot's real play at matched unit count, dancing the defect that survived, idleness
ungraded pending the intention join.

**The card is DELIVERED.** codex_1's verdict lifted the HELD-UNTIL I had put on G-b myself, so G-b
ran on real games (`agent/claude_1@643b5690`, handoff `20260823T111239Z`). The states came from
re-executing the bot that PLAYED the corpus: the 149 games' source has a fallback body
byte-identical to the Phase 3b incumbent (checked in the builder, not by eye), the D-1 adapter
rebuilds our seat's referee input, and **a game contributes states only if the re-executed command
stream equals the recorded stdout for the whole game.**

**Panel PASS, and the headline is n.** 81 of 149 games re-execute exactly, 21,478 traced turns, 729
fallback entries, 4 carrying, **1 admissible Δ-B tick**. On it the multiset delta is exactly three
duplicate element-identical bank candidates and the Δ-B unit's command is identical after select and
conflict resolution. 0 §2 violations, 0 probe-inertness failures, **8/8 controls**. G-b is no longer
UNMEASURED and is nowhere near "Δ-B is inert" — anyone quoting the gate must quote the 1.

**The easiest wrong answer, refused.** That turn's command vector does differ — unit 1's `WAIT`
becomes `PICK 1 APPLE` — and that is **Δ-A on the sibling**. The panel attributes fork differences
by unit id. Two further Δ-B ticks exist in refused games; both fall after their game's first
divergent turn, so neither was promoted.

**The control that carries the rest:** a poisoned EXTEND body must make the fork report a change on
the Δ-B unit itself, and it does, on the same turn. Without it, `same=true` on one tick is
indistinguishable from a fork that cannot see anything.

**A second finding, not about G-b.** 68 of 149 games do not re-execute exactly, median first
divergence turn 64, often transient. First quantification of the D-1 adapter's declared caveat that
plant clocks are reconstructed, not observed. Held narrowly: it does not invalidate D-1/D-3 replay
grading, which reads observed fields.

**I did not promote my own result into my own next gate.** G-d's unblock-signal is met on the letter
of it and I put a **HELD-UNTIL a `local_claude_1` ruling on whether n = 1 counts as "measured on real
games"**. Every G-d travelling condition is intact.

**Not done, and not attempted:** no promotion, no progress claim, no cure claim, no Arena action, no
fetch, no submission, no edit to `cgauto/submissions/`, nothing under `data/raw/games/`.

**Published:** 2 — G-b handoff `20260823T111239Z` (8 artifact paths at `agent/claude_1@643b5690`,
ACKing codex_1's review, local_claude_1's G1 grading and my own build handoff) and standing cards
`20260823T111331Z`.

## WAKE #70 (2026-08-23T10:40Z) — the NARRATE v2 decoder: 149 of 149 real games, 76,305 join rows, 12/12 controls, and a mis-joined seat is unspellable

**Inbound (3):** `local_claude_1`'s **charter** `20260823T103000Z` — the platform condition is
DISCHARGED on 20 real ladder games (5,257 turns, 0 decode errors, both seats, 0 leak) and I am
chartered to build the NARRATE decoder, with 149 gzipped replays supplied because my host holds no
platform credential; their ack `20260823T103300Z` recording codex_1's `ACCEPTED_WITH_UNMEASURED_G_B`
and flagging — without ruling — that my prevalence card's NARRATE unblock-signal now has a corpus;
and their mid-wake policy `20260823T104000Z`, a self-addressed queue anchor (their cards, no
bystander ack).

**The card is DELIVERED.** `claude_1/narrate1/narrate_decode.py` + `narrate_controls.py` +
`run_narrate_panel.py` at `agent/claude_1@b62e5ec2`, handoff `20260823T104109Z`. Panel **PASS**:
**149/149 games decoded end to end, 0 refused, 38,869 traced turns, 76,305 join rows (turn × own
unit alive), 0 telemetry on the opponent's seat, 61 games as seat 0 and 88 as seat 1, 12/12
controls fired.** Corpus digest `sha256:4393d05c…`, `git archive`-extracted to local scratch
outside the repo; the games directory is a parameter and `data/raw/games/` was neither read nor
written.

**Requirement 1 was the whole point and it is met by construction *and* by measurement.** There is
no seat parameter: the only identity `decode_game` accepts is `agent_id`, resolved against the
replay's own `agents` array, so the battle listing's `position` cannot enter — this module never
sees a battle listing. On top of that, per game, our telemetry must be present on our seat every
traced turn and **absent** on the other or the game is refused. Control 2 spends the *opponent's*
agent id on a real replay and gets a refusal naming 262 leaked turns; control 3 injects one `MSG
NARRATE` on the other seat and is refused with a count of 1. The coordinator's `position`/`agentId`
mis-join is now a control that fires rather than a caution.

**Two facts I put in the handoff rather than letting a reviewer find them.** `SHACK` occurs **0**
times in 149 real games — four of five target shapes are exercised live, so the sweep is not
grammar coverage. And **intention ≠ command on 120 of 76,305 rows** (`TREE|no-command` 104,
`BANK|no-command` 5, `NONE|MOVE` 11); none is a decode error, those are refused. The candidate
mechanism is post-`select_recording` command rewriting (conflict resolution, door-unblocking and
idle-harvest injections) and I named it **as a candidate, not an assertion** — 120 rows is small
enough to adjudicate exactly and that is not this card's scope.

**One thing the coordinator's 20-game check did not reach:** a fifth unit-id set, `(1,4)`. The
decoder takes the roster from the state, not from an assumed id pair, so it needed no change.

**Cards moved on evidence, not on a ruling** (`20260823T104232Z`). **G-b's UNBLOCK-SIGNAL is MET** —
the real-game NARRATE corpus it asked for exists and the reader for it is delivered — and I put a
self-imposed HELD-UNTIL on it: codex_1's re-run must return a verdict first, because a measurement
taken with an unreviewed instrument is worth nothing. The prevalence card's NARRATE disjunct is
**answered NO against my own convenience**: one agent, mid-maturation, wrong lineage for a card whose
question names resident `6561795`. Host reach remains its only block.

**Not done, and not attempted:** no grading of dancing, blocking or idleness, no prevalence number,
no cure claim, no Arena action, no fetch, no submission, no edit to `cgauto/submissions/`.

**Published:** 2 — decoder handoff `20260823T104109Z` (6 artifact paths at `agent/claude_1@b62e5ec2`,
ACKing the charter) and standing cards `20260823T104232Z`.

## WAKE #65 (2026-08-23T06:14Z) — the champion want census: `want_third_square = 0 of 989`, and the 100% that supports it is STRUCTURAL

**Inbound (3):** codex_1's rev-3 G-1 **ack** (accepts the negative; their rev-4 construction ruling
withheld pending scope); codex_1's `20260823T060529Z`, which arrived mid-wake and accepts the same
ruling, discharging that reserved construction ruling and recording the census as mine; and
`local_claude_1`'s **policy** `20260823T055832Z` — the scope call, and
it went the other way from the one we were waiting for: **`Target::None` may NOT be read as
permission to displace, PEEK rev 4 as proposed is not chartered.** My `DEFERRED: PEEK rev 4` card is
**closed by the ruling, not carried**; nothing was built toward it.

**The card in that policy is delivered.** Re-ran the coordinator's cure-C benching-set
classification on the **champion** (`547fa706…`) over the **frozen 989 peek encounters**, 989/989
joined, 19 of 34 fixtures: **169 `NO_WANT`, 497 `WANT_NOT_A_MOVE` (stay and chop), 323
`WANT_MOVE_ELSEWHERE` — all 323 to the mover's own destination — and `want_third_square` = 0.**
820 of 989 (83%) carried a real want and not one wanted the square displacement could serve. The
coordinator's shape reproduces on the champion, on a case set that is not the benching set, from an
instrument they did not use. **On this evidence the ruling stands.**

**Two facts the card did not ask for.** The `WAIT` is the **selector's**, not the resolver's — **0
of 989 manufactured downstream**, so the intention is destroyed at exactly one site, which is the
premise the Phase 3b design rests on and it now has champion evidence under it. And **29 of the 989
partners were never benched** — issued `CHOP`, mid-work, 26 getting the candidate they wanted most;
those are rev 3's 29 `target-is-the-landing` declines with intent attached.

**I argued against my own headline and it cost a number.** "All 323 to the mover's destination" is
the analogue of the coordinator's 235/235. A permutation control re-scored each `MOVE` want against
the **next** encounter's mover target in the same fixture: **320/320 versus 320/320 — identical.**
Every fixture producing `MOVE` wants has exactly one distinct mover target, so the equality holds
for any pairing. `want_dest == mover_target` **carries no information on this case set** and I
withdrew it as evidence; I suggested the same control on the coordinator's 235. What survives is
the **zero**, which is not a rate and needs no pairing.

**Gates, six, fail-closed.** Champion digest; probe anchors **imported verbatim** from Phase-1
`picker1/make_picker_probe.py` (their instrument on a new subject, not a re-implementation);
probe parity ×34; **champion stream == rev-3 stream ×34** (the join licence, re-run per fixture and
a refusal if it differs); turn-block coverage; join totality 989/989; and **anti-inertness first**,
because rev 3 failed on exactly that gate — 6 constructed classifier cases reaching all four labels,
9,061 `MOVE` candidates offered corpus-wide.

**Not done:** no rev 4, no predicate, no G-2/G-3, no Arena, **no candidate edit** —
`cgauto/submissions/` untouched. **D-1 (the replay→`Trace` adapter design) slipped** and the card
says why: a live coordinator card in the wake set outranks a self-issued queue item. It stays first
on the next wake.

**My own card message was INERT and I caught it after publishing.** In `20260823T061411Z` I wrapped
every `DEFERRED:` marker in bold; `inbox_sweep.is_deferral_card` matches `^DEFERRED:` at line start,
so none matched and four postponed jobs sat authoritative, unacked and self-addressed on `origin`
while being **absent from my own actionable set** — the exact failure the 2026-08-18 deferral rule
was adopted to end. `lint_outbox` could not catch it: it is guarded by the same regex, so a body
with no markers has no shape to check and lints clean — a guard that cannot fire, not one that
passed. Found by checking the sweep after publishing instead of trusting the clean lint; the message
was immutable by then, so it is repaired by correction `20260823T061801Z`, verified to match the
sweep's own regex 5 times. **Standing rule adopted: the `DEFERRED:` marker starts the line, always —
no bold, no backticks, no bullet.**

**Published:** 3 — champion want-census handoff `20260823T061228Z` (6 artifact paths at
`agent/claude_1@c85ee672`), standing-cards re-issue `20260823T061411Z`, deferral-shape correction
`20260823T061801Z`.

## WAKE #64 (2026-08-22T20:03Z) — PEEK rev 3 built to the ruled predicate, and it is INERT

**Inbound (2):** codex_1's step-0b/blocker ack and their **step-2 scope ruling** — BRANCH 1, the
fail-closed predicate stands, rev 3 scoped to the 13 residual re-swaps, busy-blocker
swap-and-return preserved as their DEFERRED card (not mine, not duplicated). Acked at
`20260822T195144Z`.

**Steps 3 and 4 delivered, and the answer is negative.** `make_swap_candidate.py --rev3` builds
the predicate exactly as ruled — tick-local `BTreeMap<i32,Target>` filled by the same `select`
pass, borrowed by the resolver, dropped at the end of `commands()`; all three pre-existing seam
entry points keep their signatures and pass `None`. **G-1 FAILS on the anti-inertness gate: 0
fires over 12,981 unit-turns, 34/34 fixtures byte-identical to the base.** The zero re-swaps are
**vacuous** and I reported them as such.

**Why, measured on 989 partner encounters (probe row per encounter, fired or not):** 0 admitted,
in two classes and no others — **960** because the partner's target is `Target::None`
(**`Self::wait()` sets `target:Target::None`, so a `WAIT` partner carries no target at all** —
that is exactly the path rev 2 fired on, so the fail-closed clause does not narrow rev 2's set,
it annihilates it), and **29** because the partner's target IS the landing (OSC-005 t8..16
`Tree((8,2))`, OSC-027 t4..22 `Tree((3,2))`, `CHOP` every time — the same 5+10 the decline census
found, from an independent instrument). The one admitting shape — a unit whose `MOVE` the seam
rewrote to `WAIT` while it still carries a distant target — occurred **0 times in 34 fixtures**.

**The predicate is live, so "zero" means what it says.** A second constructed-board driver
supplies the map with a base twin that ignores it: **7/7**, the fire board going base `WAIT;WAIT`
→ rev 3 `MOVE 0 1 0;MOVE 2 0 0`, and all five refusal shapes plus arrive-and-stay byte-identical.
The no-map control is identical on all 11 older boards including the four rev-1 fire twins.

**Builder guards, rev-3 form.** "Nothing changed outside the seam region" cannot hold for PEEK, so
it became **"exactly the declared lines changed"** (+14/-4, re-derived from the bytes) plus a
**reverse-apply** that must return the rev-1 candidate byte for byte — which also covers the seam
region, where the diff guard is blind. Both print `verified` on the delivered build.

**Not done, deliberately:** no rev 4, no predicate tuning, no G-2, no G-3, no Arena. The open
question is one clause and it is a ruling, not a build: **`Target::None` on a `WAIT` partner is
"no intent", which is not "intent unknown or stale"**, and the ruled predicate identifies them.
`DEFERRED: PEEK rev 4 — WAIT-partner disposition`, UNBLOCK-SIGNAL a written construction ruling
from codex_1.

**Published:** 2 — scope-ruling ack `20260822T195144Z`, rev-3 G-1 handoff `20260822T200321Z`
(13 artifact paths at `agent/claude_1@bf8127f4`).

## WAKE #63 (2026-08-22T19:41Z) — PEEK step 0 delivered, then REVERSED by step 0b; my step-0 negative rested on the wrong fixture pack

**Inbound (12 new + 2 that arrived mid-wake):** four coordinator acks clearing old debt
(corpus-prevalence 28 paths, alpha-progress-regrade, swap-r1-cure, anti-benching); chatgpt_1's
gateway handoff/correction/ack and revival handoff/ack; the coordinator's gateway ack (backlogged,
not chartered — no role assigned to me) and revival reply; **two PEEK policies**; and codex_1's
**G-f ACCEPTED** on Phase 3b r2 with `DEFERRED: Phase 3b build, UNBLOCK-SIGNAL: written build
authorization from local_claude_1` — carried, not started.

**PEEK step 0 (delivered 19:31:37Z) and its retraction (19:40:58Z).** I answered the card, then
the coordinator's own step 0 crossed with mine; we independently agreed the fire table logs fires
and never declines and so cannot answer the question. They chartered the decline census. I built
it and it **reversed my own delivery**:

- **The seam SEES the collision inside both episodes and declines every time.** OSC-005: 5
  in-window declines (t8,10,12,14,16) plus 2 early-exit rows at t18. OSC-027: 10 (t4,6,…,22).
  **All fifteen decline for one reason: partner is not `WAIT` and a detour existed.** Every other
  gate passes; the shape is a genuine pass-through and BFS strictly decreases across the landing;
  the blocker is `CHOP`ping on every one of those ticks.
- **The integrator's standing doubt is REFUTED on the mechanism** — rev 1 does not merely fail to
  fire inside OSC-005's episode, it declines there, at the clause a widening changes. PEEK is not
  confined to the 13.
- **The cause of my error, recorded: I read the wrong fixture pack.** The tooling loads
  `…/oscillation-library-98628e98/library/` (pinned to `submitted-agent6593838-readable-no-orchard`,
  `fixture_harness.py:76`); I read `…/oscillation-library/`, a different bot on different maps with
  the same fixture ids. My OSC-005 was m065 with a `WAIT` blocker; the real one is m070 with a
  `CHOP` blocker. **"The partner-state relaxation is ruled out" was exactly backwards**, and the
  episode-bounds "correction" I sent the coordinator was itself the error — their 7–18 was right.
  This is *a figure changing meaning at a boundary*, and the boundary was a directory name that
  differs from the pinned one only by a digest suffix. **Check the pinned path, not the plausible
  one.**

**Built (probe only, as chartered):** two `eprintln!` census rows via `patch_probe`;
`candidate-swap-r1.rs` re-emits sha256 `bbbb75d3…` unchanged, both controls unchanged, only the
probe differs; probe parity re-proven per fixture before any row was read, six of six. No candidate
edit, no predicate, no target map, and the mover-side pass-through test deliberately not bundled in.
Two sites, because a census at the partner block alone would silently miss collisions with an own
unit that is itself moving (they take the seam's early `continue`).

**Flagged for codex_1's step 2:** PEEK's two halves point in opposite directions on these rows —
the blocker is chopping the tree it stands on, so its planner target is plausibly its own cell, and
the sketched refusal rule would veto the very displacement the owner's swap-and-return wants.
Reasoning about intent, not measurement; no target map exists.

**Published:** 6 messages — PEEK ack, step-0 handoff, PEEK-policy-2 ack + card claim, anti-benching
ack, and the step-0b **correction** superseding the step-0 handoff and its ack. Artifacts at
`agent/claude_1@8f8cee7a`. Standing: Phase 3b build (awaiting written authorization),
corpus-prevalence resolved by the coordinator's ruling — the block is gone and the card is closed
on their measurement, not mine.

## WAKE #37 (2026-08-21T13:18Z) — queue drained and pushed; three cards standing, all blocked

Inbound: codex_1's `20260821T131344Z` ack only — no authorization, no ruling, verdict unchanged at
`PACKAGE_REPRODUCED; BLOCKED AT G-1`. They re-issued their own two deferrals self-addressed, the
same correction I made at wake #36. Outbound: `20260821T131800Z`, one self-addressed replacement
naming BOTH predecessors in `ack_for` and carrying all three cards (corpus-prevalence,
swap-r1-cure G-2->G-3->G-4, anti-benching Phase 3b). Block re-measured, byte-identical for the
fifth wake: `check_external_storage.py --intent read` FAIL exit 2, `data/processed/games.jsonl` and
`data/processed/trajectories/` absent. Post-publish sweep: 0 new, 1 outstanding — my own fresh card,
which is the correct steady state. Nothing built, nothing widened, no G-3.

**Late in the wake (19:41–19:45Z):** codex_1 ruled step 2 — tick-local `BTreeMap<i32,Target>`
inside one `commands()` call, never stored, missing/`None` fails toward not displacing, mover clause
separately measured; `DEFERRED: rev-3 build`. Their step-0 ack cites my **retracted** step-0
handoff (they fetched before the correction landed) — the OSC-027 t24 site it covers is void.
**I then raised a BLOCKER before building:** `chop_candidates` gives a unit standing on the tree it
chops `target = Target::Tree(its own cell)`, and both blockers stand on a tree **on the landing
cell** (OSC-005 LEMON (8,2); OSC-027 APPLE (3,2)) — so the ruled predicate's "partner target ≠ the
landing cell" clause **fails on all 15 rows**. Rev 3 as ruled reaches OSC-011's 13 and none of
R-1's busy-blocker half. Two branches offered (scope PEEK to the 13, or narrow the second clause);
not mine to choose. **DEFERRED: rev-3 build. UNBLOCK-SIGNAL: a ruling on branch 1 or 2 from codex_1
with local_claude_1 on scope.** Artifact `claude_1/peek/step2-predicate-vetoes-the-15-2026-08-22.md`
at `agent/claude_1@844bdc4e`. Nine messages published this wake; queue drained and pushed.

## READ THIS FIRST — what is WITHDRAWN (2026-08-17)

**Everything I published about the parked troll's CAUSE is withdrawn. Standing causal state: ZERO
established causes.** If you are resuming, do not act on any of it:

- **`GENERATOR_GAP` on OSC-001 / OSC-012 / OSC-031 — WITHDRAWN.** Three separate defects, each
  found after I published: (a) my audit runner omitted `referee.grow()`, so every measurement came
  from a world where **no plant ever ripened**; (b) my work-oracle counted *geometric reachability*
  as work, ignoring capability — **OSC-012's parked unit has `harvest=0, chop=0`**, so the planner
  offering it nothing was **correct**; (c) my runner replaced the shared runner's fail-closed error
  on early stdout closure with a fail-open `break`.
- **The "3 of 3" and "2 of 2" counts — WITHDRAWN** with the labels they carried.
- **`local_claude_1`'s dance-is-innocent result — WITHDRAWN to hypothesis** by its author (pool #4
  v2), and **my approving repetition of it is withdrawn with it**. It is *consistent with* T-1's
  1-of-25 and the ≈ +0.045 pre-registration; it is **demonstrated by nothing yet**.
- **`1.41` corpus points never travels without both its IFs** (audit shows the freezes fixable AND
  the owner judges those games winnable).

**What stands:** T-1's measured results (separate instrument, world-evolution verified `c673dd37`)
— stage 2 and 3 both **0 FIXED / 34**, stage 4 swap **2 FIXED / 34**, graded by the integrator as
**1 of the 25 predicted**. Panel: **0 de-novo oscillation**, D-1 **12.50%** vs a **matched floor
14.58%** I measured rather than inherited. Gates: 2, 3 (warm p95 **0.04 ms**), 4 (parity identical)
**MET**; gate 1 **partially met** — `half_swap` guard unvalidated because whole-game perturbation
cannot hold the trajectory fixed.

## Current position (2026-08-21T11:25:00Z) — WAKE #31: the champion has its own fixtures

Queue drained and pushed. Four new messages: three owner-approved cards/amendments from the
coordinator and one receipt. **The champion-subject library is DELIVERED**
(`20260821T112200Z`, commit `5f057e9d`), which is the ack of its card; the gate amendment is
acked at `20260821T110800Z`; `20260821-corpus-prevalence` is acked and **DEFERRED with its
replacement card** at `20260821T110900Z`, exactly where the coordinator's priority order puts it.

**`claude_1/banana-restoration-r2/oscillation-library-547fa706/` — 21 situations from 28
episodes**, `library_sha256` `4d3b3655…`, subject the champion of record `547fa706…` judged
against itself at `run_identity: floor` over a panel config that is a mechanical copy of the
`98628e98` library's (only subject and output paths differ; `panel-config-diff.json` proves it
field by field). The accepted builder is imported unmodified and its digest is checked before
anything is harvested. **Episode identity is recorded per case** and verified the hard way:
`verify_identity.py` recompiles the champion, rebuilds each game from its own provenance and puts
the run through the shared gate — **21/21 reproduce, 0 failures**. The accepted M3a suite,
retargeted, is 24/24 with `OSC_LIB_REPLAY=1`.

**8/8 controls, and one of them found something.** The old library's `panel-config.json` on disk
hashes `49bb3551…`, not the `eca5cb32…` recorded inside all 34 frozen situations: the
source-portability repair of 2026-08-12 (`07cb2bd7`) edited a file the library had already
pinned, **after** its acceptance. Benign and measured to be so — every window, board, command
line, classification and histogram rebuilds identically, and restoring the frozen digest
reproduces all 34 `content_sha256` exactly. The library's own pin is what made that a paragraph
instead of a week.

**The carry-over table's headline: benching is still the champion's most common recorded shape —
15 of 21 cases, 1,751 benched unit-turns** under the accepted eligible-action oracle, worst case
new `OSC-021` at 380. "Same tree wanted → reservation" has **no exhibit**, which is written as no
exhibit and never as fixed. Case numbers do not carry across libraries (old 013 → new 011, old
017 → new 010, old 012 → new 009); 17 old cases have no champion case on their game.

**One tooling change, flagged**: `build_viewer.py` gained two optional, default-preserving
parameters, because its subject line was the hard-coded string `readable__no_orchard` and
champion pages would otherwise have lied about whose episodes they show. Self-test green, old
tree still builds; codex_1 may have it reverted in favour of a separate generator.

**Also published**: an update answering the narrowed OSC-032/033 stamp's closing question —
`m091 s0` and `m087 s0` produce **no** champion case, and that is *no exhibit*, partly a
consequence of those games ending at 82 and 13, not evidence about the planner.

**Owed / next**: α stays BLOCKED on codex_1's G-1 remedy ruling (yield-only predicate; OSC-011
needs an owner-approved seam widening). Then `20260821-corpus-prevalence`, then anti-benching
Phase 3a. Two self-addressed deferral cards are live and discharge by doing the work.

## Previous position (2026-08-21T10:33:00Z) — WAKE #29: cure α is BUILT, and its own re-swap gate blocks it

codex_1 ACCEPTED G-0 rev 2 (`20260821T101241Z`, `requires_ack: false`) — build authorised. Built
`cgauto/submissions/candidate-swap-r1.rs` from the champion of record `547fa706…`, every edit
confined to the seam by a builder that refuses to write otherwise.

**G-1 outcome: five gates PASS, the sixth FAILS and it is the one ruling 4 put here.** 111
repeated unordered swap pairs within 4 ticks — OSC-006 swaps the pair {0,2} on 27 consecutive
ticks (6.75 % of that fixture's unit-turns), OSC-011 on 6. α cured the dance by creating a new
one. Per §8.1 I did not damp it with an invented cooldown: G-1 is declared BLOCKED, three remedies
are named, a progress conjunct is recommended, and the ruling is codex_1's.

What passed, and is worth reusing: inertness is measured by a **shadow** — the base's own seam
function lifted verbatim into the probe and run every tick on a clone of the same input state, so
"non-firing ticks are byte-identical" is measured on all 6,800 ticks and not just before the first
divergence. 11/11 constructed controls, each with a decline/fire twin. 52 fires over 12,981
unit-turns = 0.401 %; T4(a) yield fires 25, of which **24 had a detour available** — the breadth
figure ruling 1 required. α disabled itself on 0 ticks.

Two secondary findings bound G-2: **OSC-027 never fires** (its recorded stall does not reproduce
under the base — the re-run problem I measured at wake #27), and the card's "back on the tree
within 2 ticks" is **untested**, since all 27 work-displacing fires are inside OSC-006's dance.

Handoff `20260821T103200Z`, requires_ack. **DEFERRED card in force:** G-1 rev 2 (the remedy), then
G-2..G-4, blocked on codex_1's ruling on which remedy α gets.

## Previous position (2026-08-21T07:18:00Z) — WAKE #21: the drift ack landed; my own "merge main" turned out not to be a merge

One message in the queue and it owed nothing: codex_1's ack at `20260821T070937Z` of my
forward-drift question — `requires_ack: false`, the ruling explicitly left with `local_claude_1`
as integrator, and no replacement card due from either side. Queue drained, marked, 0 new and 0
unacknowledged on the confirming sweep.

**The real find of this wake is in my own history.** Last wake's `b08b089a "merge main"` has a
SINGLE parent. It carried main's content into the tree but never recorded `origin/main` as a
parent, so ancestry still said main was unmerged: `git merge-base --is-ancestor origin/main HEAD`
returned false and main commits back to `3e313711` still listed as absent from HEAD while the
files themselves matched. A content-merge that does not record its parent leaves the branch
looking permanently behind — and I would have re-fought the same five conflicts every wake.

Repaired at `5271640c`, a true merge with parents `1cfaad56` and `ac8ad8ab`. Same five conflicts,
all resolved to this branch, but the reason was re-derived per file instead of carried over from
last wake: no function in main's `scripts/inbox_sweep.py` is missing here, and main's
cc/to-recipient ack-narrowing text is present verbatim (offset by one line), so main is carrying
the older text on every one. Green after the merge: inbox_sweep 82/82 + lint_outbox 45/45 =
127/127, sentinel 18/18.

**This does not silence TOOL DRIFT, and should not.** `tool_drift()` SHA-256s the running
`scripts/inbox_sweep.py` against the `origin/main` blob byte-for-byte — no notion of direction.
Accepted card-2 tooling exists only on `agent/claude_1`, so the warning stays lit until main takes
it. The ancestry repair fixes a second and separate confusion, not this one. Published as an
`update` to `local_claude_1` at `20260821T071655Z` with one bearing on their ruling: a merge from
this branch to main is now an ordinary merge with a recorded base, so landing card-2 tooling on
main is cheaper than it looked. I took no integration action.

**Owed: nothing.** No live cards, nothing deferred, my question to `local_claude_1` remains theirs
to answer.

## Previous position (2026-08-21T07:06:00Z) — WAKE #20: G-3 ACCEPTED and closed; `main` merged; the drift check is firing FORWARD

**Queue drained. Zero unseen, zero unacknowledged, zero live cards.** One new message this
wake — codex_1's **G-3 ACCEPTED** (`20260821T065537Z`), `requires_ack: false`. They read all
six pinned artifacts and independently re-ran the three reproduction commands in a detached
worktree at `50fa5a8e`: both fixtures 200/200 routed turns, recorded windows entirely through
`main:IDLE_REGEN_FALLBACK` (110/110 and 143/143), no real candidate formed or discarded, the
post-turn-100 false conjunct left explicitly unmeasured as ruled. **My G-3 replacement card is
discharged by the acknowledged delivery. The OSC-032/033 charter is complete on both sides;
codex_1 states their queue for it is closed.** Bug-versus-correct-caution remains the owner's.

**The sweep opened with a TOOL DRIFT warning and I did not trust it.** I extracted `scripts/`
from `origin/main` into a scratch directory and ran BOTH tools over the same refs: identical
queue (1 new, 0 ack-required). Only then did I read the message.

**Then I merged `origin/main` (`b08b089a`) — and the warning still fires, because the drift is
FORWARD, not stale.** `tool_drift()` is a byte comparison against
`origin/main:scripts/inbox_sweep.py` and is direction-blind. Main's top-level definitions are a
strict SUBSET of this branch's (`SweepState`, `SweepFailure`, `actionable_set`,
`is_deferral_card` are here and absent there; `ack_obliged_to_me`, main's 2026-08-20 narrowing,
is in both). What main has not taken is card 2 — the blocking sentinel and the `actionable_set()`
extraction — **ACCEPTED at `8c531096` and still sitting only on `agent/claude_1`.**

The merge had five conflicts and **every one was main carrying the OLDER text of work repaired
here afterwards**, including `claude_1/night-tree/*`, where main still reads the moving
`origin/main` for its pre-patch control while this branch pins blob `92264bea` — the repair
codex_1's own review required. All resolved to this branch. Suites from the merged tree:
`test_inbox_sweep` + `test_lint_outbox` **127/127**, `test_sentinel` **18/18**.

**Question published to the integrator** (`20260821T070500Z`, ack required): an alarm an agent
cannot clear is an alarm everyone learns to scroll past — which is the exact failure this check
exists to prevent, arriving through the front door. Either main takes the accepted tooling, or
the comparison baseline is ruled to be something other than main. **I did not touch my own
instrument on my own say-so**, and I am not blocked either way.

## Previous position (2026-08-21T06:53:00Z) — WAKE #19: G-3 DELIVERED; the OSC-032/033 charter is complete and my queue is EMPTY

**Queue drained and pushed at `6e322618`. Zero unseen, zero unacknowledged, zero live cards —
the first wake in this task that ends with nothing of mine outstanding.**

One new message: codex_1's **`ACCEPTED_FOR_G3`** on the revised G-1/G-2 package
(`20260821T064156Z`). They re-ran all five reproduction commands in a detached worktree and
confirmed the two subject-local early anchors repair the coverage gap without touching the five
Phase-3 anchors or weakening the per-fixture gate. G-3 resumed **on that acceptance, not before
it**, which is what the card said it would do.

**G-3 delivered at `50fa5a8e`, handed off at `20260821T065107Z`.** Charter gates G-1, G-2, G-3
are now all delivered.

- **New code is one file, and it is a reporter, not an instrument.**
  `claude_1/nogoal/route_table.py` adds **no tap and no gate** — it re-runs parity and
  one-route-per-turn and refuses to print if either fails — and emits the row the charter's G-3
  names but the census does not carry: **one row per unit per turn, all 200 turns of both full
  games**, plus contiguous spans. Kept **out of** `no_goal_census.py` deliberately: that file is
  the artifact codex_1 reviewed, and **a later gate must not edit an accepted instrument to
  produce its own deliverable** — the same rule that kept the champion subject opt-in rather
  than rewriting task `20260820`'s manifest.
- **The finding.** `main:IDLE_REGEN_FALLBACK` on **110/110** and **143/143** window turns, with
  `carried=0 free_cap=2 safe_regen=true idle_regen=true` and
  `idle_harvest=0 bank=0 chops=0 n=1 discarded=1 discarded_real=0` identical on every one of
  them. **Nothing real was formed, so nothing real was discarded** — the one thing thrown away
  each turn is the seeded `WAIT` the fallback had just created. **Phase 3's finding does not
  carry across**: on OSC-013 that same fallback discarded two real `PICK` candidates on 101 of
  170 idle turns. Same route, different event, exactly as the charter warned not to assume.
- **Two facts the per-turn table produced that the histogram could not.**
  1. **OSC-032's stall onset matches its recorded window exactly** — works through turn 90
     (`main:FULL_BANK`, banks a full load), idle from 91, the window's first turn.
  2. **OSC-033's does not.** On the champion that unit stops at **turn 21**, 37 turns before its
     recorded window opens, and its first 14 idle turns come back through a **second** route,
     `early:EARLY_CHOP_FALLBACK` with `chops=0 n=1`, until the `early` branch ends after turn 34.
     Its idle run here is **180** turns, of which the recorded 143 are the tail. The recorded
     window came from an older bot; **no conclusion drawn from the difference**. This is only
     visible because the early anchors exist — the pre-revision probe could not have seen it.
- **The not-claimed statement is explicit and it held.** No bug named; lone-`WAIT`-when-nothing-
  applies may be correct caution or a defect and that is the **owner's** ruling.
  **Which conjunct of the `view.turn>=100` replant block is false stays unmeasured** — the block
  pushed nothing on any turn including both windows' turns 100–200, so the turn guard alone does
  not explain them, but the probe does not tap the conjuncts and `fixture_units_seen` is a
  **proxy**, not the predicate's own count. codex_1 ruled the seven-conjunct probe not required.
  No class-wide claim, no causal claim about why `yamo_chop_candidates` was empty, nothing
  touching P1/P2 or the open extend-versus-replace question.
- **Owner brief in plain words** at `claude_1/nogoal/owner-brief-2026-08-21.md`, readable without
  opening an artifact. Its one line: **somebody did give it a job, and the job was "wait"** — the
  silence is produced in the **generator**, not the selector.
- Both reproduction commands re-run to completion on this tree **before** the message was
  written, not after.

**Lint caught one thing worth remembering:** a handoff whose body said `DEFERRED: none.` failed
`deferral_shape_errors` — the marker is line-start-matched and does not care that the word after
it is "none". Say **`Deferrals: none.`** when you mean nothing is deferred.

**Tooling note, unchanged from #18:** the `TOOL DRIFT` banner is still a false alarm here. I
re-checked it by **marker**, not by date: `main`'s `inbox_sweep.py` blob is exactly the one this
branch synced at `16ec22c9`, and this branch is **ahead** of it via `5ad46cbb` and the ACCEPTED
`8c531096`. Do not act on the banner alone; do not dismiss it either.

**What is not mine now:** the owner's bug-versus-correct-caution ruling on these two cases, any
follow-up they charter from it, and the six held stamps.

## Previous position (2026-08-21T06:35:00Z) — WAKE #18: G-1 REVISION_REQUIRED answered; the repair was the probe, not the gate

**Queue drained and pushed at `45d64099`. One live card, mine, by design.**

Two new messages, both `ack` from codex_1, both read. One closed the nine-card backlog thread
with nothing owed. The other is the one that mattered: **`REVISION_REQUIRED` on my card-4 G-1
package**, refusing the shape I gave the both-ways control.

**codex_1 was right and the refusal names a pattern I have written down about myself.** My G-1
could name no non-idle route for OSC-033, and instead of treating that as a defect I rewrote
the charter's gate from *per fixture* to *at least one fixture in the run*. That is
reshape-the-control-until-it-passes, from the agent with "a mechanism that cannot fail is not a
check" in his own error list. The reviewer's line is the one to keep: *fixture-dependent
control flow is the thing being classified*, so OSC-032's non-constancy is not OSC-033's
control, identical binary or not.

**The defect was in the reused probe, and it was one thing.** `commands()` picks its generator
from **five** branches — `committed_regeneration` and `endgame` to `endgame_candidates`,
**`early` to `early_candidates`**, default to `main_candidates`. Phase 3's five anchors tapped
two of those functions. Turns 1–34 of *both* games run the `early` branch.

**I measured the cause instead of inferring it**, because "the structural explanation agrees
with the count" is precisely how I have shipped a right finding for a wrong reason before.
`claude_1/nogoal/unrouted_cause.py` rebuilds the reviewed five-anchor probe (`551da424…`,
digest-verified) and reports the branch flags of every unrouted turn: **34 in each fixture, all
`early=true endgame=false committed=false train_now=false`, no other combination**. One cause,
so two anchors close it — and the script exits non-zero if a second combination ever appears.

Delivered at `a7c57893`, handed off at `20260821T063135Z`:

- Two anchors, `early_candidates/entry` and `early_candidates/tail`, naming `EARLY_CARRY_BANK`,
  `EARLY_CHOP_FALLBACK`, `EARLY_GATHER`. **The five Phase-3 anchors are byte-untouched** and
  still match exactly once each. Applied **per subject** to `door1-champion` only, so task
  `20260820`'s accepted p1p2 probes and manifest are not rewritten — a bare builder run still
  reproduces them byte-identically, checked by running and diffing.
- **Per-fixture both-ways restored as the charter words it**, plus a new full-game coverage
  gate. **200/200 turns named in both fixtures, 0 unrouted.** OSC-033's 20 employed turns —
  the exact 20 the review demanded — are `EARLY_CHOP_FALLBACK` ×12 and `EARLY_CARRY_BANK` ×8.
  An employed-but-unnamed turn now FAILS the run instead of being counted and excused.
- **The gate was watched failing.** `gate_negative_control.py` points the revised census at the
  pre-revision probe and requires a non-zero exit: exit 1, all three failure kinds firing,
  matched on failure **text** so an unrelated crash cannot pass it. Both controls restore every
  artifact they touch and verify the restoration **by digest**, not by trusting a `finally`.
- **The in-window result did not move**: 110/110 and 143/143 `main:IDLE_REGEN_FALLBACK`, same
  predicates, same sub-generator sizes. The repair changed what the instrument can see
  *outside* the windows, not what it saw inside them.

**G-3 is still blocked and still not startable.** `REVISION_REQUIRED` is not an acceptance;
codex_1's requirement 3 says publish the revised package before treating either window's output
as a finding, and publishing is not being accepted. Replacement card at `20260821T063253Z`
discharges the old one and carries G-3 forward. Per G-1 ruling the **seven-conjunct probe is not
required** and the conjunct attribution stays **explicitly unmeasured** — if a G-3 sentence
names a conjunct, that sentence is wrong. Noted: the early anchors added 68 named turns but no
new unit, so `fixture_units_seen` is still 1 and the `count()>=2` proxy is no better than before.

**Tooling note for the next resume.** The sweep printed `TOOL DRIFT: running e5a2b733…, main has
bd0fb63e…`. It is a **false alarm here** — a blob-hash artifact of my own card-2 sentinel work,
which `main` has not merged yet. Do not act on that banner alone and do not dismiss it either:
check it by **marker**, not by date. `16ec22c9` already carried main's launcher and cc-ack
narrowing into this branch; `deferral_shape_errors`, `card_ack_errors`, the cross-task gate and
`ack_obliged_to_me` are all present, and `publish_outbox.sh`/`agent_launcher.py` are
byte-identical to `main`. Transport suite 145/145.

## Earlier position (2026-08-21T06:17:00Z) — WAKE #17: card 2 ACCEPTED, card 4 G-1 delivered, the revealed backlog closed

Launcher woke me on a three-message queue (codex_1's card-2 review plus two acks). Ritual
complete: swept `--fetch`, read every message, published five, `--mark`ed as its own step,
committed and pushed. **Ending state: 0 unseen, 1 unacknowledged — the G-3 card, which is
blocked on a peer by design.**

- **Card 2 is ACCEPTED** (`codex_1/20260821T060749Z`). Their `REVISION_REQUIRED` named two
  blocking findings and both are repaired at **`8c531096`**, delivered at `20260821T060111Z`.
  Suite **138 → 145**; each new test was watched failing against the unrepaired code first.
  - **Self-addressed `DEFERRED:` cards can now wake their owner.** Repaired in the SHARED
    predicate, never in the sentinel: `inbox_sweep.is_deferral_card()` admits a self-authored
    message only with the exact shape the outbox lint already enforces (line-start `DEFERRED:`,
    `requires_ack: true`, own sender in `to`), and `lint_outbox` now imports that marker rather
    than defining a second copy. Ordinary self-mail stays inert, held by a negative control.
    Self-authored mail is also out of `new_items` — an agent has read what it wrote, so one
    `--mark` can no longer retire a job that is still undone.
  - **Pidfile ownership is now an exclusive `flock`**, written in place through the held
    descriptor. The old check-then-write scored **two winners AND a crash** under a 32-process
    barrier (`W E W L L …`): every starter staged through the same `.pid.tmp` name.
  - **Gate 1 remains MIXED.** No rollout, no protocol amendment, no notify activation.
- **The repair's first act was to indict my own reporting.** Turning the route on took my
  unacknowledged count from **0 to 12** — twelve of my own cards, authoritative on origin,
  never discharged, invisible because nothing could see them. Wakes #13 and #14 recorded
  "queue drained" while they were live and the instrument agreed. **That agreement was the
  defect**, the [[troll-farm-instrument-failure-modes]] shape at the transport layer.
- **All twelve are now closed.** Three by the card-2 handoff; the other nine triaged against
  their artifacts at `20260821T061633Z` — for each, the later same-task message that delivers
  what the card deferred, with **eleven pinned commits verified reachable** by
  `git merge-base --is-ancestor`, not by recollection.
  - **The pair-selector card is the rule caught live:** its Phase-1 delivery
    (`20260820T143805Z`) named the card in **`supersedes`**, not `ack_for`. The work shipped
    and was reviewed; the card stayed open, because `supersedes` is inert and only `ack_for`
    discharges. I have that sentence in my own memory and still published it that way.
- **Card 4 (OSC-032/033 no-goal instrument): G-1 DELIVERED** at **`c0bdb4d6`**, handoff
  `20260821T061245Z`. Not deferred a second time.
  - **The Phase-3 probes were reused unmodified** — all five `make_route_probe.py` anchors match
    the champion `547fa706…` exactly once. I added a subject, a `--subject`/`--manifest` CLI,
    and the controls. A bare run still reproduces task 20260820's manifest byte-identically;
    my first version rewrote it and that is reverted.
  - **Measured, pending G-1, NOT a finding:** both fixtures take `main:IDLE_REGEN_FALLBACK` on
    **110/110** and **143/143** window turns, with identical predicates every turn
    (`carried=0 free_cap=2 safe_regen=true idle_regen=true`) and identical sub-generator sizes
    (`idle_harvest=0 bank=0 chops=0 n=1 discarded=1 discarded_real=0`).
  - **Phase 3's OSC-013 result does NOT carry across.** There the same fallback discarded two
    real `PICK`s on 101 of 170 turns; here `discarded_real=0` everywhere — nothing real was
    formed, so nothing was thrown away. The charter warned against carrying it as a premise.
  - **The both-ways gate had to change shape and this is the reviewer's to weigh.** OSC-033
    can NAME no non-idle route (its 20 employed turns outside the window all take a path the
    five anchors do not name), so the gate is now instrument-level with per-fixture recording.
    **OSC-033 carries no in-fixture both-ways evidence.**
  - **I published a wrong version of that internally first** — "OSC-033 is idle on all 200
    turns". It is not; the artifact's own `outside_window_unrouted_employed_turns: 20` caught
    me, and the note records the correction rather than the tidy version.
  - **Not measured and not inferred:** which conjunct of the `view.turn>=100` replant block is
    false. It pushed nothing on any turn *including 100–200*, so the turn guard alone does not
    explain these windows. There is a suggestive one-unit observation and it stays an
    observation — proxy-for-the-thing is an error I have published before.
- **Open rule question for the owner, unanswered:** should a green sweep include ALL open
  commitments or only the newest card per task? The repair implements the former. I did not
  narrow it to my own preference; a narrower route is a one-line change if they prefer it.
- **DEFERRED cards after this wake: exactly one** — G-3 of the no-goal instrument
  (`20260821T061246Z`), blocked on codex_1's G-1 review of `c0bdb4d6` and correctly not
  startable by me.

## Previous position (2026-08-21T05:12:00Z) — WAKE #15: owner rulings acked; `actionable_set()` extracted and handed off

Launcher woke me on a three-message queue. Ritual complete: swept `--fetch`, read all messages,
published two messages, `--mark`ed as its own step, committed and pushed. Post-mark sweep: **0
unacknowledged-ack-required, 0 delivery errors, 0 immutable collisions**; 12 quarantined, all
pre-existing and adjudicated.

- **The owner ruled twice** (`local_claude_1/20260821T044224Z-...-policy.md`, ack required, acked
  at `20260821T050909Z`). **KEEP** — `547fa706…` (door-1 pure deletion) is the champion of record
  and cure-C `ad3bfefe…` is history. **The KEEP does not claim a gain**: the step is IMMATERIAL,
  +0.220 over n=5, under the 1.0 floor. That clause travels with the number every time I cite it.
  **D3 = HOLD**, no Arena slot for the anti-benching package now or after session 3, because its
  own pre-registered condition ("when its gates are green") is not met.
- **Consequence applied:** the subject of `20260820-pair-selector-anti-benching` is now the
  door-1 base. The dual-base build already covers it, so no rebuild is owed; from here the live
  column is the door-1 one — **named absolute P3 regression on `m004` seat 0, FIXED 8 → 8**. The
  cure-C column is historical context, not an option.
- **Card 3 CLOSED as discharged-by-events, with no replacement.** The coordinator asked me to name
  any residual Phase-1 question rather than assume one. Checked: Phase 3 answered the route and
  Phase 2 answered the cost; what is left is the owner's own design question, carded to the owner.
  So I filed nothing.
- **Card 2 is UNBLOCKED and step 1 is delivered.** The coordinator ruled YES on extracting
  `actionable_set()`. Landed as its own change at **`5ad46cbb`** — `main()` now only parses args,
  fetches and prints; all computation moved into `actionable_set(me, root, tasks, senders)`
  returning a frozen `SweepState`, with `SweepFailure` carrying the four inline `return 2` paths.
  **One predicate, one code path**, so a sentinel cannot disagree with the sweep.
  - Evidence: the full sweep of this repository is **byte-identical** to the pre-refactor script on
    stdout and stderr, except the `TOOL DRIFT` banner — which fires *correctly*. Suite **118 → 123
    green** (`uvx pytest`).
  - **The weakness I disclosed in my own handoff:** a pure `main()`-vs-`actionable_set()` output
    equality assertion **cannot fail by construction** now that `main()` derives from it — the
    "mechanism that cannot fail" shape. What bites is the substantive assertions beside it, which I
    verified by two mutants applied **alone** to a clean tree (dropping `ack_obliged_to_me` → 2
    failures; ignoring the seen-state → 1 failure). Nothing in the change *forces* a future
    sentinel through that door; only review does, which is what I asked codex_1 to attack.
  - Handed off at `20260821T050910Z`, requires_ack, per the ruling's condition 4. **The sentinel is
    not started and nothing is built on top of this until codex_1 answers.**
- **`*** TOOL DRIFT` now fires on my branch and this is EXPECTED**: `scripts/inbox_sweep.py` on
  `agent/claude_1` (`c2437a55…`) intentionally differs from `origin/main` (`bd0fb63e…`) until the
  refactor is reviewed and adopted. It is not the stale-tooling hazard the banner usually means —
  but the banner cannot tell the two apart, so anyone sweeping from my branch should read this line
  before dismissing it. Both tools matched all three refs at the start of this wake.
- **Two messages arrived mid-ritual and were read, not just marked**: codex_1's ack of the same
  rulings (he will review the refactor when published — it now is), and the coordinator's update
  closing the VM disk item he claimed, **95% → 66%, 1.0 G → 6.5 G free**, by reaping 7.1 G of
  `/tmp` agent scratch older than a day, with unpushed work preserved as a bundle first. A
  scratch-reaper is named as future work and explicitly **unclaimed**; I have not taken it.
- **DEFERRED cards after this wake:** card 2 (sentinel build) only — unblocked by the ruling,
  step 1 delivered, now gated on codex_1's review of `5ad46cbb`; still mine, still not urgent.

## Previous position (2026-08-21T00:59:39Z) — WAKE #14: the owner's morning sheet; informational, nothing owed

Launcher woke me on a one-message queue. Ritual complete: swept `--fetch`, read the message,
`--mark`ed as its own step, committed and pushed. Post-mark sweep: **0 new, 0
unacknowledged-ack-required, 0 delivery errors, 0 immutable collisions**; 12 quarantined, all
pre-existing and adjudicated.

- The message was `local_claude_1/20260821T005401Z-20260819-osc031-forecast-fix-door1b-progress.md`
  — `type: progress`, **`to: ["user"]`** with me only on `cc`, **`requires_ack: false`**. It is the
  night-runner's unattended OWNER MORNING SHEET. Nothing is addressed to me and nothing is owed, so
  I published no ack and took no action on its content.
- **What it reports, recorded not endorsed** (no artifact was pinned for me to reproduce, and I ran
  no verification of these numbers): session-2 title fight, Door-1 challenger vs the cure-C
  resident, pairs [1.9, -0.6, 0.4, 1.1, -1.7], mean **+0.220** over n=5 — **IMMATERIAL**, below
  the pre-registered 1.0 materiality floor and the 1.315 winner bar. Composed three-generation
  distance **+1.240** (night 1 **+1.02** plus tonight), carrying its own author's caveat that
  composition chains ACROSS nights and the ladder moved (Legend 160 → 176 seats) between them —
  **evidence, not gold**. Branch taken: **SESSION3**, the direct Door-1-vs-`98628e98` block, 1 of
  10 marks submitted at the time of writing.
- **KEEP/REVERT is the owner's, and the sheet says so itself.** I assert no verdict on cure C, on
  Door-1, or on the composed number, and the nine named costs travel with any verdict
  (`codex_1/reviews/osc031-named-costs-package-review-2026-08-19.md`).
- **Nothing was postponed this wake, so no new `DEFERRED:` card is owed.** Standing deferrals
  unchanged and still unclaimed by peers: card 2 (sentinel build) blocked on the one
  `actionable_set()` extraction ruling; card 3 (pair-selector Phase 2) blocked behind the OWNER'S
  design gate on P1+P2 and the settled resident.
- **Tool digests re-verified against `origin/main` this wake, and BOTH HAD MOVED under me since
  wake #13** — `inbox_sweep.py` `be8251c4…` → **`7952be44…`**, `lint_outbox.py` `f3c47b70…` →
  **`40b71c4c…`**. Local matches `main` on both. This is the third time the tooling has changed
  beneath a sweep of mine; nothing on screen announces it. Re-check every wake.
- **Seen-state note:** `--mark` recorded **871** selected addressed paths, not one. The seen state
  is exact-path membership now, so a mark covers the whole current selection rather than advancing
  a timestamp — the old "watermark deliberately NOT advanced" hazard does not apply, but the
  count is large and worth reading before assuming a one-message mark.

## Previous position (2026-08-20T21:07:33Z) — WAKE #13: Phase 3 ACKED by codex_1; queue drained, nothing owed

Launcher woke me on a one-message queue. Ritual complete: swept `--fetch`, read the message,
`--mark`ed as its own step, committed and pushed. Post-mark sweep: **0 new, 0
unacknowledged-ack-required, 0 delivery errors, 0 immutable collisions.**

- The message was codex_1's `20260820T210325Z-20260820-pair-selector-anti-benching-phase3-ack.md`,
  `ack_for` my Phase 3 generator handoff, **`requires_ack: false`** — it discharges and owes
  nothing back, so I published no ack-of-an-ack. No artifact accompanied it, so there was nothing
  to reproduce.
- **He reads the Phase 3 measurement the way it is written**, including the correction: every ruled
  idle turn reaches the selector with exactly the seeded `WAIT`; on OSC-013 turns 100–200 the
  generator had also formed two `PICK`s before `main:IDLE_REGEN_FALLBACK` replaced `out`; the other
  ruled idle turns genuinely had no non-`WAIT` work. **Card 1 stays DISCHARGED.**
- **He restates my own scope boundary back to me and I hold it unchanged:** this is a
  generator-route measurement, **not** evidence that preserving the two `PICK`s restores progress,
  and **not** authority to extend P1 or P2. I did not build against the design question and will
  not until the owner rules.
- **He explicitly claims none of the open cards.** So both remain mine and both remain blocked:
  - **DEFERRED — owner design ruling:** may `main_candidates`' `idle_regeneration && chops.is_empty()`
    fallback **extend** `out` instead of replacing it? Bears on 101 of OSC-013's 170 idle turns and
    on **none** of OSC-004 / OSC-017 / OSC-034.
  - **DEFERRED — card 2 (sentinel build):** blocked on the coordinator's single-code-path ruling —
    may `actionable_set()` be extracted into `scripts/inbox_sweep.py` so `main()` and the sentinel
    share ONE code path?
- Unchanged and still open, still unowned: **VM disk** (flagged, not claimed). **No Arena action
  taken or authorized.**

## Previous position (2026-08-20T20:59:00Z) — WAKE #12: Phase 3 DELIVERED, my own card's premise corrected

Launcher woke me on a one-message queue. Ritual complete: swept `--fetch`, read the message,
**delivered rather than deferred**, `--mark`ed as its own step, committed and pushed.

- The message was codex_1's `20260820T204515Z-...-ack.md`, `requires_ack: false` — it discharges
  and owes nothing back, so I published no ack-of-an-ack. Substance: he confirms he does not claim
  or start either of my two deferrals, and receives my concurrence with his unified review.
- **Card 1 was UNBLOCKED and is now DISCHARGED.** `20260820T205740Z-...-phase3-generator-handoff.md`,
  artifacts @ `1c7aed39`. Report: `claude_1/picker2/phase3-generator-route-2026-08-20.md`.
  Replay: `idle_shape.py`, `make_route_probe.py`, `route_census.py`.
- **The card's premise was wrong and I corrected it rather than answering it.** I had written that
  the anchor "is offered no work at all". `main_candidates` and `endgame_candidates` both open
  `let mut out=vec![MoisanBot::wait()]`, so an empty list was never reachable. Measured: on every
  idle turn of all four ruled fixtures, on **both** bases, the list is exactly **one** entry — the
  seed. **Length 1, never 0**, with a cross-check (idle turn holding non-`WAIT` work) that is 0
  everywhere, so this reader and `gate_bench.py` agree on which turns are idle.
- **One route, 100% of those turns:** `main_candidates`' `idle_regeneration && chops.is_empty()`
  fallback (`chops=0 idle_harvest=0 bank=0 carried=0 free_cap=2`). It returns a **fresh**
  `vec![wait()]` rather than extending the `out` it built — and that discard is not harmless.
- **OSC-013's 170 idle turns are TWO phenomena, not one.** Turns 31–99 (69, contiguous): the
  generator had nothing. Turns 100–200 (**101**, contiguous): `out` held **two `PICK` candidates,
  score 7500 / 7499, target Cell((2,1))** and they were thrown away. The split is exactly the
  `view.turn>=100` guard on the safe-regeneration replant block. Identical on the door-1 base.
- **Settles the location: the residual stall is NOT a selector defect.** The selector is handed a
  one-element list and returns the only element. P1/P2 correctly untouched.
- **NOT claimed, deliberately:** that keeping those `PICK`s restores progress (they would have to
  be selected, be legal, and leave the cycle — the last is the grader's bar), or that the discard
  is a defect at all. That is the owner's design question and I did **not** build against it. This
  is the exact step that produced the claims about a generator gap I withdrew on 2026-08-17.
- **Five gates, each fails the run rather than degrading it:** parity for BOTH probes per fixture
  per arm; coverage (one `PS3FINAL` per window turn); **cross-probe agreement** — `PS3FINAL n` at
  `by_id.insert` must equal the selector probe's `PS2CAND` count for the same unit/turn; one route
  row per unit per turn; exact-once anchoring or the build is refused. All passed. The route tap
  is not a constant — employed turns return `main:CHOPS` / `main:FULL_BANK`.
- `run_gates.py` deliberately **unmodified** — codex_1 reproduced the Phase-2 package as it stands.
- Two lint gates fired on my handoff and both were fixed, not bypassed: multi-line `artifact_paths`,
  and the evidence gate catching the withdrawn cause label in my prose. I removed the bare label
  rather than adding a `review_ref` for a claim I was not making. A third caught the pin before the
  artifact commit was pushed — I pushed artifacts first, then pinned.
- **DEFERRED: the owner's design question** — may the `idle_regeneration` fallback extend `out`
  instead of replacing it? Scope stated in the card: it can bear on 101 of OSC-013's 170 idle turns
  and on **none** of OSC-004 / OSC-017 / OSC-034.
- **DEFERRED: card 2 (sentinel build)**, unchanged, still blocked on the one ruling — may
  `actionable_set()` be extracted into `scripts/inbox_sweep.py` so `main()` and the sentinel share
  ONE code path?
- Unchanged and still open: **VM disk** (unowned, flagged not claimed). No Arena action.

## Previous position (2026-08-20T20:30:00Z) — WAKE #11: review received, verdict concurred

Launcher woke me on two codex_1 messages, neither owing me an ack. Ritual complete: swept
`--fetch`, read both plus the review artifact they carry, published, `--mark`ed as its own step,
committed and pushed. Post-mark: **0 unacknowledged-ack-required from peers**, 0 delivery errors,
0 immutable collisions.

- **codex_1's unified review of my Phase-2 dual-base package: `PACKAGE_REPRODUCED; BOTH CANDIDATES
  BLOCKED AS QUALIFIED CURES`** (`codex_1/reviews/pair-selector-phase2-unified-review-2026-08-20.md`,
  handoff addressed to local_claude_1, me on cc). He rebuilt both candidates from a detached
  worktree at `5409ba13` with `run_gates.py --skip-panels` and reproduced every non-panel figure:
  benched → 0 on every fixture red on its own base, FIXED `3 → 4` / `8 → 8`, blocking `53 → 33` /
  `43 → 35`, de-novo/healed `0/20` and `0/8` with the swap control refilling exactly the healed
  keys, 8,160-field process parity. His own single-draw latency rerun also moved the deltas,
  independently corroborating my correction.
- **I concurred; nothing to revise.** Published as `update` to codex_1 — the verdict is the same
  reading my package states: the bench is gone, the situations are mostly not cured.
- **The P3 question I escalated is answered, and answered against me.** I published door-1
  `m004`/seat 0 P3 orchard-dormancy inertness as a reviewer ruling rather than a failure. The
  review rules that the locked panel configuration makes P3 an **absolute** candidate-equals-parent
  invariant that was explicitly kept, so an intentional selector edit does not make it
  inapplicable: **door-1 carries a named absolute regression unless the owner changes the rule.**
  Same for the `m021` P4 / `r5-horizon` addition — a game already blocked for another reason does
  not absorb a new property violation. Settled; I will not re-litigate either.
- **No Arena action taken or authorized.** Both artifacts sit on the shelf for the owner's D3.
- **Both open cards re-published as a self-addressed queue item** (`...-progress.md`,
  `requires_ack: true`) instead of living in this file only: (1) measure why the anchor unit's
  candidate list is empty on the detector-quiet-but-stalled turns (cure-C OSC-013, 170/187 window
  turns) — generator question, and P1/P2 must NOT be extended before it is measured; (2) sentinel
  build, still blocked on the one ruling — may `actionable_set()` be extracted into
  `scripts/inbox_sweep.py` so `main()` and the sentinel share ONE code path?
- Unchanged and still open: **VM disk 95% / ~1.1G free** (unowned, flagged not claimed).
- Stamp fix: my wake-#10 entry cited the latency correction as `20260820T202946Z`; the published
  message is `20260820T202206Z`. Corrected in place below.

## Previous position (2026-08-20T20:20:00Z) — WAKE #10: Phase-2 DUAL-BASE package DELIVERED

Launcher woke me on the owner's phase-two build card (D1 P1+P2, D2 dual-base). Ritual complete:
swept `--fetch`, read every new message, **delivered rather than deferred**, `--mark`ed as its own
step, committed and pushed. Post-mark sweep: **0 unacknowledged-ack-required**, 0 delivery errors,
0 immutable collisions.

- **`20260820-pair-selector-anti-benching` Phase 2 — DELIVERED** at
  `coordination/messages/claude_1/20260820T201729Z-...-phase2-dual-base-handoff.md`, artifacts @
  `5409ba13`. Report: `claude_1/picker2/phase2-package-2026-08-20.md`. Battery replays with one
  command: `python3 claude_1/picker2/run_gates.py` — **19 of 19 steps OK**.
- **The headline is half a success and is stated that way everywhere:** the bench is gone; the
  situations are mostly not cured. Every ruled fixture red on its base goes benched → **0** and
  D-1 falls silent, but on the standing grader (silent AND progress restored) three of four
  cure-C fixtures are **detector-quiet-but-stalled**. All-34: cure-C **3 → 4** FIXED, door-1
  **8 → 8**, nothing regressed.
- **Panel, 240 games vs a floor verified field by field:** cure-C **53 → 33** blocking, door-1
  **43 → 35**; **0 de-novo on both bases**, 20 and 8 healed. The 0 carries a liveness control —
  swap the arms and the de-novo bucket refills with exactly the healed keys (20/20, 8/8).
- **One generator, two subjects:** diff body byte-identical across bases (`af8f710ce50336e3`) and
  the *patched* selection regions byte-identical too. P1 observed firing on every candidate arm.
- **Two of the four ruled fixtures are NOT benched on the door-1 base** (the forecast hunk already
  employs the unit). Redness is measured per base, never inherited — my first draft inherited it
  and would have manufactured two failures.
- **Named, not buried:** `m021`/seat 1 gains property P4 + an `r5-horizon` flag on both bases;
  `m004`/seat 0 trips **P3** orchard-dormancy inertness on the door-1 base only. P3 asserts
  byte-equality with the parent's command stream, which any intentional selector change can reach
  — **that is a ruling for codex_1 and the owner, not mine.**
- **Latency: I published a single-draw delta and then corrected it.** The handoff said +0.0020 ms
  (cure-C) / +0.0616 ms (door-1); rerunning the same command flipped the cure-C sign to −0.0021 ms.
  `latency.py --repeats 5` now measures the **noise floor** — the base arm's OWN p95 varies by
  2.4058 ms (cure-C) and 0.0931 ms (door-1) across identical repeats, so both deltas are inside it.
  Correct statement: **P1's per-pair cost is not resolvable above host noise**; the gate is MET by
  three orders of magnitude, the cost is bounded not measured. Published as a `correction`
  superseding the handoff (`20260820T202206Z`, artifacts @ `14b575ce`). Process-count parity 8160
  field comparisons IDENTICAL. **No Arena action** — the queue slot is the owner's D3.
- Also drained, no reply owed (`requires_ack: false`): codex_1's build-card ack carrying his
  DEFERRED unified-review card (now satisfied by my handoff), and local_claude_1's Phase-1
  handoff ack closing a one-second transport gap.
- **DEFERRED: why progress is not restored on the three detector-quiet-but-stalled fixtures.**
  P1+P2 removes the pair that benched the unit; on cure-C OSC-013 the unit is then offered no work
  at all on 170 of 187 window turns, which is a generator question, not a selector question, and
  it is a separate phase. Replacement card: measure, on the P1+P2 candidate, why the anchor unit's
  candidate list is empty on those turns — do NOT extend P1/P2 to cover it before that is known.
- **Card 2 (sentinel build) remains DEFERRED**, unchanged, still blocked on the single ruling: may
  `actionable_set()` be extracted into `scripts/inbox_sweep.py` so `main()` and the sentinel share
  ONE code path.
- Unchanged and still open: **VM disk 95% / ~1.1G free** (unowned, flagged not claimed).

## Earlier position (2026-08-20T19:42:13Z) — WAKE #9: clean drain, nothing owed

Launcher woke me on a one-message queue. Ritual complete: swept `--fetch`, read the single new
message, judged no reply owed, `--mark`ed as its own step, committed and pushed. Sweep after
marking: **0 new / 0 unacknowledged-ack-required / 0 delivery errors / 0 immutable collisions**.

- The message was `local_claude_1/20260820T193728Z-20260820-evening-integration-ack.md` —
  `type: ack`, `requires_ack: false`, `ack_for` naming nine paths including six of mine (the
  launcher-permissions ack, the unattended-drain handoff, the codex-lane-live ack, the Phase-1
  handoff, and both door1b night-tree handoffs). Under the transport rules an ack with
  `requires_ack: false` discharges and owes nothing back; publishing an ack-of-an-ack would be
  transport noise, so I published none. This is an ordinary green wake by the standing rule that
  wake quality is judged by drained queues, not wake counts.
- Substance carried by the ack, recorded not acted on: the **Phase-1 mechanism note is WITH THE
  OWNER** as the design-gate item (P1+P2 recommended; the 235 non-deadlock turns honestly out of
  scope). The **night tree stands implemented** with codex_1's moving-baseline catch repaired
  (pre-patch control pinned to blob `92264bea` rather than the moving `origin/main`), and the
  morning sheet is on schedule. **No integrator objections anywhere.** Next gate in the benching
  lane is the owner's design ruling — not mine to force.
- **Nothing postponed this wake, so no new DEFERRED card.** Card 2 (sentinel build) remains
  DEFERRED on its published replacement, still blocked on the single ruling: may `actionable_set()`
  be extracted into `scripts/inbox_sweep.py` so `main()` and the sentinel share ONE code path.
- Unchanged and still open: **VM disk 98% / 541M free** (unowned, flagged not claimed).

## Previous position (2026-08-20T14:39:36Z) — WAKE #5: Phase 1 DELIVERED, design gate is the owner's

Launcher woke me on the owner's unblock card. Ritual complete: swept `--fetch`, read both new
messages (the unblock policy and codex_1's support ack), **delivered rather than deferred**,
`--mark`ed as its own step, committed and pushed. Sweep is 0 new / 0 unacked / 0 delivery errors.

- **`20260820-pair-selector-anti-benching` Phase 1 — DELIVERED** at
  `coordination/messages/claude_1/20260820T143805Z-...-phase1-handoff.md`, artifacts @ `8cacaa08`.
  Note: `claude_1/picker1/mechanism-note-2026-08-20.md`.
  - Step 0 measured: the selection region is byte-identical in both night arms; the one 8-line
    hunk is in `predicted_opp_chop`, which feeds candidate SCORES — so the mechanism is
    arm-independent, the arithmetic is pinned to cure-C `ad3bfefe`. Said explicitly, not assumed.
  - Measured on all **24** GOAL_SPLIT_WRONG situations (charter required 4), 2245 benched turns:
    **2245/2245 blocked at the winner by `compatible()`** (same target cell), zero by
    `stock_compatible`; **1435 score preference** (partner term dominates 1435/1435) vs **810
    ties broken by enumeration order** (lower-id unit benched, 10/10 tie cases); **2010/2245**
    (4/4 owner-ruled) the preferred partner command is a MOVE onto the benched troll's own cell,
    which the same pair makes impossible by ordering the occupant to WAIT.
  - **The margin<=0 guard fired and I was wrong**: ties are reachable because `score >
    best_score` is strict. Recorded in the note; it produced finding 2.
  - **Design proposal P1+P2 is on the OWNER's desk.** Two-doors wall: nothing is built until the
    owner rules. Phase 2 stays named-costs class on whatever resident tonight settles.
- **Card 2 (sentinel build) remains DEFERRED** on its published replacement
  (`20260820T094549Z` route is now discharged; the sentinel deferral stands) — still blocked on
  the one ruling: may `actionable_set()` be extracted into `scripts/inbox_sweep.py` so `main()`
  and the sentinel share ONE code path. Unchanged by this session; nothing new postponed here.

## Previous position (2026-08-20, 13:50Z) — WAKE TEST #3 PASSED; hand-starts are over

**This block was written by a launcher-started session with nobody watching.** Owner ruled at
13:41:59Z: launched sessions get ALL permissions (`--dangerously-skip-permissions` on the claude_1
lane, still through `claude-proxy`). Posture: mechanism trusts, PROTOCOL governs. My narrowing
recommendation was heard and overridden; I accept it and am not re-litigating.

- **Wake #3: 13:45:56Z, pid 3293323, launcher pid 3286799, ancestry ends at systemd.** Swept
  (1 new / 1 ack-required), read, acked, delivered the card's missing acceptance half, `--mark`ed
  as its own step, committed and pushed. Evidence:
  `claude_1/evidence/launcher-wake-3-unattended-drain-2026-08-20.md` @ `fa95afd2`.
- **The launcher card's bar — "a launched session DRAINS a real queue" — is now MET.** I claimed it
  in `20260820T134904Z-...-launcher-unattended-drain-handoff.md`. Bookkeeping note: the card left
  my queue at the 11:18Z handoff (`ack_for` discharge is idempotent); that delivery was rejected on
  an unmet bar, and this supplies the missing half. Not a second discharge — the substance closing.
- **Causal claim, controlled:** same wrapper, same ritual prompt, same worktree as starved wakes #1
  (3203009) and #2 (3218751); one variable changed. `git fetch`, `python3`, writes, `commit`, `push`
  all DENIED there and all succeeded here.
- **Standing rule adopted from the coordinator's postmortem:** wake quality is judged by DRAINED
  QUEUES, not wake counts. A wake that changes nothing logs an ordinary green `wake` line.
- **Not proven and not claimed:** contended queues, mid-ritual lint rejections, merge conflicts on
  `agent/claude_1`. Cap 4/h, pause file, single-flight lock, debounce NOT re-tested this wake.
  codex_1 lane still `enabled: false` (`codex exec` 403s on this host).
- Unchanged and still open: **VM disk 98% / 541M free** (unowned, flagged not claimed); card 2
  sentinel blocked on the `actionable_set()` extraction ruling; card 3 pair-selector deferred behind
  the OSC-031 KEEP/REVERT. Nothing was postponed by this wake, so no new `DEFERRED:` card is owed.

## Current position (2026-08-20, later) — proxy FIXED, launcher starves one layer up

**Inbox drained to 0/0 and pushed.** Head `agent/claude_1` carries: tooling sync (suite **119/119**,
was 105 — `agent_launcher.py` and the cc-ack narrowing were both missing here again), the `--mark`
stranded by a starved launched session, two evidence artifacts, two blockers, two acks, and the
quarantine registry resynced from the coordinator (I was one entry behind — my own 055011Z handoff).

### What actually happened today, in the right order

1. **The 403 was the PROXY, not auth** — the owner's memory, not any record. `/home/tarstars/bin/claude-proxy`
   (egress `10.77.0.1:3128`) is the sanctioned wrapper; `docs/vm-proxy.md` now exists so it can never
   be lost again. My credential-expiry diagnosis was **wrong**, and I cited `daemon-auth-status.json`
   = `auth_required` as support. **That file still reads `auth_required` with a live authenticated
   session running.** It was never evidence of what I used it for.
2. **Wakes #1 (12:38:16Z) and #2 (12:47:15Z) both authenticated and both starved.** `claude -p` is
   non-interactive: `git status/log/show/diff` allowed; `python3 …`, `git fetch`, `git commit`,
   `git push` and **`Write`** denied. A woken session can read the queue and cannot sweep, `--mark`,
   ack, publish, **or leave a DEFERRED card** — carding requires writing a file. Worse than the 403,
   which at least died visibly in 3 s; this logs an ordinary `wake` and changes nothing.
3. **The fix is tested, not proposed.** Per-lane `--allowedTools` on the launcher argv: Arm A ran
   (`42`), Arm B with the flag removed was denied — same wrapper, same command, one minute apart.
   Scoped to launcher sessions, not host-wide; push scoped to `agent/claude_1`, never
   `--dangerously-skip-permissions`. **NOT APPLIED — owner's posture call**, on the machine holding
   the Arena cookie. This is the one action that ends the starvation.
4. **I corrected the round summary's attribution.** It credited wake #1 with "read, marked, synced
   tooling". It read; it could not mark or sync. Those were mine, `mtime 12:29:33Z` vs the wake at
   `12:38:16Z` — **nine minutes earlier**. Wake #1's own log made the same misread of my uncommitted
   seen-state, and the summary compounded it. It matters because the repair aimed at it — sharpening
   the ritual prompt to "end pushed" — **was tested by wake #2 and refused**: a prompt cannot lift a
   permission denial. The ritual line is still right and still worth keeping; it is not what broke.

### Standing

- **The launcher card's bar — "a launched session DRAINS a real queue" — remains UNMET. I am not
  claiming it.** The next launched session that completes sweep → mark → commit → push unattended
  is the delivery, and it cannot happen before the allowlist lands.
- Card 2 sentinel build: still blocked on the integrator's `actionable_set()` extraction ruling.
  Note a precedent nobody has ruled on: `agent_launcher.py:58` gets the actionable set by running
  `inbox_sweep.py` **as a subprocess and parsing its stdout section headers**. That route needs no
  extraction ruling — and it is fragile in this project's signature way: reword a section header and
  `SECTION_RE` matches nothing, `paths` comes back empty, and the launcher reports "no work" instead
  of failing.
- Card 3 pair-selector Phase 1: still deferred behind the OSC-031 KEEP/REVERT.
- `night-runner` HEALTHY. **VM disk 98%, 541M free** — down from ~1.2G this morning; this has already
  blocked one deploy with ENOSPC.
- Trap re-hit and worth writing down again: `publish_outbox.sh` lints `--staged`, so running it with
  nothing staged lints **0 files and passes**. A gate with an empty subject is not a gate.

## Current position (2026-08-20) — two services deployed on the VM; one blocked on auth

**SESSION FLUSHED HERE. Read this block, then `troll-farm-vm-services`, `troll-farm-transport-rules`
and `troll-farm-osc031-state` in memory.**

### Services I deployed on the VM (check both first: `systemctl is-active night-runner agent-launcher`)

- **`night-runner.service` — HEALTHY, accepted.** Runs the M-1 decider night with no LLM from
  `/home/tarstars/prj/troll_farm-claude_1-lfs` on branch `agent/local_claude_1` (the branch NAME
  must match; the runner pushes that ref). Cookie `cgauto/cg_session.txt`, chmod 600, gitignored,
  never committed. Handshake `local_claude_1/door1-night-owner.txt` = `vm-runner` ⇒ laptop cron
  stood down. `Restart=on-abnormal`, deliberately NOT the card's `restart-always`, because
  `always` would retry the submission a HALT exists to prevent. 3 of 10 marks taken unattended.
- **`agent-launcher.service` — LIVE but REVIEW-REJECTED, and the reason is not code.** The
  mechanism is proven end to end: 11:34:08Z it detected a real peer message, debounced, wrote the
  pidfile, launched, logged `wake claude_1 n=1 pid=3107274`. **The session died in 3 s:
  `403 Request not allowed`.** `~/.claude/daemon-auth-status.json` = `auth_required`; `claude -p`
  reproduces the 403 by hand from an interactive shell; `codex exec` 403s too.
  **OWNER ACTION: re-authenticate the VM.** Re-test = one `claude -p` echo returning text.
  Service left active (cap 4/hour, sub-second failures); `LAUNCHER-PAUSED` silences it.

### Things that will bite the next session if forgotten

- **The launcher needs a FULL clone with ALL agent refs.** The card's "shallow ok" is wrong:
  shallow gave **518 phantom would-wakes** (seen-state materialization silently no-ops without
  `refs/remotes/origin/agent/*`) and made the quarantine registry reject as a set
  (`delivery errors 98 · quarantine errors 1 · quarantined 0` vs the true `0 · 0 · 12`).
- **VM disk is 19G and hit 100%**, blocking a deploy with ENOSPC. ~1.2G free now. Eight checkouts
  live here; this recurs.
- **A self-authored message never enters your own actionable set** — so the launcher card's
  self-probe cannot trigger a wake, by construction.
- **Only `ack_for` discharges; `supersedes` is inert.** A `CARD:` is discharged by the delivery
  handoff or a `DEFERRED:` replacement naming it in `ack_for` — never a bare receipt-ack.
- **Never `git commit` without a pathspec while a lint-rejected message is staged.** That is how
  an invalid handoff of mine reached origin and had to be quarantined, which made all 12
  quarantine entries reject for a sweep.
- Sync `scripts/` **and** `tests/` each session; my suite read 105 when it should read **117**.

### The OSC-031 lane

Phase 2 REJECTED (9 de-novo). I proved **pre-build** that Door-1b could not pass and that
two-truths was worse (5–14 vs a gate of 0) — no 240-game panel was spent on either. Owner then
ruled **named-costs**; my package (9 costs named, 15 healed, 53→47, latency, parity) was ACCEPTED
and reproduced byte-identically. **Decider night running**, pre-registered σ_pair 1.5 / bar 1.315
at n=5. KEEP/REVERT is the owner's.

### My open cards

- **Card 2 sentinel build** — blocked on ONE ruling: may `actionable_set()` be extracted into the
  coordinator's `inbox_sweep.py` so `main()` and the sentinel share one path? Not gated by the
  launcher.
- **Card 3 pair-selector Phase 1** — deferred; it is third and its subject rebases if tonight is
  a KEEP.

## Current position (2026-08-19) — gate 1 r4 delivered, sits with codex_1

- **Task `20260818-osc031-forecast-defect-fix`, gate 1 r4 DELIVERED** (`20260819T134755Z`,
  artifact `52bde865`, message `32cfdc9a`). codex_1's r3 verdict was REVISION_REQUIRED on one
  check-that-cannot-fail: `seq2_rows` was **assigned** `PREDICT_TREE_NONE + SEQ2_PASS` and then
  compared against that same expression, and its control called a local `check()` helper the
  production run never invoked. The finding was right and I accepted it without argument.
- **Repair**: the probe now emits a distinct `USEQ2` **entry** row immediately before
  `predict_tree`, under the same `(call, plant)` identity, so the left side of the identity comes
  off the wire. `tally()` is the single counting path, `chain_check()` the single chain checker —
  per-fixture, aggregate, counter controls and observed controls all call it. Three controls
  delete or duplicate **actual emitted rows** and re-derive through `parse_join` + `tally`; each
  runs on the first fixture that can host it and the runner **raises if any never ran**.
- **Every count is byte-identical to r3** — the only diff in `gate1-unified-2026-08-19.json` is
  `probe_sha256` on both subjects. The assigned numbers were not wrong, they were **unmeasured**.
  Resident 120 EVIDENCE_BASED / 530 UNEXPLAINED; candidate 103 / 0; seq2 entry observed
  9,900 = 650 + 9,250 and 7,368 = 103 + 7,265; `later = 0` on both.
- **Declined one thing codex_1 offered and said so**: no observed control deleting a downstream
  terminal, because all four downstream clauses have **zero rows on either subject**, so the case
  could never execute — the same inert-check defect in a new place. Counter control covers that arm.
- **Tooling**: `scripts/lint_outbox.py` was stale on this branch — `origin/main` and
  `agent/claude_1` both lacked the cross-task-reference and deferral-shape gates that
  `local_claude_1` has carried since 2026-08-18. Synced from `origin/agent/local_claude_1`
  (`3448833b`); transport suite 105 pass. **`origin/main` is no longer the freshest `scripts/`** —
  check the coordinator's branch too.
- Inbox: **0 unseen, 0 ack-required** at 13:50Z, cross-checked against peer branch logs.

## Current position (2026-08-17)

- **POOL #3 DELIVERED** (`20260817T171000Z`, artifact `4514db90`, `review_ref:` →
  `codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md`). Pools #1 and #2 are
  CLOSED (GATE_ACCEPTED). Table: **`GOAL_SPLIT_WRONG` 21 · `NO_GOAL_ASSIGNED` 6 · `NOT_STARVED` 4
  · `CANNOT_USE_WORK` 2 · `WORLD_INTERACTION` 0**, plus OSC-026 `NO_ANCHOR_SINGLE_UNIT` (coverage
  state, not a cause). WAIT turns: 2,240 / 521 / — / 349 / 0.
- **The dominant cause is not the generator.** In 21 of 34 the generator DID offer the parked
  troll a real candidate and `select()` discarded it. **That is not a defect claim** — `select()`
  maximises a joint score and the trade may be right; the token records *where* the WAIT came
  from. Whether it is worth changing is pool #6.
- `WORLD_INTERACTION` = 0 is a **measurement**: the 97 manufactured `MOVE→WAIT` land on the
  DANCER (94 in OSC-034 unit 2; anchor is unit 0), one outside its window. `--control` observes
  the arm firing on 94 turns, so the zero is not a dead branch.
- **Two defects of my own in the sweep, both found by reading per-turn records, not totals:** the
  kinds regex read the adjacent `ncand` group (so `NO_GOAL_ASSIGNED` was **unreachable** and 21
  rows were `GOAL_SPLIT_WRONG` by construction — a complete, plausible, wrong table); and
  `NOT_STARVED` cleared any unit that acted once (OSC-023: 73 WAITs of 74). Both now guarded.
- **Token SEMANTICS were never published** — the registry bound spelling only. Mine are in
  `cause_table.py`'s docstring; per-turn attribution ships in the artifact so a different ruling
  needs no re-run.
- **I retracted a false claim of my own about `codex_1`** (`20260817T163500Z`). My status query
  asserted their published work since 12:00Z was spec reviews; it was not — their pool-#2 verdict
  was published 11:23Z, addressed to me, `requires_ack: false`. **My sweep gates on the
  ack-required count, so it CANNOT surface a verdict.** Zero unacknowledged is not zero unread.
  Standing correction: before calling a sweep clean, check whether anything addressed to me is
  newer than my last read, whatever its kind.
- **LOGGING-POINT REPAIR DELIVERED** (`20260817T160500Z`, artifact `8cd55c14`, instrument
  `1384df74`) — `codex_1`'s pool-#2 verdict was REVISION_REQUIRED on one blocker: `HS2` logged
  before `force_unique_door_clear` and `HS2CHOSEN` before `resolve_move_conflicts`, so both could
  record what the selector never received and the engine never got. Taps are now **duplicated**
  (`HS2PRE`/`HS2`, `HS2CHOSENPRE`/`HS2CHOSEN`) so the mutation paths are **observable**, and the
  final-stage names are the ones every consumer already parses.
- **The blocker was material, not cosmetic:** on all 34 situations, door clearing rewrote a
  candidate list **21** unit-turns, conflict resolution rewrote a command **3,517** turns, of which
  **97 are MOVE → WAIT**. A table built from the old tap would have credited those **97
  manufactured WAITs to the generator, which never emitted them**. The other 3,420 are target-only
  (order-vs-landing) and change no attribution.
- **Row totals were UNCHANGED by the repair** (12,981 / 6,800). Coverage counts could never have
  caught this — only reading the emit point could. Everything `codex_1` accepted (anchors, count
  reconciliation, oracle repairs, fail-closure, 34/34 parity) stands.
- Instrument is now **regenerated from the byte-exact resident** by `make_instrumented2.py`, which
  refuses on a non-unique anchor and asserts tap ORDER **positionally**; the previous one was
  hand-edited. `coverage.py --selftest` drives three rejection arms of `check_final_stage` plus a
  positive twin; the tap comparator runs PRE-against-PRE and must find zero differences.
- **Both specs are OWNER-APPROVED and the specs task is CLOSED.** I am the named implementer and
  am **NOT authorized to build**: implementation needs pool #6 **and** an explicit owner go.
- (superseded 16:07Z) **Pool #1 REVISION IS HANDED OFF** and sits with `codex_1` for pool-#2 review: handoff
  `20260817T111300Z` at `37c5b9b3`, instrument pinned `0a95de5b`. Artifact and all four declared
  paths verified reachable on `origin/agent/claude_1`. Parity + coverage since closed at **34/34**
  (`34857fa1`) — the limit I had handed over at 3/34.
- **Since the anchor revision I self-audited and found FOUR more defects of my own**, all fixed and
  each observed firing: `PLANT` eligibility was **always true** for any carrying unit
  (`any(c in reach for c in walkable)` — `reach` is a BFS *over* walkable from the unit's own cell);
  `BANK` rested on `td.orth_neighbors` behind a `hasattr` guard and **that helper does not exist**,
  so the predicate silently weakened; `check_parity()` had **never rejected anything** (now observed
  rejecting a deliberately different bot); and `UNRULED_SHAPE` had **never executed** (now observed
  on an unknown kind and on a blocker cell matching no own unit).
- **The deadlock that cost two hours was mine.** I reported "awaiting acceptance" for two hours
  while never sending the pinned handoff `codex_1` was waiting for; each side believed it was
  waiting on the other. **Self-audit is not a substitute for the review gate — ship, then audit.**
- (superseded 12:30Z) **Pool #1 (instrument repairs) is REOPENED**, not complete. I declared it complete while two
  rulings addressed to me sat unread — the transport did not fail, I did not sweep before claiming
  done. **Rule I now hold: sweep immediately before any handoff that claims completion.**
- Anchor rule **revised to the ruled per-kind mapping** (`5802e357`): D1-with-blocker → blocker
  unit; D1 blocker-less pair → unique non-dancer; D1 single-unit → honest no-anchor (OSC-026);
  **`P4_STALL` → `window.unit` ITSELF** (my uniform "not the dancer" rule excluded the subject in
  all four stalls); anything else → `UNRULED_SHAPE`, fail-closed. 0 fall-throughs.
- Count reconciled: **3 single-unit situations** (OSC-026/032/033) but **1 no-anchor state**
  (OSC-026) — the other two are stalls that now anchor on the dancer.
- Other four repairs delivered but **not silently accepted**: eligible-action oracle with both
  charter arms observed firing each beside a positive twin (`f9748283`); candidate-kind and
  chosen-action logging; exact one-row-per-turn coverage with duplicate rejection; **runner parity
  PROVEN** byte-identical to `regression_tests.run_binary_custom` (`97714f13`).
- **Pool #3 not started** and must not start before `codex_1`'s pool-#2 acceptance. It serializes
  exactly `NO_GOAL_ASSIGNED` / `GOAL_SPLIT_WRONG` / `WORLD_INTERACTION` / `CANNOT_USE_WORK` /
  `NOT_STARVED` and carries `review_ref:`. **I will not map old labels onto these by inference.**
- **T-1 is FROZEN** for me; half-swap fixture is recorded debt.
- Transport: WIP limit (one in-flight ack-requiring handoff per task) and the evidence gate
  (`review_ref:` on any cause label) are machine-enforced. `scripts/` drifts on this branch —
  sync from `origin/main` every session; `pool_status.py` was missing this morning.

## The error pattern this week, stated so it is not repeated

Three published causal claims, each resting on a proxy I had not validated: all-WAIT for "no work
offered", geometric reachability for "work available", a frozen world for a live one. **Each time
the direction felt obvious and each time the proxy was the whole argument.** Plus three inert
checks shipped (viewer inference-marking, harness detector clause, stage-2 reachability model),
each caught only by a negative control, never by reading the code.

- (superseded) Updated UTC: 2026-08-15T19:39:00Z (REAL clock, `date -u`)
- **VIEWER REV 2 — all four `codex_1` blockers fixed** (`e29cf6bd`, ack `86e2f6e4`). **Blocker 1 was a real data-labelling bug I shipped:** inventory columns as `PLUM, APPLE, LEMON, BANANA, ORANGE, WOOD` where the subject's own `pub const` declarations (`:11-16`) say `PLUM, LEMON, APPLE, BANANA, IRON, WOOD` — two fruits transposed and `ORANGE` invented where the authority has `IRON`. Every inventory and carry column on all 34 pages was wrong. **I asserted a label instead of deriving one** — everything else on the page was derived and machine-checked; this one list I typed from memory. `check_slot_order()` now parses the constants from the subject and fails the build on disagreement, with a control reproducing my exact wrong order. Also fixed: frozen evidence rendered (mechanism, blocker state/cell, unresolved, provenance) with the blocker cell marked; **frame 0 is now the ENTRY state** — entry is the only exact board state and my first build applied turn one's command before rendering, so the one ground-truth frame was never shown; and the ordered cell now has its own mark, separate from the assumed arrival. Self-test 11 → **23 cases**. Visual layer still unverified by execution and rev 2 adds three new mark types, so a human look is **more** necessary than before.
- **P-1 INCREMENT 2a DELIVERED** (`e43d000b`, handoff `20260815T193500Z`): the required-site inventory **derived from the subject, never from `SITES`** — the circularity `codex_1` named. **249 §5.4-required sites; the registry names 132 (53%), 117 unnamed.** GEN 22/79, TERM 12/20, FILTER 52/76, EARLYRET 34/58, ARBITRATE 12/16. Independence is *tested*: enumeration is byte-identical with `SITES` cut to 3, and coverage falls 132 → 13. **`endgame_candidates` (`:1233`) is absent from the registry entirely** — the generator the D3 appendix places C2/C3 inside, holding 3 unnamed score-term sites; `idle_harvest_candidates` (`:1340`) absent, a plausible home for `IDLE_HARVEST`, one of the five intents increment 1 flagged as unbound. Offered as **candidate** mappings: status `PROPOSAL_FOR_INDEPENDENT_REVIEW`, and **I will not curate what I derived.** Limits: class matchers are proxies, so 249 is an upper bound; coverage measures NAMING, not semantics.
- **Transport note against myself:** mangled a commit message with an unescaped backtick, then amended an already-pushed commit. Push rejected; **reset to the remote rather than force-pushing** — published history stays immutable.
- (superseded) Updated UTC: 2026-08-15T15:32:00Z (REAL clock, `date -u` — see the stamp-drift correction below)
- **D2 PHASE 1 VIEWER DELIVERED 2026-08-15**, artifact `423b87a1`, handoff `20260815T152700Z`. 34 self-contained pages + index, generated through `load_library(verify=True)` (fails closed), no server, no external asset, keyboard step-through, display-only. Acceptance verified against generated output, not intent: 34 pages, 13 with `+`/`~`, OSC-032/033 as stalls, 32 2-cell cycles, frame indices consistent. **11 guard cases, each observed rejecting — and two caught real defects in my own code.** (1) The inference-marking check was **inert**: it matched the required class against the whole tag, and `data-role="derived-position"` itself contains the substring `derived`, so an unmarked element passed. Only the negative control exposed it. (2) The opponent was drawn **hollow**, the same treatment as inference, while the legend claimed "solid red circle" — ground truth and assumption looked alike. **No referee re-implementation:** no predicted landing is computed, because a BFS/speed mirror that disagrees with `engine.rs` is worse than no mirror. **Known limit, stated not papered over: no browser on this host, so the visual layer is unverified by execution and needs one human look before the first live session.**
- **P-1 INCREMENT 1 RELABELLED `PARTIAL_FOUNDATION`; acceptance item 1 REOPENED** (`codex_1` review `155d8dd8`, relabel `6701aa16`, ack `453361d3`). **I reproduced both of their claims by execution before accepting**: relabelling `GEN_FRUIT_CANDIDATES`'s intent `HARVEST_FRUIT` → `MINE_IRON` gives **0 failures**, and deleting three sites outright gives **0 failures**. Withdrawn: "this is rollout step 1", "this closes item 1", and "`validate_registry()` closes the wrong-at-freeze hole" — it closes only the *syntactic* subset. The registry is a **versioned partial**: no `FILTER_*`/`TERM_*` ids, so adding required sites will change `source_registry_sha256`. `STATUS`/`SEMANTIC_GAPS` now ride **inside the frozen JSON** so the label survives reading the artifact without its source. Guard suite untouched and green (26 cases, 21/21 types firing). **The recurring lesson, twice in one day: an accurate caveat lower down does not repair an overclaim in the summary — the summary is what gets quoted. Naming a gap is not pricing it.**
- **Before step 1 can genuinely freeze:** a required-site inventory derived *mechanically from the subject*, not from `SITES` (deriving expected coverage from the thing being checked is the same circularity `codex_1` killed in the viewer's acceptance check 4), published as a proposal and checked by someone who did not write it. **I will not author and then review it.** Sequencing is `local_claude_1`'s.
- Inbox clean, sweep exit 0, 0 unacknowledged (2026-08-15T15:32Z). Acked this cycle: owner rulings 3–5 (`f408b5c0`, with the materiality-floor false-stop risk quantified — **14.6% chance of stopping as "immaterial" at a true Δ of 2.0, n=5/arm**), D2 scope agreed (`9c207db8`), the two `codex_1` reviews (`453361d3`). Claim `c5f1add3`.
- **P-1 INCREMENT 1 DELIVERED 2026-08-15, artifact `ef76ab54`, handoff `20260815T054700Z` at `96f50105`.** Rollout step 1 / acceptance item 1 of the frozen Decision Packet contract: §4 envelope as code (`check_envelope`), §5.1–5.4 registries code-owned with prose as a generated projection, 22 source sites pinned by `start_line`, drift guard. **26 self-test cases, 21/21 declared failure types observed firing**, coverage computed from what the checkers actually emitted; the coverage assertion itself verified failing on an unreachable declared type. Subject byte-exact `98628e98…` before and after. **Two guards existed only on paper until this pass:** `SITE_MISSING` had no control at all, and `SPAN_CHANGED` was masked by `SITE_MOVED` in a shared any-of case — both now have their own controls. **The design point worth re-reading: drift checking cannot catch a registry that was wrong at freeze time**, because the frozen and live copies are built by the same code, so `validate_registry()` checks the registry against the *subject* instead. NOT complete and does not claim to be: 22 sites of 79 fn definitions, no `FILTER_*`/`TERM_*` ids, all 13 intents carry null predicates with `predicate_status: UNSPECIFIED`, 16 of 17 acceptance items open.
- **V1 CONCURRED AND MY P-2 SENTENCE WITHDRAWN (2026-08-15, ack `c4cf77dd`).** `codex_1`'s D2/D3 review is `REVISION_REQUIRED` and its blocking V1 lands on my own P-2 wording: I wrote *"own-side reconstruction is sound … replaying command lines will not hit a hole"* on the strength of command **contiguity**. Contiguity is a fact about the command record; positions are a different quantity. Verified in the authority, not taken on trust — `engine.rs` (`7c240abf…`) `next_cell` returns the target only `if d <= speed`, so a distant `MOVE` lands intermediate, and simultaneous resolution against an unrecorded opponent can move it again. **My own counter-proposal item 4 stated the correct rule and my summary line four paragraphs earlier contradicted it: a caveat further down the page does not repair an overclaim at the top.** Phase 1, if built, renders verbatim command / command target / *predicted* position as three distinct classes, every side panel stamped `at entry`.
- Inbox clean, sweep exit 0, 0 unacknowledged (2026-08-15T05:55Z). Acked this cycle: two `codex_1` claims (`30dfdad9`), two `codex_1` review handoffs (`c4cf77dd`). Working checkout is `/home/tarstars/prj/troll_farm-plan-agent`; `scripts/` verified in sync with `origin/main` this session.
- State: **inbox clean, sweep exit 0, 0 unacknowledged, 0 delivery errors.** Three `policy` messages processed this cycle: the two quarantine adjudications (`20260812T193500Z` superseded by `20260812T193800Z`) and the **bounded arena lease `20260812T201400Z`, ACCEPTED and not yet started**. Acks at `5c753f9f`, `26afe667`, `85045fed`.
- **ARENA LEASE COMPLETE 2026-08-13T06:43Z — all five steps delivered, authority reverted to `local_claude_1`.** Final handoff `20260813T064318Z`, artifact `a890dfa9`, published `cdbc5800`. **Pooled within-source SD = 1.501** score points, 95% CI [1.049, 2.634], 4 families / 14 mature observations / 10 d.o.f. — up 37% from 1.098, and the CI's lower bound now sits *above* the old point estimate. Campaign family n=6: [19.77, 22.46, 23.39, 23.73, 24.76, 24.90], range 5.13 (2–3× every other family). **`docs/STATE.md` §3's ±0.5–1.0 band does not survive**; a ≥+1.0 gate needs 5 runs per arm, not 3. Run 4 = `41129543` / agent `6614096`, owner-authorized in session. **Re-deployment noise and ladder drift are confounded and no analysis of these six observations separates them** — the runs are sequential, never contemporaneous, spanning 08-04→08-13 while the field grew 139→147.
- **The stale arena-room row is the story of this campaign.** `6604529 / field 140 / 22.46` appeared **six times** across two days, including on three consecutive *complete* 160/160 reads of run 4. **A gate on `matching_finished == 160` alone would have recorded 22.46 — another deployment's score — as run 4's terminal observation, with 0 pending, 0 unexpected rows and 0 fetch failures.** Gate on `identity_clean` AND the process exit status; `field total 140` is the reliable tell. Related repair `a9abae5f`: `submission_history.py` validated `filtered_ladder.agent_id` but never `arena.agent_id`, then read score/rank/field from that unchecked block — silent corruption with `identity_faults: 0` and maturity `terminal`. Two tests, both verified to fail first. `codex_1` reviews; I authored it.
- **Read the label, then read the content — the content wins.** I escalated a semantics question about run 2 that did not need to exist: `run2-checkpoint-initial.json` was a complete 160/160 clean terminal observation (23.73) sitting in the same directory the whole time. I had filtered on the `*-terminal` filename role and never opened it. Maturity is keyed on `matching_finished`/`matching_pending`/`identity_clean`, never on a role string.
- **`publish_outbox.sh` fetched only `origin/$BRANCH` until 2026-08-13** — so publishing could never surface inbound mail, and a policy addressed to me sat unread for 8h28m while I executed the task it governed. Fixed on trunk (`git fetch origin`, all refs), synced here at `5596941d`. **Binding: any Arena mutation requires a full `--fetch` sweep with its exit examined within ~10 minutes of the call.** Publishing is not freshness.
- (Superseded) **ARENA LEASE HELD (bounded, reverts on final handoff)**: σ campaign steps 1–5, serialized. Preconditions verified independently — cookie sha `09164093…` mode 600, gitignored + untracked; submission blob = `98628e98…` in three-way agreement with the `--expected-sha256` and the committed sidecar; run-3 interim is the 118-game read (arena 23.61, filtered 23.73, rank 31/147). **Step 2 (run-4 submit, the fourth and LAST budgeted mutation) is held for an explicit owner go** — irreversible, single call, ambiguity → STOP with no retry. Execution-environment gap named to the coordinator: the cookie is in the ~1300-commit-stale `/home/tarstars/prj/troll_farm`, the tooling is at `f7069d16`, and `troll_farm-plan` is detached at `21bd338d`.
- **`scripts/publish_outbox.sh` — the wrapper the coordinator calls binding — was ABSENT from `agent/claude_1`.** `scripts/` was stale against `main` by nine files; synced at `7ec39b4c`, and every message this cycle published through the wrapper with the lint armed. Second silent drift of this directory while the publish gate was defined as one of its scripts. **Verify the gate exists before trusting it; nothing on screen announces its absence.**
- **`requires_ack: false` does not exempt a `policy` message.** `policy` is in `ACK_REQUIRED_KINDS` (`scripts/inbox_sweep.py:78`) and the set is applied after the field (`:289`), so both adjudications declared `requires_ack: false` and both were correctly reported ack-required. Raised with the coordinator; needs a ruling.
- **250 messages remain `new (unseen)` and the watermark was deliberately NOT advanced** — protocol forbids blanket timestamp-marking a backlog before a pushed legacy-backlog audit. That audit remains the outstanding transport work.
- **Filename stamps ≠ real time.** Messages named `20260813T*` have real commit dates of 08-09; the M3a repair, the transport review and bite-test r2 are all ancestors of the current tip despite later-looking names. Trust `git log`, never the filename.
- (Prior cycle) **G2 delivered and accepted** (substance ACCEPTED by `codex_1`; the `task_id` provenance revision is published at `6fbacca4` and awaits the coordinator's integration, at which point G2 closes). **G6 started: all four D-7 branches pinned, 4 of 19.** Collector-v2 tasks both in `review`, all findings ACCEPTED.
- **G6 COMPLETE 2026-08-13 — 19 of 19 actionable branches resolved** (artifact `bb845da5`, handoff `20260813T200014Z` at `dac57f73`). Whole-manifest mutation: **51 caught / 25→13 survived of 64**, `caught_by_expected` **51/51**, control green. Ledger `impl_validity` **33 PINNED, 3 PARTIAL, 6 UNPINNED, 5 NO_FIXTURE** — from **12 PINNED / 22 NO_FIXTURE** when G6 opened; mutation from **21/64** at the audit's first publication. Groups: D-7 (4) → 29, D-8 (3+1) → 33, D-5 (3+2) → 39, D-6 (3+1) → 46, D-1/D-3/D-4 (4+1) → **51**. Detector suite 67 tests OK; audit self-tests 13 passed. **D-9 (b)/(c)/(d) still parked on the c5 instrument ruling, which is assigned to me after G6 and is now the natural next item.**
  - **TWO BRANCHES ARE UNPINNABLE — EQUIVALENT MUTANTS, PROVEN NOT ASSERTED.** **D-8 (b)** `plant kind == BANANA`: reached only inside `c in alive_per_turn[t]`, and `own_banana_history` builds that set from the *same* `state(t)` with the same kind filter. **D-4 (e)** DROP-at-door commitment start: `DROP` is not in `D4_BANNED_VERBS` so no episode can be raised on that turn, `executed_drop` clears `committed` on the same turn, and the only residue `nd_run = 0` is set by every commitment start anyway. Each proved by construction **and** by differential (**0/416 probe-corpus traces differ**). **Both left COUNTED and their rows at `NO_FIXTURE` on purpose** — excluding them moves the headline 51/64 → 51/62, i.e. in my own favour, so the disposition is referred to the coordinator. Each carries a test pinning the *reasoning*, so if the surrounding code changes the branch fails loudly.
  - **D-6 clause (a1) is close to inert and is reported, not repaired**: `min_own` is always 0 at a PLANT event because the planter stands on the cell it plants, so `opp_h <= min_own` can only fire when an opponent harvester shares that exact square. Pinnable that way, but not what the spec text suggests. Detector-semantics question; G6 changes no predicate.
  - **Nine of the newly caught mutants were incidental** — killed by fixtures aimed elsewhere. Each was traced, its `owner_test_classes` extended, and reported; `caught_by_expected` was short at every group until they were named. Two recurring levers: **asserting an exact boundary value constrains every term in the formula that produces it** (the D-5 deadline pair also pinned the cutoff arithmetic), and **asserting a value sits just OUTSIDE a bound constrains how far that bound can move** (the D-6 speed pair also pinned the `<= 2` clause).
  - **A test asserting SILENCE needs a companion proving the noise was available.** The D-1 progress clauses suppress episodes rather than raise them, so their fixtures assert absence; `TestD1Uncovered` therefore opens by showing the same pacing with no progress event *does* fire.
  - Boundaries verified not asserted at every group: no predicate touched, nothing under `rust/`, `yamo_orchard_live.rs` byte-exact sha256 `fff6669b0bc0b15b…`. Pinned-source drift re-pinned every time, never `--allow-drift`.
- **Owner plain-language policy in force (`20260813T191500Z`, acked `4b011941`)**: anything the owner reads opens with a sentence a non-specialist can follow, spells out what a thing IS before its code name, and gives numbers meaning. Technical artifacts keep full precision; the plain summary goes in the message that carries them.
- **THREE OF MY OWN GUARDS FAILED TODAY — read before publishing anything.** (1) **Message stamps ran up to +42 min ahead** of the clock because I incremented them by narrative instead of reading `date -u`; my drift put a coordinator reply *before* the message it answered. (2) **I published an invalid `correction` with an empty `supersedes`** — the identical defect that quarantined `20260807T113000Z`. (3) **I broke the publish gate**: `lint …; echo "LINT=$?"; git add … && commit && push` chains off `echo`, which always succeeds, so the gate ran and gated nothing. Worse, once pushed the message becomes *published* and default lint **skips it** — exit 0, defect invisible. Use `lint … || exit 1`, and `--all` after publishing. Retiring a message also **retires every ack it discharged**: carry `ack_for` forward when superseding.
- **`project_host`'s cron fires 02:17 UTC, not 05:17** (crontab `17 5` on Europe/Moscow) and skipped Aug 11-12. My unit comment and reports are corrected: 05:47 is right, but by luck not by the stated reasoning.
- **First unattended collector run** (2026-08-12 05:47): 6,295 candidates, 6,295 held, **0 fetched, 0 dropped**, exit 0 — verified as coverage not blindness (max held id `898583715` > max live-window id `898550181`). **Cut-over caution: with the platform quiet AND the reference cron intermittent, the seven-day criterion measures neither collector.**
- **Three measured facts to carry:** replay availability tracks participant battle windows, not age; the bucket grant blocks deletion but NOT overwriting (append-only is enforced by `If-None-Match: *` in our code); *missing from a day's manifests* (352) is a different question from *absent from S3* (**0**).
- Role: contributor + **execution reviewer** on every artifact. Coordinator/integrator/arena controller AND detector-semantics owner = `local_claude_1`. **`chatgpt_1` and `chatgpt_2` are unreachable** (owner ruling 2026-08-12). `codex_1` is a NEW agent (canonical `agent/codex_1`, onboarded 2026-08-09) and is **not** `local_codex_1`, which is dormant since 2026-08-06.
- Branch: agent/claude_1-banana-restoration-r2; canonical agent/claude_1 at `7366e1cf`. Tooling `inbox_sweep.py` `be8251c4…`, `lint_outbox.py` `f3c47b70…` (synced from `main` twice this cycle — `main` moved under me).
- **Read `claude_1/SESSION-FINDINGS-2026-08-07-to-11.md` before acting.** It carries the programme state, the measured findings, and the error patterns. It predates the 08-12 unblock below.

## Blocking state

- **The TRAIN/referee blocker is CLEARED.** r4 accepted by `chatgpt_1` for the c5 execution layer; B1 closed by `local_claude_1` through independent execution in a second checkout (7/7 artifact digests, `engine.rs` `7c240abf` untouched, panel 163 OK, pre-review 24 OK, mutation 16/16 caught, and floor packets **row-level `IDENTICAL`** to committed `evidence-r4/` — agreement on *which* games block, not just the total). The r4 panel is merged to `main`: `main:claude_1/pipeline/fuzz_panel.py` = `d8900abf31dd030d…`, 33 TRAIN references. `main` was pre-r4 until 08-12, so anything measured from `main` before then used the broken referee.
- **This does NOT authorize verdicts.** `chatgpt_1` holds I-30 at `GATE_UNREADY / MEASURED_UNTHRESHOLDED` and states plainly: **no detector branch is authorized for candidate acceptance, and no I-30 PASS, FAIL, threshold or candidate verdict is accepted.** Do not read the r4 acceptance as a gate opening.
- Instrument `fuzz-panel/5` · corpus `c5-two-player-phase-merged-2026-08-11`. **Floor (parent vs itself) = 118/240. Candidate run (banana `eac2eb36` vs parent) = 121/240.** Different quantities; `run_identity` is machine-checked. `118/240` is quotable **only** with r4's binding restriction attached: TRAIN is witnessed in 2 games (1 spawn each), and 10 of 17 repaired rules have no corpus witness — those are pinned by unit tests, the two-oracle differential and the mutation drive, never by the floor.

## Reviewers — resolved, and degraded on purpose

`chatgpt_1` held every review slot below and is unreachable. `codex_1` claimed
`20260807-gate-architecture-review` and the M3a idle-blocker replication, and declined the rest.
`local_claude_1` ruled (`20260812T211000Z`, superseding `20260812T204000Z`): **three of the four
reviews had already been delivered before `chatgpt_1` went dark**, so the vacancy is the *re-review
of my repairs*, not of my current work — I am not blocked.

Standing terms of that ruling, all still in force:

- **I do not review my own repairs.** Not negotiable, and it is why I am not the check on anything
  below that I author.
- Anything `local_claude_1` reviews alone is labelled **`SINGLE_REVIEWER_DEGRADED`**; it is the
  coordinator, so it adds a second look, not a second opinion.
- **Nothing closes as fully `ACCEPTED` under a single reviewer without the owner's sign-off.**
- Every `chatgpt_1` disposition is **`RECORDED / UNREPLICATED`** until reproduced by execution here
  — they rest on self-run Actions jobs by the reviewing agent, the same evidence class as the
  quarantined 2026-08-06 fabrication.
- `local_claude_1` **cannot** review `20260807-transport-quarantine-and-outbox-lint` (it authored
  it), so that task still needs a second reviewer; I am one of the two required and the other slot
  is unfilled.

Worth remembering: I once treated a reassignment table as a settled allocation. It was an *offer* —
a reassignment is not complete until the receiving agent claims it, and the decline was already
published when I wrote. **Re-sweep between reading an allocation and acting on it.**

## Open dispositions requiring my revision work

- **M3a correct-subject** — **REPAIRED AND DELIVERED** 2026-08-13, handoff `20260813T003000Z`, artifact `ae701fc4`. Each panel config now carries `source_git = {commit, path}` on an immutable 40-hex commit; the replay materialises the blob and re-checks it against the config's own `sha256` before compiling; corpus skips are evaluated before compilation; no absolute host path remains in either config's data fields. `fuzz_panel.py` untouched (`d8900abf…` is the accepted referee digest). Verified against a control that failed first: with the scratch directory masked, pre-repair reproduces `chatgpt_1`'s `PanelError` verbatim and repaired gives 94 tests OK / **34 of 34 byte-for-byte**. New `TestSourcesArePortable` (6 tests, default suite, no `rustc`) makes a recurrence a failure now. **Still open and not mine:** the M3b substrate selection — the c5 46-episode diagnostic library and the golden v2 record (34 exact D-1 episodes / 32 source games) are different populations and neither may silently replace the other.
- **Bite-test audit r2** — **blockers 1, 2, 4, 5 CLOSED; blocker 3 open.** Handoffs `20260813T030000Z`, `20260813T054000Z`, `20260813T081000Z`; latest artifact `3e5ade1b`.
  - **4** `run_mutations.py` exit status describes the experiment: `1` control not green, `2` incomplete, `0` only when whole; `--only` needs `--partial`. Accepted.
  - **5** 47-branch tallies derived from `branch_ledger.json`; `render_branch_ledger.py --check` compares audit prose to data both ways. Accepted. **The contract-authority tally was never derivable from the table** — now an explicit field.
  - **1** `LIVE` → **`PROBE_SENSITIVE`** with the limit inline everywhere: *changes probe output on generated traces; does NOT establish legal-game reachability.* Results schema bumped to `detector-mutation-results/3`; derived artifacts regenerated, not edited. Measurement unchanged and verified: 64 counted, 21 caught, 43 survived, 30 probe-sensitive survivors.
  - **2** No contention label. `max(speed, 1)` replaced by the engine's own `d <= speed` — **`engine.rs::next_cell` has no floor**, so at speed 0 the authority returns `current`. Three D-3 rows carry `NO_WITNESSED_POPULATION (720 referee games, 3 corpora)`. **Binding wording: zero observed episodes is a statement about this corpus, NOT "the predicate cannot fire."** No D-3 branch is probe-covered.
  - **3** — **substantially unblocked 2026-08-10, not closed.** The owner's strict rule (*no banana manipulation before training the second troll*, threshold 0) **dissolves** D-9 (a)'s affordability question rather than answering it: there is no affordable delay to price when the permitted count is zero. Row (a) is the operative rule, no longer a retired proxy. **I pinned it** (handoff `20260810T111000Z`, artifact `80c3dd63`): it was `UNPINNED` with D9-M1/M2/M3 surviving — a strict rule policed by a detector nobody had shown could tell right from wrong — and three negative tests, each verified to kill its own mutant before being written, take D-9 to **4/4 CAUGHT, 0 survivors**. Overall 21→24 caught; tally 11→12 `PINNED`. **Paired branches (b) `train_late`, (c) `train_missing`, (d) `train_stats_differ` still carry the stale pre-c5 `INSTRUMENT_UNSUPPORTED` label and are NOT addressed** — the rule says nothing about non-banana TRAIN displacement.
- **I-30 rev 3** — **blocker 2 REPAIRED**, handoff `20260813T050000Z`, artifact `7e5c9874`. Owner-freeze chronology is decided by Git ancestry between the decision's commit and an immutable `observation_anchor`; an anchored authority refuses to fall back to timestamps, so an unanchored production run cannot reach `verified`. Demonstrated: the pre-repair analyzer verifies a bound frozen AFTER the observation with **zero reasons**. 105 existing tests still pass + 8 new (all 8 fail pre-repair). **Blocker 1 still open** — `ExecutionValidity` still validates a self-declaration: `referee_sha256` checked for presence only, `verb_manifest_sha256` self-consistent by construction, command counts caller-supplied. Design proposed; awaiting a ruling on whether the verb manifest is *derived from the dispatcher* or *bound to a committed registry of reviewed referee digests*.
- **M2 rev 2** — accepted, nothing owed. **Fast-verification-executor requirements** — **PARKED** by the coordinator: its author is unreachable and nobody inherits an unowned spec. `coordination/tasks/20260811-fast-verification-executor-design.md` is `PROPOSED / BLOCKED ON REQUIREMENTS REVIEW`, owner unassigned.
- **`20260807-transport-quarantine-and-outbox-lint`** — my execution review delivered 2026-08-13, handoff `20260813T012000Z`, artifact `afb6903a`: **`REVISION_REQUIRED`**. Accepted: the 41-message delta is exact, all 41 carry an explicit `ack_for` (verified from raw blobs, not via the tool under review), 92 tests pass, zero regressions. Blocking: `parse_json_list` is unguarded in `collect_my_acks`, so a malformed `ack_for` in the sweeping agent's **own** namespace crashes the sweep with an uncaught `JSONDecodeError` — exiting `1`, which collides with the documented "healthy but unacknowledged" status — and published messages are immutable, so it cannot be repaired without quarantine. No test reaches the changed branch.

## Wake #6 — 2026-08-20 (night tree)

**Card `20260820T144705Z-...-night-tree-card.md` DELIVERED**, ~10 h ahead of its
clock deadline. Handoff `20260820T151421Z-...-handoff.md`, artifact commit
`84d3624b` on `agent/claude_1`; deployed as `3f189cad` on
`agent/local_claude_1` + `main`. The owner-approved post-B5 tree is live in the
VM night-runner lane (PID 3658317 since 15:12:55Z): extension when |mean| is in
[floor, bar), otherwise session 3 vs the very-old resident `98628e98…` in a
fresh state+ledger with the process rebinding and continuing; owner morning
sheet published in either branch, gated on `lint_outbox.py`'s exit status and
never committed if rejected. 26 tree tests + 9 publish tests + 119 transport
tests green; six mutants killed; pre-patch control shows `origin/main`'s runner
records the verdict and stops. codex_1 reviews post-hoc (`20260820T150139Z` ack).

**Changed rather than flagged:** the winner bar depends on the block size
(pre-registered 1.315 at n=5, 0.930 at n=10) and the runner had it as a
constant — an extended block would have been graded against the 5-pair bar and
a true +1.0 reported as "between floor and bar" when at n=10 it is a WINNER.
`bar_for(n)` now carries both literals. Consequence: at n=10 the bar sits BELOW
the floor, so the band is empty and a second extension can never fire.

**INCIDENT 15:06:34Z — the unattended lane died and nobody knew.** Not my patch:
`origin/main`'s `git_publish` raised an uncaught `RuntimeError` when the A3
publish hit a non-fast-forward push (the coordinator had appended the composed-
comparison addendum to the SAME ledger) and its single `pull --rebase` retry
conflicted append-vs-append. Exit 1, half-finished rebase left in the working
tree, **no HALT block anywhere**, service dead ~10 minutes. `Restart=on-abnormal`
was right not to restart it. **No double-submission exposure** — one traceback,
six submissions, no duplicate id, verified before touching anything. Recovered
keeping both sides in append order (`0e4953b4`). Hardened in the same delivery:
`merge=union` on both night-ledger names, three publish attempts with a rebase
between each, **any unsettleable rebase aborted** rather than left behind, and a
publish failure now HALTs fail-closed. Reproduced against real git with a
control that conflicts without the union driver.

**Live pattern, another instance:** a green guard that cannot see what it covers
— the sentinel/health story said the lane was HEALTHY while the lane was dead.
The crash was found by walking into it at deploy time, not by any check.

**Night tree ACCEPTED_WITH_EVIDENCE_CORRECTION** by codex_1 (`20260820T152133Z`):
handoff delivery validates, 26/26 + 9/9 reproduced in a detached worktree, tree
accepted. The correction was mine to own and it was right: `mutation_control.py`'s
part-1 pre-patch control read `origin/main:cgauto/night_runner.py`, so the instant
the patch landed on `main` the "control" loaded the *patched* runner and exercised
the session-3 path instead of demonstrating the old stop. It was unreplayable for
any reviewer. Repaired in `c8d69b14` and delivered at `20260820T152959Z`: pinned
blob `92264bead9f02a23226baedf90296fe5f301d563` (`3f189cad^`, == `966d0aff`) read
via `git cat-file blob`, a wrong-pin guard that fails loudly if the blob carries
any patch marker or equals the deployed runner, and `TemporaryDirectory` so no
synthetic files survive. Re-run: control holds, 6/6 mutants KILLED, suites green.
**Another instance of the live pattern, and the sharpest one yet — my own
anti-decorative-check script was itself decorative after deploy. A control that
reads a moving ref is not a control; pin a blob.**

**Pair-selector Phase 1 ACCEPTED** by codex_1 (`20260820T144531Z` ack,
`20260820T144532Z` review handoff): all central counts independently reproduced
(2,245 benched-with-work turns, 1,435/810 split, 2,010 deadlocks). P1+P2 routed
to the OWNER'S design gate; **no Phase 2 build is authorized** until the owner
chooses a design and the settled resident is pinned. 235 non-deadlock turns
remain explicitly out of scope. Nothing owed by me there.

## Wake #8 — 2026-08-20T15:40Z (queue drain, nothing owed)

Launcher woke me; queue held **one** message and it was terminal.

- **codex_1 `20260820T153828Z-...-door1b-ack.md` — night-tree control repair ACCEPTED.**
  `requires_ack: false`, so **no reply is owed and none was published**: an ack of an ack is an
  inert message and the transport rules forbid publishing one. Read, acted on (recorded here),
  `--mark`ed as its own step.
- The verdict on the night tree moves **`ACCEPTED_WITH_EVIDENCE_CORRECTION` → `ACCEPTED`**.
  codex_1 replayed `c8d69b14` from a clean detached checkout: the pinned blob
  `92264bea` is genuinely pre-tree and shows `BLOCK COMPLETE` with no extension/session 3,
  **6/6 mutants killed**, runner restored byte-exact, **26/26** tree tests, **9/9** publish tests.
  The moving-`origin/main` control defect and the temp-file leak are **closed**. Deployed scope
  unchanged; **no KEEP/REVERT ruling and no authority beyond the carded submissions is implied.**
- Sweep after mark: **0 new / 0 unacked / 0 delivery errors / 0 immutable-path collisions**;
  12 quarantined, all pre-existing and adjudicated.
- **Nothing was postponed this wake, so no new `DEFERRED:` card is owed.** Standing deferrals are
  unchanged: card 2 (sentinel build) still blocked on the one `actionable_set()` extraction
  ruling, on its published replacement; card 3 pair-selector Phase 2 blocked behind the OWNER'S
  design gate on P1+P2 and the settled resident.
- Health, checked not assumed: night-runner **PID 3658317 still alive** — the same process
  deployed at 15:12:55Z, so no restart and no repeat of the 15:06Z crash. VM disk now
  **95% / 1.1G free** (was 98% / 541M); still unowned, still flagged not claimed.

## Wake #16 — 2026-08-21T05:30Z (card 2 DELIVERED; a new card 4 deferred; one blocker raised)

Queue held **three** messages. Two were terminal (`requires_ack: false`), one was a new CARD.

- **codex_1 `20260821T051440Z` — the `actionable_set()` extraction ACCEPTED at exact `5ad46cbb`**
  (123 tests replayed in an isolated detached worktree). No ack owed and none published. This
  **discharged the single ruling card 2 was blocked on**, so card 2 became my live item and I built it.
- **local_claude_1 `20260821T051241Z` — 4b package, `to: user`.** Read, no action owed; the
  champion beats cure C on the frozen cases 8 FIXED to 3, and OSC-031 is still NOT FIXED (the
  benching, not the chop). Recorded, not acted on.
- **local_claude_1 `20260821T051959Z` — CARD 4, the OSC-032/033 no-goal instrument.** Landed
  mid-ritual; **DEFERRED** with a live self-addressed replacement (`20260821T053050Z`), my first
  item next wake.

### Card 2 delivered — `scripts/sentinel.py` + `docs/sentinel.md` at `f538bd3c` (doc repair `ec02a55b`)

Handoff `20260821T053024Z` to codex_1. **138 tests pass** (123 his + 15 new); **5 mutants run,
5 killed**. The predicate is `inbox_sweep.actionable_set()` and nothing else, asserted against a
live sweep rather than trusted at the call site. Controls fire both ways, including the one I rate
hardest — **mail for a DIFFERENT agent keeps it hanging** — and the git verb set of a whole run is
recorded by a PATH shim, not asserted in prose.

The fifth mutant **survived my first attempt**: a wall-clock break-heal-break test cannot separate
"the counter reset" from "the second failure never landed". Replaced with an in-process scripted
fetch-outcome list, which kills it. A control that cannot fail is not a control.

**Gate zero re-verified live this wake, not cited:** a real sentinel ran as a harness-tracked
background task against the true origin, hung through four fetches of nine remote refs, exited 2 at
the keepalive and removed its pidfile — and that exit re-invoked this session. Gate 1 stays
**MIXED** (Codex harness falsified); `nohup`/`setsid`/systemd shapes remain **unverified**; no
harness is proven to *notice*. Ruling requested on one widening: a `SweepFailure` is counted on the
same budget as a fetch failure, so exit 3 means N consecutive fetch-**or-sweep** failures.

### BLOCKER raised — the deferral queue anchor is inert (`20260821T053322Z`)

Measured, not inferred: `inbox_sweep` builds `addressed` with `m.sender != me`, so a self-addressed
`DEFERRED:` card is authoritative on origin, `requires_ack: true`, unacked — and **absent from its
own owner's `actionable_paths`**. My "queue drained" notes at wakes #13 and #14 were honest and the
sweep agreed with them while two cards were live; that agreement IS the defect. The sentinel
inherits it (charter element 3 never fires) and I did **not** patch it there — a second predicate is
what codex_1's boundary forbids. `docs/sentinel.md` states the gap in place. No patch proposed
inside someone else's rule; the narrow question is the rule owner's.

**Standing cards:** card 2 **DELIVERED**, awaiting review · card 3 closed, no replacement · **card 4
the only live DEFERRED**, carried by this file and by `20260821T053322Z`, because by measurement the
queue will not carry it.

**Pre-existing and NOT mine:** `tests/test_doc_budgets.py` fails on `docs/STATE.md` (171 lines,
budget 150); that file last moved 2026-08-14 and nothing this wake touches it.

## Owed, now unparked by r4

M1 Decision Packet implementation (spec frozen against `98628e98`) · M3b adjudication (needs M1 + valid M3a) · P4 re-do on c5 evidence · D-4 repair · gate revision 3 execution review. **With the owner:** the D89a label; whether to fund a fresh 512-row corpus for U4.

## Do not cite

**My idle-blocker claims are `UNREPLICATED / UNRESOLVED`** (`codex_1`, `20260809T190604Z`, accepted
by me in full). The terminal population of **20 episodes** on subject `98628e98` IS independently
reproduced and may be cited. **Claims 1 (all 20 have an `IDLE` blocker) and 2 (no working-blocker
episode reaches 62 turns) are not** — the base panel carries no per-turn states, so they are
unresolvable from any evidence outside my own library. **The merged repair plan's mover-only
rationale rests on claim 2 and must carry that label wherever cited.** Repair proposed and awaiting
the coordinator's sequencing: commit raw `98628e98` transcripts as a non-library artifact. The
lesson is mine — committing my extraction is not committing the evidence it came from.

The `+12.453/+76.508` D89a split (`UNRESOLVED`, TSVs never committed) · `oscillation-library/` as M3a (it is parent lineage `a8eb3b2b`) · D-9 as `INAPPLICABLE` or "196 false positives" (now `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`) · D-6 as falsified (it is a `CONTRACT AUTHORITY: CONFLICT`) · any floor figure for the ~10 of 17 rules lacking a corpus witness.

## Transport

**Dual-format MANDATORY** (v2 front matter + legacy `- To:` bullets) — a peer was blind to v2 for ten days. **Gate publishes on `lint_outbox.py` EXIT STATUS**, not on grepping its output. Push before citing: *unpushed is unsent*, and a stale remote-tracking ref makes `git merge` a silent no-op. Never `git add -A` — agents share this tree.

**`ack_for` is no longer inert on non-`ack` kinds** (changed 2026-08-12, `f9fc1810`). It used to count only on `type: ack` — I broke that 4x — and now any kind may discharge by naming exact paths. `ack` must still carry a non-empty `ack_for`. **Prefer a separate `ack` anyway:** a busy handoff acking four questions in its front matter is easy for a reader to miss.

**`pytest` is absent from the host but the transport suite requires it** — `tests/test_inbox_sweep.py` does `import pytest`, so `python3 -m unittest` cannot run it. Use `uvx pytest tests/…` (92 pass). The old "use `python3 -m unittest`" guidance holds only for suites that do not import pytest.

**Tooling: `inbox_sweep.py` `7952be44…`, `lint_outbox.py` `40b71c4c…`, both matching `main` as of wake #14** (they were `be8251c4…`/`f3c47b70…` through wake #13; both moved under me). `lint_outbox.py` had been **absent from this branch entirely** — the publish gate did not exist where I was publishing from, which is the mechanical cause of all three of my quarantined messages.

**Verify your tool digest against `origin/main` before trusting any sweep — every time, not once.** I went stale twice in one cycle: first at `12b27e9c…`, which reported **56** unacknowledged against the true **16** and printed no quarantine section at all; then again the same day when `main` moved to `be8251c4…` under me, so a handoff I had genuinely acknowledged still showed as outstanding. Nothing on screen announces a stale tool. Re-check after every `main` movement.

**Three of my messages are quarantined** (`20260807T090000Z` non-canonical type, `20260807T113000Z` correction with empty `supersedes`, `20260811T163000Z` handoff pinning a commit lacking two of its own paths). All rejected on transport, not substance; all have verified replacements; no content lost.

**Roster blocker (`20260812T193500Z`) — RAISED AND CLOSED.** The roster naming `codex_1` sat only on
`origin/session-2026-07-01` while both `roster.json`'s own note and `inbox_sweep.py`
(`ROSTER_REF = refs/remotes/origin/main`) treat `main` as the sole authoritative location. Upheld in
full by `local_claude_1`, which reproduced it and fast-forwarded `cff2398c..db0574cf`. Verified:
`origin/main:coordination/roster.json` now carries `unreachable: [chatgpt_1, chatgpt_2]` and
`dormant: [local_codex_1]`. Coordination commits now go to both refs in one action.

**Live pattern to watch — state reaching a ref ahead of the process governing it.** Four instances
this cycle: task records committed but unpushed; the roster on an unread ref; a withdrawal stated in
an `ack`, which carries no `supersedes` and so retires nothing; and `f9fc1810`, whose own commit
subject says *PENDING REVIEW*, already an ancestor of `origin/main`. *Integrated* and *accepted*
are not the same event.

**Watermark deliberately NOT advanced.** 141 messages remain `new (unseen)`. Protocol forbids blanket-marking a backlog by timestamp: actionable messages are acknowledged by exact path (done — 16 of 16, sweep exit 0), and the rest need a pushed legacy-backlog audit before `--mark`. That audit is outstanding.

## Standing constraints

Arena controller: **NO**. `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`) byte-untouchable; `engine.rs` (`7c240abf`) is the authority, not any bot's self-restraint. `trace_detectors.py` is `local_claude_1`'s. No CI anywhere.

## Wake #22 (2026-08-21) — cause-attribution G-1 delivered; a premise in the card refuted

- **Card taken and answered at G-1.** `20260821-osc032-033-cause-attribution` (chartered 07:32:56Z
  at the owner's request). Delivered the instrument package at `20260821T075136Z`, artifacts at
  `eb697462`. **G-2 and G-3 are NOT claimed** — the card puts codex_1's instrument review first
  and I held to it. codex_1 had already ACKed the reviewer duty at 07:43:18Z noting no package
  was published yet; it is published now.
- **What was built.** The clause tap: 7 new anchors on a NEW subject `door1-clause`, so the
  predecessor's accepted `door1-champion` probe and both manifests still reproduce
  byte-identically (observed via `git status` on every build). All 14 anchors match exactly once.
  Every edit splits an `a||b` guard into its named halves or turns one iterator chain into the
  same loop — no predicate added, removed, weakened or reordered. Nine fail-closed gates, all
  green, including the cross-check against the ACCEPTED route probe's `chops=` and a referee/bot
  agreement gate (249 + 358 rows, 0 mismatches) that licenses joining the oracle to the clauses.
- **The control the first run forced.** Across both fixtures, on all 607 tapped calls, the tap
  emitted **zero rejection rows** — so the card's both-ways control tests only the ACCEPTED
  direction, and a constant-ACCEPTED tap would look identical. Added `clause_control.py`: same
  probe binary over all 34 situations, parity re-checked on each; the runner refuses to attribute
  a cause without it. Reject side observed firing (`PREDICT_TREE_NONE` ×103, `NO_FRUITS` ×425,
  `FN_NO_HARVEST_POWER` ×991, `FN_NO_CHOP_POWER` ×1091, `OPPONENT_EMPTY_HANDED_ON_CELL` ×77).
  **Eleven clauses were never observed firing anywhere in the corpus and are recorded as
  UNOBSERVED, not as exercised** — gating on all sixteen would gate the corpus, not the tap.
- **A premise in the card is refuted, and I did NOT act on it.** The card's THE QUESTION says the
  eligible-action oracle reported legal work every window turn. `oracle.py`, under the agreement
  gate, returns the **empty set** 110/110 and 143/143 — `view.plants` is empty there (OSC-032 has
  a plant on turns 1-81 only, OSC-033 on 1-12 only; the windows open at 91 and 58). The claim
  traces to the fixture's P4 record wording, *"work remains … [RAW liveness: every stall window
  over a non-terminal world blocks]"*, which is a different predicate — `oracle.py` exists because
  the earlier work-oracle conflated exactly these two. Raised to local_claude_1 at G-1 because it
  bears on what G-3 should be asked; **no hypothesis marked, no cause attributed, no judgment on
  the fixtures' classification.**
- **Queue drained.** Four more messages arrived mid-wake, all `requires_ack: false` acks/rulings.
  Acked the deferral-rule ruling (`policy` is in `ACK_REQUIRED_KINDS`, so a policy cannot opt out
  by front matter — named once, no change requested). **TOOL DRIFT has CLEARED**: local_claude_1
  ruled option 1 and merged `agent/claude_1` to `main`, so the instrument is untouched and the
  red line is gone. Transport suites 145/145 on this tree.

## wake #27 — 2026-08-21 ~09:50Z — real-end re-grade DELIVERED; cure α G-0 DELIVERED, G-1..G-4 deferred

- **Queue.** Two cards arrived and a third message set landed mid-wake. Both cards are
  acked and delivered in this wake: `20260821-p4-stalls-real-end-regrade` (all four
  deliverables) and `20260821-swap-r1-cure` G-0 (design note, no code). Nothing outstanding
  except G-1..G-4, which carry a DEFERRED replacement card gate-blocked on codex_1's ruling.
- **The re-grade answer: none of the 34 recorded windows is artifact.** Not one turn. On the
  bot that produced them, 18 of 34 games never reach `has_stalled` inside the 200-turn horizon,
  and the other 16 end +3 to +46 turns AFTER their window closes (tightest OSC-009, +3). Zero
  wholly artifact, zero partly. OSC-031's window is real end to end; OSC-034's game ends 16
  turns after its window closes.
- **The finding that produced it, and it corrects my own G-3 from this morning.** The card's
  premise — "on the champion re-run" — re-runs a bot that did NOT record the windows. The
  library's provenance names its subject as `98628e98…`; the champion is `547fa706…`. Two arms:
  the subject reproduces **34/34** recorded episodes, the champion **11/34**. OSC-032/033 are
  among the 23 it does not: their window commands are all `WAIT` so a command comparison passes,
  but at OSC-032's window entry the frozen board still carries a live PLUM while the champion's
  replay has been bare since turn 82. **The G-3 numbers are right about the champion's game and
  wrong to be identified with the recorded windows** — the cross-game figure error, mine, from
  four hours earlier. Put to the owner as a question; no re-ruling proposed.
- **The gate that caught it, and the gate that did not.** Window-command identity alone is an
  inert check on an all-`WAIT` window — it passed OSC-032/033 while the boards differed. The
  frozen `world_state_at_entry` comparison is what fires. The run now REQUIRES the pair to
  accept 34/34 on the subject arm and reject ≥1 on the champion arm, so neither can go quiet.
- **Adapter reuse.** G-3's `to_sim_state` / `check_adapter_fidelity` / `stall_negative_control`
  imported unmodified, digest in the artifact. One declared delta: G-3's per-fixture non-vacuity
  raise lifted to the corpus, because "never ends inside the horizon" is the correct answer on 18
  of 34 and a per-fixture raise would make it unreportable.
- **Cure α G-0.** Design only, per the card — the seam is `resolve_move_conflicts_*` line 720 and
  nothing else. Four decisions put to codex_1 rather than built: T4(a) swap-before-detour (the
  one place α changes a non-`WAIT` outcome), the partner's forbidden-cell test, the fail-closed
  positional index map (`commands` carries no unit id for `WAIT`), and where the re-swap detector
  belongs. G-1 will fail if the corpus-wide trigger count is zero — an α that never fires would
  pass a byte-identical parity check perfectly.
- **Offered, not claimed.** `sweep34`'s grader re-detects on the candidate's own trace (sound) but
  takes its region of interest from the recorded window, which on 23 fixtures is not an interval
  of the game being graded. Not measured, not asserted; flagged because it touches cure α's G-2.

## 2026-08-21T10:05Z — wake #28 (claude_1)

- **Queue: 2 messages, both from codex_1, both drained.**
- **`20260821-p4-stalls-real-end-regrade` — ACCEPTED and CLOSED.** codex_1 re-ran
  `claude_1/regrade1/real_end_regrade.py` from detached commit `4502c655` and reproduced the
  delivered artifact exactly on every decision-relevant number: subject identity 34/34, champion
  identity 11/34, subject `REAL_THROUGHOUT` 34/34 with zero artifact windows, champion
  `REPLAY_MISMATCH` 23/34 including OSC-032/033, and all four constructed predicate controls plus
  corpus non-vacuity. G-1, G-2 and G-3 all ACCEPTED; the declared corpus-level non-vacuity delta
  was ruled appropriate because a per-fixture raise would reject the valid answer "never stalls".
  The two-part episode identity gate was ruled necessary and non-vacuous — command identity alone
  genuinely accepts the all-`WAIT` OSC-032/033 windows, and only frozen entry-board identity
  rejects the champion's different games. Q1 (whether the cross-game premise re-rules anything)
  stays with the owner through the coordinator; my `sweep34` borrowed-region-of-interest
  observation is explicitly **not** validated by this review and needs its own charter if pursued.
- **`20260821-swap-r1-cure` G-0 — REVISION_REQUIRED, revised and resubmitted the same wake.**
  One blocking finding, G0-1, and it is correct: the emission inserted `m.cell` into `reserved`
  without first requiring it to be free. `m.cell` is not reserved at initialisation because `m`
  is itself a mover, so an **earlier accepted mover** in the same sorted pass can already hold it
  — and the insert is idempotent, so it would have detected nothing. The engine's id tie-break
  would then discard one half of the exchange while the emitted stream still read as a swap.
  Closed as pre-fire conjunct **T2b** (`!reserved.contains(&m.cell)`), declining to fire rather
  than repairing, with the note stating why it is not subsumed by the existing third-mover guard:
  that one protects against a *later* mover **after** the fire, T2b against an *earlier* one
  **before** it. A focused G-1 control (prior mover holding `m.cell`; α must decline and emit a
  byte-identical stream) is required so T2b is not an untested branch.
- **The four rulings, all decided, now recorded as binding.** T4(a) before detour ACCEPTED —
  broader trigger stays, and G-1 now reports T4(a)-with-detour-available fires separately so its
  breadth is a number. Partner forbidden-cell test ACCEPTED per-participant, not a blanket
  stand-down. Fail-closed positional map ACCEPTED plus a new precondition: command count must
  equal own-unit count before the map is built. Re-swap detector ruled **G-1**, blocking before
  panel work.
- **Still no code.** `cgauto/submissions/candidate-swap-r1.rs` does not exist; the build begins
  only on G-0 rev 2 acceptance. The `DEFERRED: cure alpha G-1..G-4` card from the rev-1 handoff
  remains in force and, per codex_1's ruling, is not duplicated.
- Artifact: `claude_1/swap1/g0-design-swap-r1-2026-08-21.md` @ `9e483d84`.

## Wake #32 — 2026-08-21 ~11:45–12:00Z — both queued cards discharged, one delivered, one blocked

- **Queue: 3 unseen messages (2 receipt-only acks + codex_1's P4 review), plus my own two
  self-addressed DEFERRED cards. Both cards acted on this wake.**
- **`20260821-corpus-prevalence` — BLOCKED, returned with the blocker measured.**
  `claude_1/prevalence1/corpus-prevalence-blocked-2026-08-21.md` + `corpus-availability-…json`
  @ `609f7a2a`, handoff `20260821T114540Z`. The card-named `data/processed/games.jsonl` (9,082
  records) and `data/processed/trajectories/` are absent and were never tracked; the bulk backend
  is unmounted (`check_external_storage.py --intent read` → FAIL); and the resident of record
  `6561795` has **0 games** in the 290 tracked raw games. Our lineage there is `6536563` (140) and
  `6536359` (1) — older, so a table built from it would answer a different question under the same
  title. I did **not** run `data/scripts/parse.py` (it would overwrite the tracked 15,291-game
  `stats.json`), did not loosen the storage check, and did not pass off the six `waste_sweep`
  detectors as this card's answer.
  - **I corrected my own prior ack**, which had asserted `games.jsonl` was present without looking.
  - Scoping finding that outlives the storage problem: **both** D-1 and P4 need a replay→`Trace`
    adapter that does not exist. codex_1's precision correction on P4 was **checked and accepted**
    — `eval_p4` documents `post_state=None`, so "not applicable to a replay as accepted" was
    withdrawn; the standing ruling is *exact accepted P4 unestablished pending an adapter/parity
    test; the reduced column only if relabelled and authorized*. Recorded in the artifact at
    `3101da6e`, acked at `20260821T…-p4-correction-ack`.
  - The DEFERRED card stays live and blocked; it is the one open ack in my sweep, deliberately.
- **`20260820-pair-selector-anti-benching` Phase 3a — DELIVERED.**
  `claude_1/picker3/phase3a-diagnosis-2026-08-21.md` + probe/analysis + raw rows @ `ea0a5154`,
  handoff `…-phase3a-handoff`. **The two named panel findings have opposite signs:**
  - `m004` s0 — P1's veto is causal on **4** turns (42–45) and the surviving pair is real work
    every time. Candidate: **D-1 ×1, no P4**. Floor on the identical spec: **D-1 ×2, P4 42–200**.
    The "P3 regression" is P1 **removing the champion's own 159-turn stall**; only byte-equality
    with the parent got worse, which is all P3 measures.
  - `m021` s1 — the veto fires on **103/200** turns and on **80 contiguous** ones (20–99) removes
    the highest-scoring pair, leaving a pair scoring **0.0 — both units WAIT**, inside the recorded
    P4 window 20–106. The floor has neither the P4 nor `r5-horizon`. **A real, quantified harm
    from P1 as written**, identical on both bases.
  - Gates: parity, **row identity against the Phase-2 panel record** (both matched), 200/200 turn
    coverage, causal-veto discipline (inert vetoes 23 and 6 excluded, not folded in), parent
    control read directly rather than inferred. `run_gates.py` untouched.
  - Three questions handed back unanswered: P1's veto has no fallback; the `idle_regeneration`
    fallback replaces rather than extends `out` (the 101/170 collision); P3's applicability to an
    intentional selector change — now shown firing on a change that removes a stall.
  - Carried correction: **OSC-013/017 reproduce on the champion, OSC-004/034 do not** — reported
    `NOT_REPRODUCIBLE_ON_BASE`, no exhibit, not fixed, not absent.
- **New this wake:** `claude_1/picker3/panel_game_probe.py` reaches **panel games** (not just
  library fixtures) by reusing `fuzz_panel`'s own `build_jobs`/`make_referee`/`run_pair` with the
  accepted selector probe. That is the instrument any later panel-game diagnosis should reuse.

## WAKE #34 (2026-08-21T12:41Z) — the cure is BLOCKED AT G-1 by review; nothing new authorized

- **`20260821-swap-r1-cure` — reviewer verdict in, and it is a block.** codex_1's
  `20260821T123322Z` ack returns **`PACKAGE_REPRODUCED; BLOCKED AT G-1`**: all 16 declared
  artifacts fetched at `65c716b3`, independent execution reproduces the package including the
  byte-identical G-2 JSON. The **13 residual OSC-011 re-swaps fail the strict fail-first G-1
  condition**; the construction ruling required them measured, it did not waive the gate. The
  amended population result (D-1 +18, P4 +16 healed-minus-new, zero new) is **accepted and
  strongly positive but cannot advance a G-1-failing candidate to G-3**. **No G-3 work is
  authorized and I started none.**
  - Planner-target widening stays **owner-blocked**; do not broaden.
  - P5's deletion of the CHOP/HARVEST working-partner exchange stays a **named scope cost**.
  - P3 on this task is a **named signal only** — the single m004 seat-0 occurrence is explained by
    the intended alpha exchange and the floor's zero is a vacuous column. Explicitly **no general
    exemption**; the anti-benching card's owner-upheld P3-clean rule is unchanged.
  - Baskets: the reviewer agrees the identity predicate belongs on the subject/base arm and
    proposes proving subject identity then grading the cure arm for absence of the same shape.
    That is a **coordinator/owner gate amendment, not mine to enact**. OSC-005 remains a
    substantive miss because alpha fires after its episode.
  - The ack required none back; two DEFERRED cards it carries (planner-target widening / alpha
    replacement, anti-benching Phase 3b pre-build ruling) are **codex_1's queue items, not mine**.
- **`20260821-corpus-prevalence` — still BLOCKED, re-measured not recalled.** Ack published at
  `20260821T124100Z`. This wake: `check_external_storage.py --intent read` → `storage preflight:
  FAIL` (no `medium_data` label, no `troll-farm-data:archive` mount); `artifacts`, `outputs`,
  `data/external` absent; `data/processed/` holds only `corpus_manifest.json`,
  `parse_failures.json`, `stats.json` — `games.jsonl` and `trajectories/` both absent. No ruling
  on the authoritative-corpus question has reached my queue. Card stays parked, nothing started,
  nothing degrading. The DEFERRED card is again the one open ack in my sweep, deliberately.
- **Nothing else was built this wake.** With G-1 blocked and the prevalence card blocked, there is
  no authorized work left in my queue; inventing some would be the failure mode this programme has
  been correcting all week.
