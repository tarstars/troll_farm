# 20260816-h-starve-1-standing-troll-audit: why does a troll stand doing nothing for 150+ turns?

- Status: open — OWNER-APPROVED 2026-08-16 as a PARALLEL track ("Yes").
  **Increment 1 DELIVERED 2026-08-16** (claude_1, artifact `4fc5439d`): on the 2
  specimens measured (OSC-001, OSC-012) **the suspected commitment mechanism is NOT
  witnessed** — the parked unit routes through the MAIN planner every observed turn
  (195/195, 193/193), zero regeneration commitments, candidate lists non-empty but
  every candidate WAIT. claude_1 refused the `NO_WORK_ON_MAP` label (that would read the
  generator's output as a fact about the world) → labelled `ALL_WAIT_CAUSE_UNDETERMINED`.
  Non-interference verified on OSC-001 (byte-identical command streams; runner voids the
  table on divergence). **Table NOT trusted yet — codex_1 instrument review pending
  (charter gate);** author-named limits: non-interference checked on the first situation
  only; commitment acquisition before the window start is unobserved. **Increment 2
  (approved direction): read the world-state predicate `fuzz_panel.work_remaining`
  (:1756) to split `NO_WORK_ON_MAP` vs `GENERATOR_GAP`** — that is the increment that
  answers the owner's actual question. Two specimens are not a population; the
  ~24-specimen sweep continues, the commitment mechanism may still appear elsewhere.
  **Increment 2 DELIVERED 2026-08-16** (claude_1, `f44fecf6`): world-truth check via the
  panel's own `work_remaining` (:1756); claimed **GENERATOR_GAP 3/3** (OSC-001/012/031 —
  world offered work 195/193/190 turns while the unit was handed only WAIT).
  **codex_1 review: headline NOT ESTABLISHED**
  (`codex_1/reviews/h-starve-1-increment2-cause-review-2026-08-16.md` @ `7273bb2f`):
  (a) **OSC-031 audits the wrong unit** — the P4_STALL anchor is unit 0, the audit
  reports unit 2; **independently confirmed by the integrator against the frozen
  library** (`OSC-031.json window/unit = 0`) → row WITHDRAWN; (b) OSC-001/012 keep
  their accepted raw facts (MAIN, no commitment, all-WAIT) but the player-level
  predicate cannot prove work reachable by the PARKED unit (multi-source BFS over all
  own units; work reachable only by the dancer still counts) → **cause remains
  UNRESOLVED**, per-unit reachability could move rows to `NO_WORK_ON_MAP` (walled-off
  geometry is plausible in these corridors). claude_1 pre-flagged (b) in the handoff;
  (a) it did not. **Instrument revision REQUIRED before the full table**
  (`…increment1-instrument-review-…` @ `3bd155b9`, five defects): select the explicit
  D1 blocker / P4 stalled anchor rather than every non-window unit; exact
  one-row-per-turn coverage; log candidate kinds + chosen directly; non-interference on
  EVERY specimen; stderr backpressure — plus label-specific negative controls before
  layering `work_remaining`. **Table UNTRUSTED.** Next: repair the five defects, then
  increment 3 = per-unit per-turn reachability (BFS from the parked unit's cell) with
  negative controls. **Integrator quarantine note:** claude_1's T-1 cross-implication
  (these rows likely un-fixable by transport; the registry's 25 possibly optimistic) is
  a NAMED HYPOTHESIS for the owner session only — the prediction registry stays frozen,
  nothing is re-scored on an untrusted table.
  **Increment 3 DELIVERED 2026-08-16** (claude_1, `f5a9d2e9`, **crossed in flight** with
  the increment-2 adjudication and codex reviews — it cites neither): per-unit
  refinement `unit_offered_work()` (BFS from the parked unit's own cell); claims
  GENERATOR_GAP survives on all three (unit itself could reach work 195/193/190 turns,
  still handed only WAIT). **Integrator verification:** the faithful-narrowing claim
  HOLDS — both predicates read side by side, same two clauses, same static-walkable
  `game::nav`-mirror BFS (`trace_detectors.bfs_distances`), only the source set differs.
  **But: (a) the OSC-031 row still reports `parked_unit: 2`** — the wrong-unit defect
  is UNREPAIRED (selection logic unchanged), so **the OSC-031 withdrawal STANDS and the
  honest count is at most 2/2 (OSC-001/012), pending review**; (b) none of the five
  instrument defects are addressed; (c) the new `UNIT_CANNOT_REACH_WORK` arm has never
  been observed firing (observed-failing rule) — a walled-in negative control is
  required. **Adjudication 2026-08-16 (integrator): no discipline breach (parallel
  composition), but no ruling moves** — critical path stays: five repairs +
  label-specific negative controls (incl. the walled-in control) → codex_1 re-review of
  increments 2+3 together → re-run so numbers land on the RIGHT units → only then owner
  session. Named review question for codex_1: both predicates ignore unit-blocking by
  design; whether the bot's own candidate nav does too decides if transient blocking
  could excuse the generator. Generator-fix charter, if any, is an OWNER gate — not
  spawned on today's table.
  **CORRECTION + increment-3 review, 2026-08-16 late — standing state: 2 solid raw rows,
  ZERO cause labels established.**
  claude_1 SELF-CAUGHT an instrument divergence (correction `20260816T162300Z`,
  artifact `f6e628c9`, supersedes both increment handoffs): broadening non-interference
  to every situation exposed (a) a stderr pipe-buffer deadlock silently TRUNCATING the
  command stream (fixed: drained on a thread — repair #5 landed) and (b) after that fix,
  a **print-only build still changes a decision** (`DROP 0` vs resident `CHOP 0`),
  unisolated — the audit now structurally refuses to emit a table if ANY situation
  diverges (repair #4 landed). OSC-031 row withdrawn by author (divergence) — now void
  on TWO independent grounds (wrong unit, still unengaged by claude_1). Its "2 of 2
  validated" headline was superseded within minutes by **codex_1's increment-3 review**
  (`…increment3-reachability-review…` @ `0785882f`): static BFS matches the bot's
  occupancy-blind nav (settles the integrator's review question), BUT **capability
  kills the labels** — OSC-012's parked unit has `harvest_power 0 / chop_power 0`
  (pure carrier; a reachable plant offers it NO action) and OSC-001's is harvest-only
  (needs per-turn fruit-state join); cargo needs a reachable legal sink. **Both
  capability facts independently confirmed by the integrator against the frozen
  library.** Required: per-unit/per-turn ELIGIBLE-ACTION oracle + capability/
  disconnection negative controls before relabeling anything.
  **Adjudication 2026-08-16 (integrator):** correction ACCEPTED and credited (fastest
  self-catch of the day; structural enforcement is the right shape). Headline ledger for
  honesty: 3/3 → confirmed 3/3 → corrected 2/2 → actual **0 established**. **Publication
  gate ENFORCED (existing charter, not new law): cause labels appear in owner-cc'd
  handoffs only after the producing instrument has codex_1 acceptance;** instrument and
  raw-data handoffs flow freely. Critical path: repairs #1 (anchor unit — restated a
  THIRD time), #2 (one-row-per-turn), #3 (candidate-kind logging) + divergence isolation
  (bisect `hs1_branch` vs `eprintln!`) + eligible-action oracle + controls → codex_1
  re-review → re-run on correct units. Open questions to claude_1: enumerate ALL
  divergent situations under the broadened check (message cites OSC-002 in "Known"
  while the table voids OSC-031); state the run set behind "2 of 2" given the
  table-void rule. **Cross-track hazard flagged: a print-only patch changing behaviour
  threatens EVERY instrumented-build methodology (P-1 packet capture included) — the
  mechanism must be isolated, not worked around.** T-1 implication: weakened by
  author's own correction; stays quarantined.
- Code owner: `claude_1` (builds on its own stage-1 re-run machinery) · Reviewer: `codex_1`
  · Integrator: `local_claude_1`
- Priority note: the grader repair (T-1 stage-1 reopen) stays first; this interleaves with
  T-1 fix stages at claude_1's judgment. This is the only score-shaped thread on the board.

## The hypothesis (H-starve-1)

In the long oscillation episodes the real cost is not the dancer but the BLOCKER: a troll
idle (wait fraction ~1.0) for 150–195 turns — half the workforce parked. Suspected cause:
a stuck persistent "regeneration commitment" routes the troll to the ENDGAME candidate
generator mid-game (readable `:1396-1398`); holding no fruit, it gets an empty/WAIT list
every turn and never escapes. If confirmed and fixed, un-parking a worker for ~2/3 of a
game in ~13% of games is real score — unlike the dance fix (+0.045). This is the leading
candidate explanation for the −13.6-below-par mystery (deep-dive deliverable D6).

## The measurement (Packet-lite slice; no cure in this task)

Instrumented build (separate build only; resident byte-exact) over the stage-1
deterministic re-runs of all idle-blocker situations (M1-idle + all M2 + the 4 P4 stalls,
~24 specimens): per turn, for the idle unit, log (a) routing branch taken
(early/main/endgame; commitment flag state), (b) candidate list summary (count, kinds,
chosen), (c) the commitment map. Output: per-situation cause label — e.g.
STUCK_COMMITMENT / NO_WORK_ON_MAP / GENERATOR_GAP / OTHER — with the evidence line.
Grouped cause table goes to the owner session (rulings per cause, not per case — owner
ruling of 2026-08-16). Every new check observed failing first; this doubles as P-1's
candidate-enumeration slice and must be labelled a SLICE, not packet completeness.

## Boundaries

No cure code in this task (the fix, if any, is chartered separately on the audit's
result). No resident mutation, no Arena, no tuning against the prediction registry.
