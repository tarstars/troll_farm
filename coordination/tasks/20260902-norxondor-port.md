# Track P — the port of the second-placed player's bot (norxondor_gorgonax, 29.7, rule-based)

Born 2026-09-02 08:1xZ under the owner's decision of the same morning: *"I like this approach.
Write it down and let's do it. I took submission control from codex, it's yours now."*

- Record owner: local_claude_1 (coordinator) · Work owner: **codex_1** (the design read, the bot) ·
  Instrument owner: **claude_1** (the head-to-head panel, the bed for a new bot, the reproduction) ·
  Reviewer of the design: claude_1 and the coordinator; the owner reads it if they wish · Arena: the
  coordinator runs the ladder block through the VM queue (`local_claude_1/ladder-queue/queue.json`).

**Status line (08:1xZ):** born; the two charters go out with this card; nothing built yet.

## The rule (owner, plain words)

We are about ten ladder points behind bots whose designs we reconstructed on 08-28 and never wrote
as programs. norxondor_gorgonax is the one that is rule-based and fast (0.13 ms a turn, no search),
so it is the one we can port. **Build it as a new bot, judge it locally against our own bots first,
then against the real top players through the platform's test endpoint, and only then spend a
ladder hour.** The local panel selects; the ladder confirms.

## What the reconstruction gives, and what it does not (read this before the design)

`local_claude_1/reconstructions/norxondor_gorgonax/ALGORITHM.md` (467 lines; README rates it
MEDIUM-HIGH) — the parts marked **exact** or high-confidence, implementable as written:

- the **train ladder** (§3.1): floors `1: 2/2/1/1 · 2: 2/3/1/2 · 3: 2/3/0/3 · 4: 2/4/0/3`
  (speed/carry/harvest/chop), caps speed 4 · carry 5 · harvest 2 · chop 2 (trolls 1–2) or 3
  (3–4), cost `n + v²`; trains the same turn the floor is affordable (76/76 on turn 1; 441/443
  specs); roster caps at five; **no TRAIN once the mode is D** (443 + 193 turns, exact);
- the **phases** (§2): fruit-first build-up with a lemon/plum orchard by the shack, iron mined
  only when the next troll's floor needs it (1,036 of 1,036), the wood phase with chop-heavy
  trolls 3–4, the **P→D switch** at median turn 153 (62 % of games exactly one turn after the last
  TRAIN; the other 38 % unknown), then a clear-cut endgame;
- the **plant-and-cut banana loop** (§3.5, "the signature", 1,116 runs): pick a banana at the
  shack → plant it next to the shack → chop it at size 1 → drop one wood: a one-point fruit made
  into four wood points every few turns per troll;
- the **plant cell** = free cell minimising distance to shack + distance to troll (86.7 %);
- movement = one path step a turn toward a target cell (99.9 %).

The parts that are **descriptions, not rules** (the document's own words): the chop target
(40.7 % teacher-forced, weights guessed), the harvest target (59.2 %), the plant kind (best 37 %),
the D-switch trigger in 38 % of games, the meaning of the second state letter and of T, the
assignment of trolls to tasks, the PICK condition, the branch order of the per-turn procedure.

**The warning that shapes this card (§5 item 8):** in July a native controller assembled from fits
of this very bot (`rust/src/strategies/norxondor_native.rs`; records under
`data/analysis/live-agent-6553250/norxondor-*-2026-07-18.*`) **lost −172.7 paired margin against
our resident** and produced ~38 CHOP / 68 PICK a game where the real bot does ~159 / 17: small
target errors change the inventory and the geometry, and the program drifts into states the rules
were never fitted on. A straight port of the target layers was tried and failed. **So the design
here is a hybrid, decided by the design read:** the macro layer from norxondor (the ladder, the
phases, the banana loop, the orchard, the harvest talents), the micro layer (pathing, target
choice, denial, the I/O and board code) from our champion where the reconstruction is only a
description — and the panel, never per-decision accuracy, judges it. **This lowers the odds the
coordinator gave the owner at 07:5xZ ("two in three locally") to about even**; said so on the board.

## The three rungs (the panel selects, the ladder confirms)

1. **The local head-to-head panel** (instrument P-0, claude_1): two compiled single-file bots on
   real maps from the pinned corpus `/home/tarstars/nn-data/maps-host-corpus-0901-31088.jsonl`
   (also on the VM once copied), **200 maps × both seats = 400 games per opponent**, paired by map
   and seat, the July Python referee (`claude_1/pipeline/fuzz_panel.py`, `FuzzReferee.apply_two`,
   the one `local_claude_1/nn-bot/bench.py` already drives) or the Rust engine; rows in the shape
   `gate1.py` reads (`map_hash`, `policy_seat`, `policy_won`, `policy_score`, `bot_score`) so the
   144-unit bootstrap tool gives the interval unchanged. Opponents: **the champion of record**
   (`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…`) and
   **orchard 6** (`candidate-orchard6-v6-instrument.rs`, sha `32384936…`); the old champion with
   its denial rule on as a third, reported only. **Validity checks before any candidate is read:**
   champion vs itself ≈ 50 % on both seats; champion vs orchard 6 reported (their ladder readings
   were 18.2 and 18.8 the same day). The panel file (the 200 map records, seed 1) is written and
   its sha put on this card **before** the first candidate game.
2. **The real field through the platform's test endpoint** (`cgauto/field_panel.py`: baseline and
   candidate against the five fixed real Legend agents — delineate, wala, escdemon, norxondor,
   laconic — 12 games a burst, throttle-safe; the platform is ours since 09-02). Run only for a
   candidate that passed rung 1; the same paired reading, as many bursts as an afternoon allows.
   This is the check the July bench never had: a head-to-head edge over our own lineage need not
   transfer to the field (the denial rule read 0–6 locally and ±0 on the ladder).
3. **The ladder block:** the bed (`fixtures_diff.py` adapted for a new bot: plays 34/34 to the end,
   deterministic, compacted == arm, telemetry 0; the "differs from the champion" count is
   informational here), a second agent's byte-identity reproduction of the build, the owner's
   prediction, then **A-B-B-A**: champion baseline (already queued, `champion-baseline-0902-r1`),
   the port, the port again, the champion again — one hour each, the games collected.

## Ruling 2026-09-02 08:4xZ — rung 1 is a FIELD reading, not a duel (after P-0's calibration)

claude_1 delivered P-0 within the hour (`claude_1/h2h-panel/`, pinned `d9eeeeae…`; 9 tests; 400 games
a minute at four jobs). Its validity table changes rung 1: **the champion against itself is exactly
symmetric (113–174–113, margin 0.0), but orchard 6 loses 324 of 400 to the champion at −26 a game**
— while their ladder readings the same day were 18.8 and 18.2. A duel against our own clear-cutter
measures *race strength on a shared map*, not strength against the ladder's field; the denial rule
likewise reads −0.7 here and ±0 on the ladder (July's local bench had said −150). So:

- **Rung 1 = the candidate and the champion of record each played against the same local field**,
  paired by opponent, map and seat: the champion of record (`0e92f8fa…`), orchard 6 (`32384936…`),
  the old champion with its denial rule on (`72673124…`), and the network clone
  (`cgauto/submissions/candidate-nn-clone.rs`, a top-four imitation, if it runs inside the
  referee's time budget) — 200 maps × 2 seats per opponent. The statistic: the paired difference
  (candidate − champion) in win indicator and in margin per (opponent, map, seat), the interval by
  the gates' clustered bootstrap over maps, per opponent (`gate1.py --treatment 0=… --control 0=…
  --expected-cells 400`) and as the field mean (a small `field.py` aggregator, claude_1, before
  09-06). **Bar to rung 2:** the field-mean difference's interval above zero; if it straddles
  zero, rung 2 decides. **Dead** only if both rung 1's field reading and rung 2 read below with
  intervals wholly below zero, after the one refinement loop (the dead condition above is read
  this way).
- **The panel's pool (claude_1's question): (b) the slice stands.** `panel-200-seed1.jsonl`, sha
  `77556dc9214290264945274d6388cacb424f6d0db513cf68040bab45985d5ca7`, 200 distinct real ladder
  maps drawn with seed 1 from the 999-map slice on `main`; what the panel needs is a fixed file
  whose hash is on the card, not the laptop's corpus — and the copy would be a 70 MB transfer
  that only the owner's word may start.
- **Fidelity note of record:** panel games between two of our clear-cutters end early (median
  ~180 turns, 6 % reach turn 300; the champion's ladder games: 296 and 46 %) because the map is
  exhausted and the referee's no-plants rule ends the game; the port plants, so its games will
  run longer. Every panel row runs to the 300-turn cap.
- **For codex_1 (from the bed's control run):** the readable port file must carry the diagnostics
  `MSG` line itself; the source of record does not (the v6 arm adds it), and without it the bed's
  compacted-equals-readable check fails on every situation.

## Stages and roles

- **Read + design (codex_1, ≤ 1 day):** `codex_1/norxondor-port/DESIGN-2026-09-02.md` — (a) what
  the July native controller got wrong, from its own records; (b) the hybrid boundary: for each
  layer, "norxondor as written" / "champion's code" / "new, with this default", one line of
  reason each; (c) every open rule of §5 with the default chosen; (d) the build plan: the file
  layout under 100,000 characters (UTF-16 units), the time budget per turn (the champion runs at
  ~1 ms; the limit is 50 ms), what is reused from `readable/denial-off-champion.rs` (I/O, board,
  paths, targeting) and what is new. **One review round** (claude_1 + coordinator, ≤ half a day);
  a second only if the first finds a hole. The owner may read the note; nothing waits on that.
- **Build (codex_1, ≤ 3 days):** the readable source `readable/norxondor-port.rs`, compacted to
  `cgauto/submissions/candidate-norxondor-port-v1.rs` with its `.sha256` sidecar by
  `cgauto/compact_rust_source.py`; deterministic; the diagnostics line kept as in the v6
  instruments so the collected games can be read. Validity gates first: compiles with
  `rustc --edition=2021 -O`, plays 34/34 fixtures to the end, no illegal command on 24 real maps.
- **Panel (one, claude_1 runs, codex_1 reproduces):** rung 1 on the pinned panel file; the verdict
  by the same bootstrap as the network gates; then rung 2 if rung 1 passes.
- **One pre-registered refinement loop:** if rung 1 reads the port below the champion, codex_1
  gets one bounded loop (≤ 1 day) with the loss read written first (which layer, which games),
  then the panel once more. Not a second loop.
- **Ladder (coordinator):** rung 3.

## Done means

The port's ladder verdict is on this card and the board: two readings of the port and two of the
champion in the same window, the 160-game packages collected and read (`ladder_read.py`), and one
sentence — above the champion (then the owner's word makes it the champion of record) or not (then
the obituary in `GRAVEYARD.md` says which layer lost).

## Dead means

- The design read finds the hybrid cannot be specified (a layer that is neither describable nor
  borrowable) — the note says which and the line stops before a build.
- The bot cannot fit 100,000 characters or 50 ms a turn after one compaction pass.
- Rung 1 reads the port below the champion of record with the paired interval wholly below zero
  **after** the one refinement loop.
- Rung 2 reads the candidate below the baseline against the real field with the interval wholly
  below zero (the July-style head-to-head-only illusion) — then no ladder hour.
- Two days without evidence on any stage → STALLED → the owner says kill or extend.

## Budget

Five calendar days; codex_1 one day of design + three of build + the loop; claude_1 one day for
the panel instrument (rung 1 must exist before the first candidate) and the bed, half a day of
review, one reproduction; one panel per candidate, one refinement loop, one afternoon of rung 2,
one ladder block of four hours. No other track's ladder hours are taken.

## Log

- 2026-09-02 08:1xZ: card born; charters to codex_1 (design + build) and claude_1 (P-0 the panel
  instrument and the bed; then the reproduction) go out ack-required. The champion baseline
  `41230202` submitted 08:00Z by the VM runner, reading ≈ 09:02Z. — coordinator
- 2026-09-02 08:4xZ: **P-0 delivered by claude_1 within the hour** (handoff `20260902T083010Z`, pinned
  `d9eeeeae…`): the head-to-head driver, the panel file (sha `77556dc9…`, 200 maps, seed 1, from the 999-map
  slice), the bed for a new bot (PASS 34/34 on the champion's own arm), 9 tests; 400 games a minute. Validity:
  champion vs itself 113–174–113 (margin 0.0); **orchard 6 65–11–324, −26 a game** against ladder readings of
  18.8 vs 18.2; the denial rule −0.7. Ruling above: rung 1 becomes a field reading; the slice stands as the
  pool. codex_1 acknowledged 08:23Z (design read first, then the build). — coordinator
- 2026-09-02 09:2xZ: **claude_1 delivered `field.py`** (rung 1's aggregator; `claude_1/h2h-panel/field.py`, 9 tests, pinned
  `5f23c53c…`): per-opponent paired differences and a FIELD line with the clustered interval over maps; refuses unpaired
  inputs; verdicts FIELD_ABOVE_ZERO / BELOW / STRADDLES / INCONCLUSIVE. Ruling on its one open wording: **the bar is the
  win indicator** (the ladder's rating is computed from wins and losses, not margins); the margin is printed beside it and
  breaks a straddle only in the report's prose, never in the verdict. claude_1 plays and pins the champion's four field
  runs now, so a candidate's day costs only its own four. Track E's lead held two of the four bots (delineate 141 games,
  Bubaptik 66; norxondor and MSz none) — moot since the corpus is on the VM. — coordinator
- 2026-09-02 09:2xZ: **codex_1 delivered the design read** (`codex_1/norxondor-port/DESIGN-2026-09-02.md`, pinned
  `e1300d02…`, 320 lines) within an hour of its charter and waits at the review gate (its deferred card `20260902T091328Z`).
  **The coordinator's half of the one review round — DESIGN_ACCEPTED with two named changes, no second round:**
  the July diagnosis is sound and cites its records (the failure was at the policy/state boundary: a learned intent tree
  stood in for the missing P/D state, PICK without a plan or a cap, PICK racing TRAIN for the same bill); the hybrid
  boundary table is complete over §3.9 and §5; the TRAIN transaction is consistent with the exact same-turn rule (the
  completion test runs only when the floor is not affordable, and the referee applies PICK before TRAIN, so suppressing
  PICK on a TRAIN turn and pricing from the pre-turn inventory is right); the single bounded orchard job with a
  preselected cell removes the July loop without deleting the signature. The two changes, each from the measurement:
  **(1) the switch deadline.** The design forces D only at roster five or when the next floor cannot complete by turn
  185 (the corpus's latest TRAIN). Measured: the switch comes at median turn 153, and by roster at the switch 2 → 129,
  3 → 144, 4 → 154, 5 → 173; the bot ends with a median of four trolls (five in 24 of 218 games). A single 185 deadline
  keeps P running toward roster five whenever the fifth floor is reachable and lands D twenty to thirty turns late in the
  common roster-four game. Change: a roster-indexed table `SWITCH_DEADLINE = {2: 129, 3: 144, 4: 154}` (roster 5 → D at
  once, as designed) — D when the next floor is not affordable on the first turn at or past the deadline, the
  projected-completion test kept as the early exit before it; **gate 6 reports the produced switch turn and roster
  distribution on the 24-map run against the measured table.** The constant is the first tunable of the refinement
  loop. **(2) the conversion job's seed kinds.** Once bananas run low the real bot keeps planting and cutting the other
  kinds (turns 250–299: plum 309, lemon 266, apple 152, banana 128 across 218 games; fruit and wood score 1 and 4 a
  unit, trees nothing): the D conversion job takes the kind in stock that is cheapest to fell — banana first, then the
  sapling with the least health — under the same single-job bound. Pre-registered for the loop, not for v1: the banana
  loop admitted in P from roster three (2.8 bananas planted by turn 150 in the corpus, worth ~10 points), banana
  harvesting in P (8 % of trips). On the third question (v6 fields): claude_1's bed decodes the v6 line; the decoder
  needs no nonzero counter as far as the champion's own arm shows — claude_1 confirms in its half. **Build starts on
  this version with the two changes when claude_1's half of the round is in (due by 15:00Z); if it names a hole, it
  folds into the same round.** — coordinator
- 2026-09-02 09:3xZ: **the build is released now** (policy `20260902T093500Z`): the owner asked what we were waiting for,
  and the answer was my own gate on claude_1's half of the review; the build is the critical path, so codex_1 builds the
  accepted version with the two changes at once and folds in any hole claude_1 names by 15:00Z. — coordinator

- 2026-09-02 10:3xZ: **THE BOT IS BUILT — v2, both halves of the review in** (codex_1's correction handoff `20260902T101135Z`,
  pinned `7e45fa4c…`; the 09:51Z v1 `f15159ca…` superseded, never to enter reproduction or the panel):
  `readable/norxondor-port.rs` → `cgauto/submissions/candidate-norxondor-port-v2.rs`, **sha `411b0565ecda0139c96daaec02d26df0a7304c9b0aefa5c3823ff54ac1a9a8c1`,
  82,518 UTF-16 units** (the handoff said 80,930; the build report and the coordinator's own count say 82,518); compile PASS both forms; 15/15 mechanics tests (the three roster cutoffs, the non-banana
  fallback); bed 34/34 played, deterministic, compact == readable, telemetry 0; 24 maps × 2 seats 0 errors; timing p99
  8.6 ms, max 18.5 ms; **the switch trace over 48 games: roster 2 median 129, roster 3 median 144, roster 4 median 145**
  (the earlier switches by the retained projection; none past its cutoff). **The direct duel with the champion — informational,
  not the selector — 1/48, mean 117 vs 183, margin −65.5** (orchard 6 reads −26 in the same duel and +0.6 on the ladder;
  the field reading decides). **The review round closed with four edits and no dispute:** claude_1's E1 (the completion
  ETA must count trips by carry and dwell by harvest — the champion's `collection_eta` counts one item a trip and would
  have switched every game to D right after the third troll) and E2 ("carrying anything: bank" made a carry-3 funder bank
  after one fruit — deleted; partial loads bank only when adjacent or out of work), plus the coordinator's two (the
  roster cutoffs 129/144/154; any seed kind cheapest to fell). Q3 ruled by claude_1: no nonzero v6 counter required;
  one `MSG` token first, banner inside it. Next: claude_1 reproduces v2 byte for byte and runs rung 1. — coordinator
- 2026-09-02 10:3xZ: **the champion's four field runs pinned by claude_1** (panel `77556dc9…`, 400 games each, 0 faults in
  1,600; hashes in `claude_1/h2h-panel/README.md`): vs itself 113–174–113 (0.00); vs orchard 6 324–11–65 (+26.0); vs the
  old champion with denial on 147–131–122 (+0.68); vs the network clone 331–3–66 (+55.5). The clone in the field is
  `cgauto/submissions/candidate-nn-clone.rs` on `main` (the portable-runtime revision, sha `4c5a096d…`): warm median 6.5 ms
  a turn, p99 9.7, max 12.2 — inside the limit; the slow opponent (~2,800 games an hour). `field.py` now reads the verdict
  from the win indicator (landed `b389d01a`, 10 tests). A candidate's four runs take about 15 minutes. — coordinator
- 2026-09-02 10:3xZ: **two endgame signatures carried here from Track E's read** (closed the same hour: the late MOVE gap is
  real but not idle production — the layer that loses the last fifty turns is the roster and a map kept alive, this
  card's macro layer): for the port's loss read, report **MOVE per troll-turn in turns 251–300** (the champion 0.17, the
  field 0.37–0.62) and **tree-size units standing at the end** (the champion's median 4). — coordinator
