# Session Handoff — 2026-07-11 (flush-safe snapshot)

Durable state so a fresh/compacted session resumes without the transcript. Committed to git.
Trust `docs/arena-queue.md` (live verdict log) + `docs/silver-experiment-log.md` (full narrative)
over this file when they disagree; the memory header (`MEMORY.md`) is the one-line pointer.

## CHAMPION (live / default / tree — all consistent)
**v1.59.0-ringfix3** = v1.56.0-ringfarm (user's 8-cell tent-ring banana farm, built early) + FIX3
(banana no-carry-in-advance / backtracking fix, isolated from the E1 fund-first term that sank
v1.57). Best bot the project has produced.
- Arena: converged band ~17.7-18.8 (read 118/530 @18.8 on 2026-07-11); +1.1-1.4 over its bracket
  when promoted. The v1.56 ringfarm base was +1.7 (first positive economy result ever; pie family
  0-for-5) and ~18% vs REAL Boss 5 (2W/9L — first boss wins for the 2-troll lineage, was 0/32).
- `cgauto/api_submit.py` default = `cgauto/submissions/v1.59.0-ringfix3.min.rs`. Tree HEAD carries
  VERSION 1.59.0-ringfix3 (the etudes additions do NOT change VERSION — they're isolated).
- Revert target = that artifact. Read rank via `uv run --no-sync python cgauto/cg_rank.py`
  (ARENA-ROOM line only). Same-code arena DRIFT is ±1-2 over hours — use policy v2 (deltas only).

## STRATEGIC STATE — the tuned-band champion is at its practical CEILING
SIX consecutive "cleaner/smarter but arena-negative" results prove the tuned band system is a
robust local optimum; re-architecture and economy-rebalance both keep losing:
- WINS (all EXECUTION/coordination cuts WITHIN the band framework): race check +1.3, yield/task-
  interference +1.0, joint move solver +0.7, ringfarm-early +1.7, ringfix3 (FIX3) +1.1.
- REVERTS: ownership +0.2-inert, taskfloor −1.0, ringtune −2.4, trainfruit −3.2, roam4 −3.6,
  v1.60-fellmission −1.0. RECURRING LESSON: "obvious waste" usually isn't load-bearing; the
  band's turn-by-turn FLEXIBILITY (re-target, race-steer) IS. Quick in-framework cuts are
  exhausted; anti-oscillation = "more STICKY" (already swept, STICKY=6 optimal). Candidate well
  is DRY for eyeballed cuts → this is exactly why the ETUDES pivot exists.

## ★ ETUDES PROGRAM (the pivot: prove what decides games, stop guessing) — TOOLCHAIN COMPLETE
Approach A (user-chosen): EXACT/PROVABLE on small constructed positions; verdicts restricted to
FORCED outcomes (a side guarantees strictly-better final score vs ANY opponent play — sidesteps
the simultaneous-move mixed-strategy problem; contested = Unresolved, excluded).
- **Oracle** (`rust/src/etudes/{situation,actions,oracle}.rs`, MERGED, isolated, 9 tests):
  `forced_verdict(&Situation) -> Verdict::{ForcedWin{side,proof}, Unresolved, TooLarge}`. Sound
  informed-minimax (X commits its joint action, Y sees it and best-responds → value>0 ⇒ genuine
  forced win, a conservative lower bound) + alpha-beta + transposition table over the REAL
  `game::engine::step`; NODE_BUDGET=100k (~0.1s at H=16). `replay_proof(&Situation,&Verdict)->bool`
  independently re-validates each forced win by brute-force opponent enumeration (a false ForcedWin
  can't pass it). Verdict metric = score-diff (fruit+4·wood) at the horizon.
- **Editor/runner** (`rust/src/bin/etude.rs`, MERGED): `cargo run --release --bin etude <file.txt>
  [--step]` renders an ASCII board + entity table, prints the verdict + forcing line, `proof
  validated: true/false`, and --step walks the board ply-by-ply. Sample:
  `rust/data/etudes/sample-forced-win.txt` (a size-2 banana felled + banked → ForcedWin(0), 8-0).
- **Situation text format** (hand-authored, `situation::from_text`): `MAP w h` + grid rows
  (`.`walk `#`rock `~`water `+`iron `0`/`1` shacks) + `INV0/INV1 <6>` + `UNIT id player x y ms cc
  hp chop <carry6>` + `PLANT TYPE x y size health fruits cooldown` + `TURN n` + `SCORES a b` +
  `HORIZON h` + `PROVE -|0|1`. ★ cooldown MUST be >0 (e.g. 6) for a quiescent tree — cooldown==0
  triggers immediate regrowth in tick_plants (a real gotcha the builder hit).
- SCOPE HONESTY: tractable only for TINY positions (~1 troll/side, H≤16) → discovers transferable
  PRINCIPLES, not full 300-turn strategy verdicts (2-troll strategy Qs return TooLarge → use the
  arena for those).
- NEXT etude sub-projects (not yet built): the etude DATABASE (a library of authored etudes +
  verdicts + proofs), a VISUAL browser editor (option B), and AUTHORING the first real etudes —
  the farm-sustainability questions below.

## IN-FLIGHT (as of the handoff)
- **v1.61.0-chopharvest** — BUILDING (subagent a4a28cc4b0708f40c, worktree
  agent-a4a28cc4b0708f40c; 3+ commits: 423538b band-38 harvest, eaff348 telemetry, 6c04cb1 wired
  hp into the live turn-1 adaptive spec). USER IDEA: chopper spec hp 0→1 (`GE_SPEC (2,3,0,2)→
  (2,3,1,2)`, +1 apple) so it CAN harvest, + opportunistic harvest of full/ripe bananas STRICTLY
  below its chopping (idle-fruit band 38; high bands 75/62 gated `!is_chopper` so felling always
  wins; starter byte-identical). Fixes the "ring bananas fill to cap and stall" farm-death. When
  it reports: review (the reviewer subagent a1cec0b4181e8e8da carries planner/context) → paired
  boss gate (ring stays alive AND wood ≥ ringfix3 — if wood drops, harvest steals chop turns =
  fail) → arena chained on ringfix3. FARM-SUSTAINABILITY CLASS (0-for-3: seedloop/reserve/
  ownership) but a fresh cheap mechanism → arena decides. brief: data/candidates/v1.61.0-chopharvest/.

## OPEN BACKLOG / IDEAS (evidence-ranked)
1. **Farm-sustainability etudes** (now PROVABLE on tiny positions): (a) "with a nearby wild banana
   tree, is protecting it (forgo early wood) a FORCED net advantage, or does early-wood tempo
   dominate?" — the clipboard#3 finding (chopper fells both nearby wild bananas t52/t64, removing
   the renewable fruit/seed source → farm dies t148 → distant foraging → loss); (b) chopper
   opportunistic-harvest value; (c) the spec tweaks — does +1 cc or +1 hp on the chopper force a
   net gain given the quadratic apple/lemon cost? Author these as etudes to settle by proof.
2. **chopharvest arena verdict** (in flight) — if KEEP, it's the first farm-sustainability win.
3. Parked (likely non-load-bearing per the reverts): mutual-oscillation / BuildRing mission (the
   6th-revert commitment-hurts lesson); frontdoor-v2 (chopper roam + seed-reserve still shack-
   bridge on chokepoint maps — reviewer follow-ups, non-regressions); the full mission layer
   (spec docs/superpowers/specs/2026-07-10-intent-missions; FellForWood increment reverted −1.0).

## KEY MECHANICS (verified from engine, reusable)
- Troll `hp` = HARVEST POWER (fruit per HARVEST, up to MAX_FRUITS); NOT combat health — trolls
  can't die, no combat. TREES have `health` = chops-to-fell = ceil(health/chop_power).
- Training cost = `n + stat²` per stat, paid in that stat's fruit (n = the troll number): PLUM→ms,
  LEMON→cc, APPLE→hp, IRON→chop. Quadratic → +1 stat is cheap in stat terms but resource-expensive
  (the "lemon wall"). BANANA is NOT a training resource (fruit-for-points + fells for wood).
- Fruit caps: `if fruits < MAX_FRUITS { fruits += 1 }` — a full tree STOPS producing (stalled
  throughput, not lost value). Score = sum(fruit inv) + 4·wood inv (banked only; carry doesn't score).
- Starter troll = the game's INITIAL unit, fixed 1/1/1/1 (ms/cc/hp/chop) — can't be retrained;
  only ADDITIONAL trolls are trained. Champion trains 1 chopper `GE_SPEC (2,3,0,2)`, GE_MAX_TROLLS=2.
- Engine turn order: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE. Shacks NOT walkable
  (only GRASS). Trees don't block movement.

## PROCESS (binding)
- Policy v2 (docs/arena-queue.md): only base→candidate DELTAS carry signal; baseline valid ~5h;
  chain candidates; ±0.5 bands (KEEP ≥+0.5, promote +1.0-once or +0.5×2, REVERT ≤−0.5); verdict
  at +50m. Absolute reads uncomparable across hours.
- Subagent pipeline: builder(worktree)→review(reviewer a1cec0b4)→gate→arena-runner. Tree-tracks-
  champion (arena revert must restore source consts). Commit-verdict-immediately. Reverted
  candidates' code is PRESERVED on their worktree branches (worktree-agent-*).
- RESILIENCE: the Anthropic API drops subagents mid-task (connection/Overloaded) — builders commit
  per-step; the CONTROLLER can run collect/gate/arena INLINE from the main thread (CodinGame API
  works even when subagent inference is throttled); reconstruct dead subagents from worktree
  commits, never resubmit blind. cwd slips recur (cgauto from repo root, cargo from rust/).
- Python: `uv run --no-sync python`. Commit trailer: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## RESUME POINTER
On resume: (1) `cg_rank.py` — confirm champion ~17-19 (if regressed, revert to
v1.59.0-ringfix3.min.rs). (2) Check the chopharvest subagent (a4a28cc4) — if done, review→gate→
arena; if dead, reconstruct from its worktree commits. (3) The etudes toolchain is ready — author
the farm-sustainability etudes (backlog #1) to settle the farm-death questions by PROOF.
