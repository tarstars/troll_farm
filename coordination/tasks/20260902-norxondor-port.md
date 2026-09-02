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
- 2026-09-02 08:3xZ: **P-0 delivered** (claude_1, `claude_1/h2h-panel/`, report `P0-2026-09-02.md`):
  the driver, 9 tests passing, the bed for a new bot, and the validity runs — the champion vs
  itself 113–174–113 (margin exactly 0; seat 0 wins 52, seat 1 wins 61 of the decided maps),
  orchard 6 vs the champion 65–11–324 (margin −26 [−30.6, −21.6]; its ladder reading the same day
  was above the champion's — the non-transfer rung 2 is for), the old denial-on champion −0.7
  [−1.4, +0.1]; 0 faults in 1,200 games; 26,000–32,000 games an hour on the VM at 4 jobs.
  **Panel file `claude_1/h2h-panel/panel-200-seed1.jsonl`, sha
  `77556dc9214290264945274d6388cacb424f6d0db513cf68040bab45985d5ca7`** — drawn with seed 1 from
  the 999-map slice on `main` (`local_claude_1/nn-bot/maps-slice-1000.jsonl`), because the
  pinned laptop corpus is not reachable from the VM; to be regenerated from the pinned corpus
  (same seed, new sha here) once it is under `/data/scratch/`, before the first candidate game.
  Games here are shorter than ladder games (median ~180 turns vs 296) because two clear-cutters
  exhaust the map and the referee's no-plants rule ends the game; the port plants, so its games
  will run longer. — claude_1
