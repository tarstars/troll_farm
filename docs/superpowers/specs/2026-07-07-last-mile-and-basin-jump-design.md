# The last mile and the basin jump — design (Track A + Track B, subagent pipeline)

**Goal / success gate:** verified arena-room **rank ≤99** (two stable `cg_rank.py` ARENA-ROOM
reads ≥15 min apart). Standing invariant: the champion never ends a cycle regressed — every
arena trial uses same-hour bracketing and the frozen-fallback revert (as practiced 2026-07-06/07).

**Context (measured, 2026-07-06/07):** champion v1.28.2-steady2 (three-layer bot: tactics
Plan → planner bands+matching → joint move solver + sticky targets) at 19.0-19.2, rank
111-115. Census: even (+4 avg) with the 100-150 band; the ≤100 tier (≥19.6) wins by
hoard-then-factory scale (decoded from replay: jrl86 602 = no felling to t150, 4-5 trolls
funded off the untouched map, then a plant-and-fell factory). Closed lines: protection alone
("pie" feeds the stronger late engine: −1.0…−2.8 ×3), 3-troll on the tempo build (lemon wall
— a TIMING artifact: lemons are spent at t3 and never ripen under fell-at-2), stickiness
beyond 3 (neutral). User decision: success bar = rank ≤99 (Legend/boss is a later feature).

## Shape: one bot, two phases, one pipeline

Track B is NOT a second bot. It is a **tactics-layer phase mode** in the champion, selected
by a const (`GE_META`), with the planner's value bands parameterized by phase:

- `Meta::Tempo` (default = today's champion, byte-identical when selected — enforced by the
  equality harness: the flag-off build must stream-match the frozen champion),
- `Meta::Scale`: `Phase::Hoard` for `t < T_SWITCH` (~140): harvest/mine/plant bands raised,
  fell bands suppressed (exception — denial-emergency band, concrete trigger: a fellable
  tree in OUR half with an enemy troll within map-distance 2 of it may be felled; nothing
  else), native lemon/plum banked BEFORE the map deforests (dissolves the lemon wall),
  hands trained from the hoarded wallet (the dormant GE_MAX_TROLLS/feeder machinery re-arms
  here, spec (1,1,1,0) and/or (2,2,0,2) second chopper per gate results); then
  `Phase::Factory`: plant-and-fell loop bands (PLANT feeds CHOP; the farm is the fuel, not
  the map), existing liquidation tail.

Track A stays on the champion: single-knob arena cycles from the hypothesis queue.

## Subagent pipeline (stages; main session = orchestrator)

Contracts are files; each stage's brief is self-contained (agents start cold).

1. **builder** (worktree isolation): implements ONE candidate from the queue; runs local
   gates: `cargo test --release` (all suites), self-determinism equality (bot vs bot,
   ≥8 seeds, opp=self), bundle + rustc compile + minify <100 KB, and — for any candidate
   with `Meta::Tempo` selected — flag-off stream-equality vs the frozen champion binary.
   Output: `data/candidates/<name>/{<name>.rs, <name>.min.rs, report.md}`.
2. **gatekeeper**: plays boss 8 + field 4-6 (MUST include denial-style opponents — a hoard
   build's weakness is exactly what our own tempo bot punishes; roster via
   `field_targets.py`, e.g. mikdiet/plcc + one ≥19.6). Reads telemetry (@TFFARM, @TFPHASE).
   Verdict vs thresholds: wood ≥45 era-norm, no crater signature, phase invariants hold.
3. **arena-runner** (the ONLY submitter — the arena is one serialized slot): same-hour
   bracket read → submit → convergence reads → keep/revert per ±0.2 rule → update
   `api_submit.py` default + experiment log. One candidate at a time, ~1 h/cycle.
4. **analyst**: after each verdict — battles.py census, replay decodes of new loss patterns,
   append findings + re-rank the hypothesis queue.

Main session dispatches stages, reviews reports between stages, merges builder worktrees,
and is the only writer to the roadmap/memory.

## Initial queue

- **A1** `GE_LIQ_T` 34→44 (earlier endgame banking; targets the +4-margin coin-flips).
- **A2** denial-weight probe in fell valuation (small `w·dist(tree, opp)` bonus, w∈{1,2}).
- **B1** phase skeleton: `Meta`/`Phase` enums, band parameterization, @TFPHASE telemetry,
  ALL BANDS UNCHANGED in Tempo — gate = flag-off equality (zero behavior change shipped).
- **B2** hoard bands + wallet/training ladder (gates: hands trained ≥2 by t140 in ≥6/8 boss
  games; lemon banked ≥ ladder cost by t100).
- **B3** factory bands (gates: plant→fell loop sustains — PLANT count t150+ ≥25, wood ≥60).
- **B4** Scale-meta arena trial vs champion bracket.
- Track A retires after two consecutive neutral/negative cycles; B4 keep/revert decides the
  champion. Repeat analyst→queue until rank ≤99 verified.

## Testing

Existing suites stay green every candidate (20 suites incl. corridor + planner + solver
property tests). New: phase-invariant unit tests (Hoard emits no CHOP except the
denial-emergency band; Factory sustains the loop on a constructed farm state), @TFPHASE
telemetry asserted in gatekeeper readouts. The equality harness protects Tempo throughout.

## Risks

- **Transfer wall**: probes filter, ONLY the arena verdict counts (rule since seedloop).
- **Hoard fragility vs denial**: mitigated by gatekeeper's denial-opponent requirement and
  the denial-emergency band; if hoard loses the early race unrecoverably, T_SWITCH sweeps
  down (120/100) before abandoning.
- **API budget** (~150 games/day observed): gatekeeper batches are 12-14 games/candidate.
- **Arena drift ±0.3**: bracket discipline; neutral zone ±0.2 keeps the champion.

## Exit

Rank ≤99 verified twice → feature done; leftover B momentum (Legend/boss 26) becomes the
next feature's spec.

## Amendment (2026-07-07 ~14:30, after Scale gates #1-#4) — hoard PARKED, queue re-ranked

Gates #1-#4 (data/candidates/v1.34.0-factory/report.md) proved the Scale machinery works
(phase flip 8/8, wallet fills, all 4 hands train 7/8) and simultaneously condemned the
strategy at our band: our wood 0→0→4→23 across fixes while OPPONENT wood held ~57-60
throughout — the gap is the 100-140 turns of shared map ceded to feller opponents, not our
internals. Field probes −400 avg = arena-crater signature (seedloop lesson). Matchmaking
argument: the hoard meta cannot climb from rank ~113 because every rank between here and
the 20.0-tier is a feller who punishes it; the blueprint works only AT the tier where
neighbors reciprocate. **B4 (Scale arena trial) is PARKED** — do not spend gate #5.

**Salvage → new queue head, T-hand (v1.35.0-thand): Tempo + funded third hand.** The Scale
arc's real yield is the battle-tested funding machine (iron 65/64 > deficit-fruit 63 >
wallet 62 > printer, want_feeder-scoped, self-extinguishing, gracefully absent when the
resource doesn't exist). It dissolves the historical lemon wall. Under Tempo: GE_MAX_TROLLS
2→3 (the existing feeder gates apply: nchop≥1, t≥45, farm≥3) + the elevated funding stack
extended from Scale-only to all want_feeder. Adds extraction (right side of the pie
insight); attacks the champion's one measured flaw (late farm supply). Degrades gracefully
to the 2-troll champion on maps where the wallet can't fill. Then A2 (denial probe).
Exit gate unchanged: rank ≤99 verified twice.

## Amendment 2 (2026-07-07 ~20:00) — user replay-review: three efficiency findings → queue
User watched live-bot games and found: (1) DOOMED-TARGET CHASING — we trek to trees an
enemy is already chopping and lose the race + the travel; fix = race check in fell valuation
(enemy-on-tree: ceil(health/enemy_chop) vs our ETA; doomed → value ~0). (2) BANANA SOURCE
ORDER — printer PICKs the tent before harvesting ripe trees; backwards: tree-first accumulates
tent stock = 1pt held or 8pt via plant→fell (2 wood) conversion. (3) DIAGONAL FARM GEOMETRY —
plant preference for the 4 diagonal-to-shack cells: map-distance 2 but OFF the orthogonal
bank-path cells (no traffic block); collect-all → plant → bank excess loop. The "keep grown
diagonal fruiters" sub-idea = protection (3× arena-negative) → separate, strictly-gated
sub-candidate only.
QUEUE (after the in-flight v1.35.0-thand arena verdict): v1.36.0-race (finding 1, standalone,
zero-pie-risk waste cut), v1.37.0-nanaflow (findings 2+3 placement+loop, one candidate;
protection part deferred). A2 (denial probe) follows.
