# BACKLOG — path to Legend top-3

Created 2026-07-27, consistency-revised 2026-07-28. Owner-ranked task list for the
standing goal (`docs/STATE.md` §2: rank ≤ 3 on a mature read + confirmation; bar 28.22
as of 2026-07-28 — MSz; was 28.11 at Phase 21). Every item cites its evidence
(`Dnnn`/`Phase n` = ledger; classes = `docs/CONSTRAINTS.md`). Re-rank only from written
evidence. One experiment in flight at a time (standing Tier-0 operations may run in
parallel); each ends with a ledger entry.

## Position summary (2026-07-28)

Resident `6561795`: rank 43/110 @ 21.97, score **source-side frozen since 07-23** (the
ladder recomputes fresh-agent scores rarely) — the once-assumed passive-maturity recovery
is dead as a lever; **code strength must carry essentially the whole +6.25 gap** to the
28.22 bar. The loss mechanism is measured: anti-compounding catastrophic tail (D159 —
leads +23.9 at t100 → −5.2 at t225; ~10–11% of games carry ~58% of negative mass,
independently replicated at n=192), rooted in production persistence during/after scaling
(D101: top-3 reap 24.16% of created crops, resident 0.94%; suppression already
competitive). The replay corpus is 8,122 games / 469 agents after the 2026-07-28
wide-lens collection (4× in one run). The active critical path is Tier 2: D169's
envelope PASS (+10.671) → D170b closed-loop training (in flight).

## Tier 0 — free points and standing discipline (no code)

- **B0.1 ✅ DONE 2026-07-27** — passive read: resident 43/110 @ 21.97 (203 battles), bar
  MSz 28.22; 198 new replays, QA clean. **Key finding: the score is source-side frozen
  since 07-23 (no ladder recomputation; 6 battles in 4 days) — the passive-maturity lever
  is much weaker than assumed. Code strength must carry essentially the whole +6.25 gap.**
- **B0.2 ✅ DONE 2026-07-27** — cleanup executed (SDD, all reviews clean): 22 worktrees
  removed, debug cache cleared + cap rule, 683 files / 1.04 GB migrated + symlinked, YT
  dead dir removed, 425 MB mirror uploaded md5-verified. Repo 23.5 → 2.76 GB.
- **B0.3 No-churn rule stays absolute** — no arena write until a candidate passes the
  promotion protocol (B4.1). Every failed trial costs ~2–4 points of standing for days.
  [class (g), fresh-vs-mature]
- **B0.4 ✅ INSTALLED 2026-07-28** (authorized under owner decision (b)): daily cron
  05:17 → `data/scripts/collect_wide_cron.sh` (marker `# troll-farm-wide-collect`;
  removal = delete that line via `crontab -e`). Driver committed (`b15a75f`) with
  offline failure-path tests; live test run: +9 games → 8,131 cumulative, QA clean.

## Tier 1 — declared next experiments (cheap, bounded, evidence-backed)

- **B1.1 ✅ DONE 2026-07-27 (D167a)** — acquisition paths ARE regular: **BANK_SEED
  frozen-eligible** (135/135 local; 71.4% top-5 field, 4/5 agents, both seats; all frozen
  gates passed, no tuning). OPPONENT_DERIVED closed as a class. Bonus discovery: top agents
  pre-carry seeds through suppression (22/49 cycles) — the resident never does (0/1,024).
- **B1.2 ✅ DONE 2026-07-27 (D168a) — kill rule fired.** Both bounded BANK_SEED options
  failed value decisively (post-return −6.73 [−8.40,−4.08]; pre-carry −8.21; worst
  family −17.11) with mechanism and integrity fully clean. **Hand-written successor
  controllers are closed**; the motif enters B2.1 as a rollout-valued option only.
  Bonus fact for B2.1: carry is empty at 100% of P→S entries — pre-carry preconditions
  never arm on resident trajectories. Tier 1 is complete. [D168; vol 2]

## Tier 2 — the big bet: resident-native options + closed-loop learning

The only levers with measured headroom ≥ the gap are hindsight oracles over
option/joint-assignment spaces (D97 +36.9; D107 four-use +35.2; D144 combined +42.6;
D152 exact-second +36.8 on actives; D162 resident-native envelope **+12.7 [+9.0,+16.3]
with zero regressions**). Every *offline* selector over them failed (best D142b +3.06,
under bar); the never-executed branch is closed-loop optimization on the **resident**
substrate with a family-robust objective (skipped-D109 question, D157 audit; D158's
invalidation was substrate-only). Prereq chain, each gate preregistered:

- **B2.1 ✅ DONE 2026-07-27 (D169a) — PASS, gate cleared cleanly.** Envelope over
  {OPT_RETURN, 3× D163 resource options, all ± B3.1-trigger arming}: **+10.671 mean,
  CI [+9.420, +11.922], 65% improved, 0 regressions**, tails better than control, 100%
  coverage. Every option negative always-on — value is pure per-game selection. No
  D169b needed (all six PASS conditions held on the first pass). *(The one-time Fable
  STOP for D170 authoring was satisfied 2026-07-28; no pause is in force.)*
- **B2.2 → D170 — IN FLIGHT (D170b re-run executing 2026-07-28).** History: D170a
  protocol frozen (Fable) → Phase 1 trained 8 fits → resume validation exposed a
  structural trig-arming bug in the new composition code → **CLOSED-AT-PHASE-1
  adjudicated as implementation invalidation** (no value ever computed; frozen vocabulary
  intact) → **D170b** mechanics-only repair protocol frozen and now executing (repair +
  activation verification + offered-conditional exploration semantics; all science
  inherited). Chain: `d170a-...-protocol`, `d170a-...-result` (the invalidation record),
  `d170b-...-repair-protocol`. Four-objective comparison (the skipped-D109 question) →
  LOBO admission/selection → veto → sealed confirmation → int8 deployability → 🛑 user
  arena gate.
  Recurrent policy over the B2.1 options with exact-resident action zero; objective =
  paired margin with group-DRO/worst-family term and own-score protection (D109's
  rotation, r=−0.014 across panels, is the failure this objective targets). Selection by
  independent-block leave-one-out only (D134 — fit statistics anti-predict transfer).
  **Gates:** same-panel dominance over exact resident (D158 rule); fresh-block +≥2 with
  all families ≥ −1; latency p95 < 50 ms in the deployable form (V5 buffer pattern);
  ≤100 kB source. **Kill:** two consecutive objective variants fail fresh-block → close
  the program and hold at Tier 0/3.
- **B2.2 ❌ CLOSED 2026-07-28 (D170b, kill rule fired on valid mechanics).** 8/8 fits
  trained; 0/8 admitted — all four objectives converged to always-KEEP (P(invoke) ≤3.3%);
  sampled-invoke value −1.0..−2.3. The envelope's positive contexts are unlearnable by
  on-policy terminal-reward training at this (or any sane) budget; objective choice
  irrelevant in this regime. Tier-2 CLOSED; project holds at Tier 0/3. Successor
  (dense counterfactual credit) = new program, owner authorization required. [D170b]
- **B2.3 — moot** (gated on B2.2, which closed).
- **B2.4 ❌ CLOSED-AT-SELECTION 2026-07-28 (D172a) — the definitive Tier-2 closure.**
  Signal abundant (40.4% of 27,392 states carry ≥+2), labels exact, states
  on-distribution — and held value only +0.14..+0.26 for both function classes. The
  positive contexts are not identifiable from current observables (CONSTRAINTS ★FINAL).
  Tier-2 is closed on the strongest possible evidence; sealed block 9,862,000–063 and
  the veto discipline preserved. Residual for any future owner decision: spatial-plane
  observations on the official substrate (never retried post-D33).

## Tier 3 — execution-class diagnostics (historically the only transferrers)

- **B3.1 ✅ DONE 2026-07-27** — signature replicates independently (19/192, 57.9% of
  negative mass); the endgame switch has NO coverage bug (fires at the earliest turn its
  behind-AND design permits; retuning closed — CONSTRAINTS §(f)). Surviving output: an
  observable early-warning trigger — opponent scaling past 2 workers precedes the
  crossover by 42–125 turns in 84% of catastrophes (83% of mass). **Feeds B2.1 as an
  activation-conditioning signal**, not a switch retune.
- **B3.2 ✅ DONE 2026-07-28** — motion audit clean at 4× scale (49,977 moves, zero
  failures, replicating 07-16). **One concrete candidate found → B3.4.** Context: 29
  first-seen agents include qualitatively new scaling (Pafin: 5 workers in 48% of games)
  and denial styles absent from the local panel.
- **B3.3 ✅ DONE 2026-07-28** — BANK_SEED (67.5%), pre-carry (40.5%), catastrophe
  signature (9.8%, lead 74.4 turns) all stable; **D164's top-5 motif population rate
  corrected 72% → 49.7%** (sampling-completeness artifact; the frozen breadth+gap gate
  still passes, 5/5 agents, +38.9pp vs resident). CONSTRAINTS updated.
- **B3.4 — diagnosis ✅ (root cause pinned: memoryless detour tie-break,
  `yamo_orchard_live.rs:1505-19`; coverage gap in `force_unique_door_clear`); fix v1
  (D171a) ❌ CLOSED** — hard-forbid breaker under-cured long runs (45.7% vs 80%) and
  manufactured short ones (+117%, stale-arm design hole). Causality was modest anyway
  (2/18 suspicious). **Open successor option — D171b** (redesigned semantics: bounded arm
  lifetime + echo-stop disarm + ≤2 forced choices, or preference-based tie-break); cheap
  (all machinery exists), expected value small; promotion of any qualified successor
  needs a NEW owner authorization (the D171a standing grant never triggered and does not
  carry over).
- **B3.5 ❌ CLOSED 2026-07-28 (D173a + D173b)** — diagnosis excellent (missing HARVEST
  action class, 1,972 pts/9.62 per game lost), fix works on what it can reach (99.9%
  elimination among harvest-capable choppers) but 99.93% of the vein needs trained-unit
  harvest capability (`opening_options` hp:0) — strategy, not execution. Both variants
  also failed worst-family/catastrophe/tail gates identically: delaying wood for fruit
  has a real cost. **Successor is strategic and gated on B3.8's funding verdict** (does
  the fruit pay TRAIN bills? if no, the whole vein closes; if yes, a worker-capability
  protocol becomes justified). Original entry:
  — ripe fruit unharvested ≥3 turns with a capable worker nearby: 2,163 episodes in
  204/205 games, ~536 pts gross ceiling (~2.6/game), loss-enriched +15–20%, 91%
  independent of the closed oscillation vein. Plausible target-reassignment root cause.
  Pipeline: diagnosis (in flight) → bounded fix protocol → gates. The waste-sweep tool
  is now standing (`cgauto/waste_sweep.py`, commit 31b3ef0).
- **B3.6 ❌ CLOSED 2026-07-28** — `idle_with_work` sub-classified: ~78% benign/correct/
  detector-artifact, genuine ceiling ≤0.6 pts/game with no shared mechanism, flat across
  outcomes; round 2's "wood-race" flagship falsified (11% clean loss, ≤68 pts). No fix
  candidate. **Deferred chore:** gate the detector on free capacity (blocked while D173b
  uses `waste_sweep.py`).
- **B3.7 crop-fate census — IN FLIGHT** (owner-originated): what happens to the ~99% of
  our crops we never reap — harvested/chopped-by-us/taken/expired/alive — plus
  live-crops-per-capable-worker vs the top cohort. Verdict shapes whether a plant-pacing
  rule, denial, or an orchard rethink is warranted.
- **B3.8 ✅ DONE 2026-07-28 — verdict (c) NO: the bootstrap is IRON-limited.** All
  uncollected fruit (ours + opponent's) would open a cheap-helper window in ~10% of games,
  balanced spec 0/205 ever; IRON limits 97.3–100% of failures. Owner's near-camp
  hypothesis CONFIRMED (1,144 events ≤2 from our door; 71.8% outside D173b's scope; 43.4%
  capturable in a ≤2-turn detour). Top-5 fund 66% of bills from earned currency, 76% fruit.
- **B3.9 ✅ DONE 2026-07-28 — verdict (A), the strongest lead in the project's history.**
  Mining is gated off entirely at workforce ≥2 (one call site, `own_units < 2`); 0.68
  iron/game vs top-5's 13.02; 98%+ of reachable iron unconverted at approach distance 0;
  no capability wall. Fruit+iron together: cheap-helper affordability 8.8% → **84.4%**,
  balanced 0% → **42.4%**. → **D174a frozen** (`d174a-opportunistic-mining-protocol-
  2026-07-28.md`): TRAIN-trigger preflight, opportunistic MINE candidate at workforce ≥2,
  mechanism gates including **worker-3 TRAIN in ≥25% of tasks** (control 0%), value gates
  retaining the family/tail floors both D173 variants failed. QUALIFIED → candidate at the
  arena gate (new owner authorization required).
- *(original B3.9 scope)* IRON acquisition audit + combined
  counterfactual — mining has never been audited. Measure our MINE behaviour vs the top
  cohort (rate, timing, iron-source proximity, missed reachable iron), then re-run the
  affordability counterfactual crediting BOTH uncollected fruit AND missed iron. This is
  the decisive test of whether the production+consumption coupling has ANY viable bootstrap
  for us. If iron slack is large → an execution-class mining fix becomes the top candidate;
  if not → scaling is structurally out of reach and the orchard must be justified by direct
  fruit value alone.
- **B4.3 ✅ DONE 2026-07-28 — the scaling destination is priced**: within-agent +48.2
  margin/worker (CI [44.1,52.7]); 2→3 = +1.9 rating, 3→4 = +3.3, 4→5 = none; resident wins
  5.0% vs 4+-worker opponents. **2→4 ≈ +5.2 rating = 84% of the gap.** Gated on B3.9.
- **B4.4 ✅ DONE 2026-07-28 — the non-scaling path is real and identified.** We plant at
  turn 191.5 vs peers' 21–29; reap 0.93% vs 15–17% for every other two-worker agent; at
  equal roster we are at PARITY with strong peers (58.2/58.3) — the deficit is entirely
  scale-asymmetry survival, downstream of having no sustained plant-reap loop. The loop's
  code exists, tested, defaulting OFF behind a rarely-firing selector (D89/D91 lineage).
  Ranked: (1) no plant-reap loop [policy/parameter], (2) scale survival [downstream],
  (3) suppression efficiency 0.31 vs 0.43 wood/chop [execution]. Caveat: 4/12 STRONG
  agents share our no-loop profile and still outrank us.
- **B4.5 (new, OPEN — next after D174): planting-gate diagnostic → D175.** Characterize
  the `banana_factory_*` enable condition and selector precisely; measure how often it
  fires in real games and what it would do at various thresholds; reconcile with D89's
  safety rejection (full factory, +82.9 opponent) and D91's 5/16-map selector failure, and
  determine what distinguishes the field's early-moderate planters from D89's
  plant-everything design. Read-only; sequenced after D174 to avoid concurrent edits to
  the resident source. Output: a frozen D175 protocol for the middle-ground planting loop. 25
  Legend agents run the resident's exact 2.00 roster yet rank 7–54 — a two-worker
  architecture demonstrably reaches rank 7, ~9 rating points above us, with no scaling at
  all. What do the strong two-worker agents do that we don't? Read-only field comparison
  of score composition, production, suppression, timing, and terminal behaviour. This is
  the only direction that is neither closed nor affordability-gated.
- **B3.10 (new, OPEN, conditional): near-camp opportunistic harvest** — 956 bill-relevant
  near-camp events, 71.8% outside the tested scope, 43.4% cheaply capturable. Justified by
  DIRECT fruit value only (B3.8 closed the scaling rationale), and must budget for the
  trigger-independent family/tail cost both D173 variants paid. Design only after B3.9.

## Tier 4 — arena protocol (standing, entered only by qualified candidates)

- **B4.1 Promotion protocol v3** — capacity A/A (control must reconverge within noise of
  its prior bracket) → candidate submit → mandatory +20/+35/+50-minute reads → delta vs
  same-window control with the frozen bands (≥ +0.5 KEEP, ≤ −0.5 revert) → restore exact
  resident on any failure. [arena-queue policy v2 + 07-16/07-18 Legend amendments]
- **B4.2 Bar tracking** — with each authorized read, record rank-3 score and top-3 battle
  counts (maturity context) in STATE §1.

## Tier 5 — infrastructure (pull in only when it blocks)

- **B5.1 ✅ DONE 2026-07-28** — TWO broken frozen bins found and feature-gated (d35c +
  the d36 oracle nested in its file; sources untouched, proof via identical error counts
  under the features). `cargo test --workspace`: **1,312 passed / 0 failed / 19
  ignored** — first green workspace in weeks. Commit `83bf5c0`; cap rule applied after
  the 29 GB test build (target back to 2.0 GB, release lib intact).
- **B5.2 ✅ YT tranche mirror** — done as part of B0.2 (plan Task 5, md5-verified).
- **B5.3 (re-scoped 2026-07-28): cold-file migration only; the LIVE games store stays
  local.** Rationale: the daily collection cron writes into `data/raw/games/` at 05:17 —
  symlinking the live store to the sometimes-detached USB drive would turn every
  drive-absent morning into a failed collection and permanently lost stream games
  (windows rotate). Instead: periodically migrate games older than ~30 days per-file
  (copy-verify-symlink), keeping the hot store and all indexes local. Low urgency at
  2.4 GB on a 900 GB NVMe. *(Ripeness checked 2026-07-28: oldest file is 07-03; zero
  files cross the 30-day threshold — first actionable window ≈ 2026-08-03.)*

## Recommended order

B0.1 → B1.1 → (B1.2 if warranted) → B2.1 gate → B2.2 → B2.3; B0.2 and B3.1 interleave as
fillers; B0.3/B4.x standing. Honest odds, **revised 2026-07-27 after B0.1**: the maturity
lever is largely dead — the ladder recomputes fresh-agent scores rarely (score frozen 4+
days), so visible-rank recovery cannot be assumed from waiting. Top-3 requires B2 to
succeed where thirty-odd offline selectors failed — the closed-loop objective is the one
untested lever the evidence still permits — and any promoted candidate must additionally
survive the same slow-recompute regime (mature reads will take days, reinforcing B0.3's
no-churn rule).
