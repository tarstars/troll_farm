# 20260824-real-game-dance-attribution — WHY do the dances that survive in real games happen?

- Status: **DELIVERED 2026-08-24T18:15Z — all three steps, both passes.** G-1
  `DEFINITIONS_ACCEPTED` (codex_1 `20260824T172730Z`, r3 `agent/claude_1@7405b779`); G-2
  `EXECUTION_ACCEPTED` (codex_1 `20260824T175604Z`, fresh archive of `d75cb2f0`, byte-identical,
  six controls K0–K5); G-3 brief `agent/claude_1@4c92432f`, integrated as
  `local_claude_1/dance-attribution-owner-brief-2026-08-24.md`, receipt `20260824T181500Z`.
  Result: 462 episodes with facts and a class; 42 % / 38 % a *working* teammate parked on a plant
  beside the dance; the library's idle-blocker shape **0 of 80** in real instrument games;
  `NO_TARGET` empty; class 3 renamed `POSITIONAL_EXCHANGE` (K3 negative side fired 3,256 times on
  the July bot — R-1's premise unverified for that lineage). One owner question carried in the
  brief; nothing chartered against it. Original status follows.
- Status at charter: **OPEN — CHARTERED 2026-08-24 by owner instruction** (owner, in the coordinator
  session 2026-08-24 ~15:50Z: *"do it"*, in reply to the proposal "charter a champion grading run
  and a cause classification of the 22 episodes". This authorization exists in the repository
  only as the coordinator's transcription; if the owner reads it back differently, the charter
  is withdrawn.) **Coordinator's half DELIVERED 2026-08-24T16:28Z**
  (`20260824T162800Z-…-policy.md`): the champion dances in **16.80 %** of its real 2-troll games,
  the very-old bot in 17.37 %, cure C 16.85 %, the instrument 14.57 % (n.s.); same-ladder A/B
  door 1 vs very-old **+0.00 pts over 2,268 games**. The swap-R-1-as-origin hypothesis is
  **refuted**; the **second pass is TRIGGERED** (382 champion episodes / 306 games shipped).
- Record owner: local_claude_1 · Work owner: **claude_1** (instrument + classification) ·
  Reviewer: **codex_1** (definitions-first, then execution) · Integrator: local_claude_1
- Area: the dance ("oscillation") question, real-game branch. Successor to the 08-23 G1 grading
  (`local_claude_1/narrate/g1-first-grading-2026-08-23.json`), which COUNTED the surviving dances
  and did not explain one of them.
- Base commit (inputs): `agent/local_claude_1` @ `3256dafb164dc17417ddb84e00909157f5eb763a`;
  claude_1's own instruments at `agent/claude_1` @ `7b623b1bbcfd4acc7205fa6214878c5ecbcf912a`.
- Branch: agent/claude_1 (work), agent/codex_1 (review), agent/local_claude_1 (record)
- Progress lease: 15 minutes without concrete evidence inside a session (phase markers renew it);
  an agent asleep between wakes is not stalled (§5.1).
- Created UTC: 2026-08-24T16:03:00Z
- Last updated UTC: 2026-08-24T17:20:00Z

## THE QUESTION (owner's, plain words)

We spent weeks on why a troll "dances" — steps back and forth between two cells without doing
anything. On fixtures the answer was: one of *our own* trolls is in the way, usually standing
idle, and the movement resolver never issues the swap that would end it. Then we measured real
ladder games (2026-08-23): trolls blocking each other happens **0 times in 469 games**, yet
dancing still happens in **about 11 % of games** — 22 episodes in 17 of the first 149, replicated
on the second batch. Those 22 are counted and nothing more. **What was each dancing troll doing,
what did it want, what was in its way, and what ended the dance?** In particular, is it the old
dance (an own troll in the way), a goal that flips every turn, the instrument's own swap rule
re-swapping, something the opponent does, or something new?

Two facts make this answerable now when it was not on fixtures: every game here carries the
troll's **stated intention each turn** (the NARRATE telemetry, v2: the chosen target; v3: also the
best candidate the picker discarded), and the games are real, not hand-picked stress maps.

A caution the record already carries and that must travel with every number: **D-1 off replays is
an upper bound** — plant clocks are reconstructed and the error direction *invents* dancing.

## Inputs (all pinned, all read-only)

- **Batch 1** — 149 replays, agent `6652424` (instrument v2 = swap R-1 + telemetry):
  `local_claude_1/narrate/games/*.json.gz` @ `3256dafb`. The 08-23 grading of exactly these:
  D-1 **22 episodes in 17 games**, D-2 0, D-3 0 (`g1-first-grading-2026-08-23.json`).
- **Batch 2** — 160 games, agent `6652602` (v2):
  `local_claude_1/narrate/read2/games-agent6652602-submission41182352.jsonl.gz` @ `3256dafb`
  (the 08-23 replication: "dancing 11 % replicates exactly").
- **Batch 3** — 160 games, agent `6652642` (v3, carries `available` beside `chosen`):
  `local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz` @ `3256dafb`.
  Its D-1 grading is not in the record; grade it here.
- Instrument sources, for the swap rule's exact shape: `local_claude_1/narrate/instrument-swap-r1-narrate-v2-SUBMITTED-2026-08-23.rs`
  (sha256 `aaebc503…`) and `…-v3-SUBMITTED-2026-08-23.rs` (sha256 `9a3e8758…`).
- claude_1's accepted instruments (its own branch): the replay→`Trace` adapter
  `claude_1/adapter1/replay_to_trace.py` (G-1 ACCEPTED), the detectors
  `claude_1/banana-restoration-r2/trace_detectors.py` (`detect_d1`), the v2 decoder
  `claude_1/narrate1/narrate_decode.py`, the v3 grammar `claude_1/narrate3/`, the library's
  blocker criterion and mechanism labels `claude_1/banana-restoration-r2/build_oscillation_library.py`
  (`classify`, lines ~241–302; blocker/idle criterion ~57–61 and ~185–238), and the frozen
  library `claude_1/banana-restoration-r2/oscillation-library-98628e98/library/` (38 D-1 episodes
  with M1/M2/M3 labels) as a classifier control.
- Known swap turns, for the swap-tick control: the 9 `MANUFACTURED` / `swap` rows in
  `claude_1/narrate2/results/idle-adjudication-2026-08-23.json` (game, turn, unit).
- A corpus whose bot never swaps, for the swap-tick negative control: the 290 git-tracked
  replays under `data/raw/games/` (agents `6536563` / `6536359`, pre-cure; the very-old bot
  "never generates swaps, self-imposed" — `docs/RULES-LEDGER.md` R-1).

## Deliverable — a fact table per episode, then a class, then a tally, then plain words

**Step 0 — grade.** Run the unmodified adapter + `detect_d1` over all three batches, own seat
resolved from the replay's `agents` array by agent id (never a listing position). Every episode
(game, seat, unit, `turn_start`, `turn_end`, `k`, cells) is a row. Batch 1 must reproduce
**22 / 17** exactly (control K1) before anything else is believed.

**Step 1 — facts per episode, all observable, none judged:**

- F1 the dancer: unit id, speed / capacity / harvest power / chop power, carry at entry and exit.
- F2 the two cells, window length, `k`, turn of entry and exit.
- F3 every other own unit alive in the window: distinct cells, wait fraction, orthogonal
  adjacency to either dance cell, plant on its cell at entry, working verbs it emitted — using
  the library's blocker / IDLE criterion **verbatim** (wait fraction ≥ 0.95 and one distinct cell;
  a blocker holds one cell orthogonally adjacent to a dance cell for the whole window).
- F4 telemetry: the dancer's `chosen` target per window turn (v2 and v3) and `available` (v3
  only); summarised as CONSTANT / ALTERNATING (the distinct targets and their period) / NONE /
  MIXED, with the raw sequence kept in the row.
- F5 swap ticks: every turn `t` in `[turn_start − 2, turn_end]` on which two own units exchange
  cells in one tick (`u: a→b` and `v: b→a` between consecutive states). Count and list, whether or
  not the dancer is one of the two. Observable from positions — no probe.
- F6 opponents: per window turn, any opponent unit on either dance cell, on the dancer's target
  cell, or orthogonally adjacent to the dancer; the count of such turns.
- F7 how it ended: the first event after the window — progress type (carry change /
  inventory change on the dancer's DROP or PICK / plant created or removed at its cell), a peer
  moving off, a swap, unit death, or game end.

**Step 2 — class, by precedence, first match wins; exhaustive and disjoint; published BEFORE
counting (gate G-1):**

1. `SWAP_FLAP` — at least one F5 swap tick involving the dancer.
2. `BLOCKED_BY_IDLE_TEAMMATE` — F3 names a blocker that is IDLE; sub-tag `ON_PLANT` /
   `NOT_ON_PLANT` (the library's M2 and idle-M1 shapes).
3. `BLOCKED_BY_WORKING_TEAMMATE` — F3 names a blocker that is working (library working-M1).
4. `GOAL_FLIP` — no blocker; F4 is ALTERNATING between two or more real targets.
5. `FIXED_TARGET_NO_BLOCKER` — no blocker; F4 CONSTANT; sub-tag `OPPONENT_ON_TARGET` when an
   opponent stands on the target cell for at least half the window.
6. `NO_TARGET` — F4 NONE throughout (a want the v2 instrument cannot see; in batch 3 use
   `available` before assigning this class).
7. `UNCLASSIFIED` — facts published, no class asserted.

**Champion pass (ruled by the record owner 2026-08-24T17:20Z, closing codex_1's r2 blocker):**
the champion package carries no telemetry, so its precedence is the r2 ordering of classes 1–3
and then **every remaining row is `NO_TELEMETRY`** — there is no `UNCLASSIFIED` on the champion
pass; the telemetry-only classes appear in the champion column as `n/a (no telemetry)`, never as
zero; the mechanism layer `mech` is carried on every row of both passes and is the exact
cross-corpus comparison. codex_1's two `REVISION_REQUIRED` rulings (r1 16:24Z, r2 16:41Z) were
published as bare receipts and woke nobody — rulings must be `requires_ack: true` (§5.1).

Co-occurring conditions (a swap inside a blocked window, an opponent beside a goal flip) are
reported as facts on the row, never folded into a second class. A class that is empty is reported
as **empty**, never merged away. If the definitions turn out wrong on contact with the data, say so
in G-1's revision — do not bend a boundary after seeing the counts.

**Step 3 — tally and brief.** Counts per class per batch and pooled; episode lengths per class;
the share of episodes that end in progress versus game end; and an **owner brief in plain words**:
which classes carry the real-game dance, one number per claim, an explicit "not established"
section. **No bug-versus-correct-caution ruling** — that is the owner's, afterwards. No cure.

## Controls (each mandatory, each reported with its number; a vacuous pass is a failure)

- **K1 identity:** batch 1 → D-1 22 episodes / 17 games / D-2 0 / D-3 0, exactly.
- **K2 classifier reproduction:** the F3-based part of the classifier (classes 2–4) run over the
  frozen library's 38 D-1 episodes must reproduce the library's M1 / M2 / M3 labels; every
  disagreement listed with its reason. The classifier must therefore be a function of `Trace`
  facts so it runs on library transcripts and on replays alike.
- **K3 swap-tick detector:** fires on the 9 known manufactured-swap rows (game, turn, unit) and
  is silent over the 290 never-swapping replays (both seats). Report both counts.
- **K4 telemetry decode:** the v2 / v3 decoders' own panels re-run on the batches used; every
  refused game listed by reason; nothing partially decoded.
- **K5 exhaustiveness:** classes sum to the episode count per batch; each class exercised by a
  control or a real row, or reported EMPTY.
- Determinism: the final results file reproduced byte-for-byte on a second run.

## Gates (fail-first, in order)

1. **G-1 definitions review (codex_1), before any count is believed:** the fact list F1–F7, the
   class precedence, the verbatim reuse of the library's blocker criterion, and the swap-tick
   definition. codex_1 rules `DEFINITIONS_ACCEPTED` / `REVISION_REQUIRED`. One wake each.
2. **G-2 controls K1–K5** delivered with the run; codex_1 execution review from a fresh archive
   of claude_1's commit.
3. **G-3 the tally and the owner brief** (Step 3). Integrated by local_claude_1 into the dance
   record; the owner rules afterwards, if at all.

## Exclusive write set

- claude_1: `claude_1/dance1/**` (scripts, `results/*.json`, the report
  `claude_1/dance1/dance-attribution-report-2026-08-24.md`), `coordination/status/claude_1.md`,
  `coordination/messages/claude_1/**`.
- codex_1: `codex_1/reviews/**`, `coordination/status/codex_1.md`, `coordination/messages/codex_1/**`.
- local_claude_1: this record, `coordination/status/local_claude_1.md`, `docs/STATE.md` §4,
  `local_claude_1/dance-lineage/**` (see "Coming from the coordinator").

## Shared read-only paths

- Everything under "Inputs". The replay packages and instrument sources are frozen artifacts.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred, `fff6669b…`), `cgauto/submissions/*`,
  `data/raw/games/` and the 02:17 UTC cron, any other agent's namespace, the Arena
  (controller local_claude_1; no submission, no TestSession, no fetch of new games).

## Delivered from the coordinator — the second pass is triggered (2026-08-24T16:28Z)

The **champion of record** (door 1, `547fa706…`, NO swap rule) and the two bots before it were
graded on their own real ladder games (2026-08-18…08-23) with the unmodified adapter + `detect_d1`
on `project_host`: `local_claude_1/dance-lineage/lineage-grading-2026-08-24.md` + `results/*.json`
@ `agent/local_claude_1@6595935e` (four controls PASS, 46 pinned agent ids, 22/17/0/0 identity
exact). Result at two trolls: very-old 17.37 % of games, cure C 16.85 %, **door 1 16.80 %**,
instrument 14.57 % (n.s., p = 0.25); pre-cure July `v1.2.2-farmcap` 0 of 51 (but 43 % own-troll
contention). **Swap R-1 is not the origin of the dance.** The champion's **382 episodes in 306
games** are shipped sanitised at `local_claude_1/dance-lineage/door1-games/` @ `4b9bd563`
(package sha256 `57832fd9…`; every game reproduced its episodes through the adapter before
packaging; forbidden-key sweep 0; no battle index, no opponent submission id claimed).
**claude_1 classifies them with the same instrument in the second pass** — no telemetry there,
so classes 4–6 collapse to `NO_TELEMETRY` and are reported as such; classes 1–3 are computable
from positions. The deliverable of the second pass is the **comparison** of class distributions,
instrument (with intentions) beside champion (without). The first pass does not wait for it.

## Acceptance checks

- `python3 claude_1/dance1/run_dance_panel.py --help` exits 0; the panel run prints K1–K5 with
  their numbers and `PASS` only when every control fired.
- `claude_1/dance1/results/dance-episodes-2026-08-24.json` holds one row per episode with F1–F7
  and exactly one class; row count per batch equals `detect_d1` totals.
- The report's tally sums to the episode counts; every class present in the table appears in the
  tally, empty classes included.
- codex_1's G-1 and G-2 verdicts are published messages naming claude_1's commit.

## Arena authority

Read-only platform access: not needed. Platform mutation: forbidden. The Arena is untouched by
this task in every phase.

## Explicitly OUT of scope

- Any fix, cure, candidate, behaviour change, or harm/benefit judgment; any re-opening of the
  swap/yield chain (retired 2026-08-23) or the anti-benching chain (r2 rejected); any prevalence
  claim beyond these three batches; any statement about opponents' *reasons* (their bots carry
  no telemetry).

## Handoff

claude_1 → codex_1: G-1 definitions as a `handoff` (short: the F-list, the precedence, the
verbatim criterion citations) → codex_1 ruling → claude_1 build + run + G-2 controls as a
`handoff` naming the commit and the artifact paths → codex_1 execution review → local_claude_1
integrates and carries the brief to the owner.

Deferrals: none.
