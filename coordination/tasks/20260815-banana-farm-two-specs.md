# 20260815-banana-farm-two-specs: write specifications A (unconditional) and B (conditional) for the banana-farm bot

- Status: **v11 in codex_1 re-review** (v10's two operational contracts closed +
  claude_1's citation-precision fix). Prior: **v10 in codex_1 re-review** (v9's three evidence-contract blockers closed:
  frozen census generations; D-1+P4 double backstop; log-until-resolution). Prior:
  **v9 — FIVE owner rulings carried; latest:
  LOG-AND-DEFER on the suppression corners (no prevention machinery; logged
  context; panel de-novo gate as backstop).** Prior: **v8 — FOURTH owner ruling:
  NO PLANTING DURING DENY; exclusion machinery deleted.** Prior: **v7 in codex_1 re-review** (v6's owner rulings unchanged; v7 closes codex's
  v6 constructed case — census-eligible round progress — and gives the exclusion
  tracker its own contract). Prior: **v6 — OWNER RULED ALL THREE DECISIONS 2026-08-17 (B-1 no floor; K_futility
  RETIRED; futility = the owner's census-sequence design, completion gate subsumed).
  v6 in codex_1 re-review of the new mechanism text; then owner FINAL confirmation.**
  Prior: v5 GATE_ACCEPTED_FOR_OWNER_REVIEW (codex_1, 2026-08-17T10:00Z) — AWAITING
  THE OWNER: B-1 floor, K_futility freeze, completion gate adopt/strike. No
  implementation before owner approval AND the programme's oscillation gate.**
  Prior: v5 delivered (`3cc51122`) — in codex_1 re-review (7b), then
  owner approval with THREE decision items: B-1 floor, K_futility freeze, completion
  gate adopt/strike (ruled in-scope but a new owner decision by codex v4 review;
  operational definition added in v5).** Prior: v4 `96f1b400` REVISION_REQUIRED on
  two gaps (register entries; operational confirmation definition) — both closed. Both blocking corrections addressed: abort sensor
  characterized in BOTH directions (wood masking, `WOOD_POINTS=4`) + per-event score
  decomposition reporting; K_futility relabelled heuristic + completion gate (≥1
  completed focus-chop per non-decrease run) + gate GK; shared skeleton §3–§8
  re-verified byte-identical. One open scope question to codex_1: whether the
  completion gate stays within textual/test-gate scope or joins the owner list.
  Previous status for history: v3 REVISION_REQUIRED (codex_1, 2026-08-16T06:00Z) —
  revision owed by local_claude_1, then codex_1 re-review, then owner approval. Review:
  `codex_1/reviews/banana-farm-two-specs-v3-review-2026-08-16.md` @ `701a3802`. Two
  blocking corrections, both textual/test-gate, no design reopening: (1) score-delta
  abort bias is NOT one-way-safe — total score includes wood (4 pts vs banana 1), so
  our wood production can mask enemy banana gain and make the abort fire late or
  never; characterize false positives AND negatives, measurement reports both;
  (2) K_futility=10 is a HEURISTIC, not a bound — label it so and add a constructed
  case where a legitimate long in-flight denial chop is not mistaken for futility (or
  supply the missing bound). M-1 arithmetic confirmed correct (SE 0.9493, bar 1.8606).
  **Integrator record correction 2026-08-17: this verdict sat unread ~26 h while the
  integrator reported the review as outstanding; the block was the integrator's, not
  codex_1's** (details in `coordination/ITERATION.md` log). Pool item 7a.
  Previous status line follows for history:
  DRAFTS DELIVERED 2026-08-15 — awaiting codex_1 review, then owner review.
  Files: `docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md` and
  `…-spec-b-conditional.md`. Shared skeleton verified byte-identical (§3–§8); the only
  difference is the FARM entry predicate. Three OWNER-DECISION items flagged inside
  (A-1 entry anchor, B-1 no-turns-floor, A-2/B-2 first-night pairing). Notable finding:
  the "farm when denial ends" reading of Spec A collapses into Spec B, since the denial
  gate expires exactly at the enemy's third troll — Spec A therefore enters at own
  second-troll materialization (D89a's proven activation point).
  Originally: stage 4 of `docs/PROGRAMME-banana-farm-2026-08-15.md`; may run in
  parallel with the oscillation deep-dive (paper work, no code), but implementation
  (stage 5) waits for the oscillation gate (stage 3).
- Record owner / integrator: `local_claude_1`
- Reviewer: `codex_1`
- Owner gate: owner reviews BOTH specs before any implementation
- Created: 2026-08-15
- Authority: owner decision 2026-08-15 — "let's write down two specifications"

## ★ OWNER RULINGS 2026-08-15 (session with local_claude_1) — Spec A REDEFINED

The drafted Spec A ("farm at second-troll materialization, overlapping denial") read to the
owner as "throw out denial, plant bananas instead" — a bad bot by expectation. It is DEMOTED to
collection candidate **Spec A0** (kept on paper, expected poor, may be measured someday).

**The real Spec A is the owner's state machine, all transitions latched one-way:**

COLLECT → (own second troll trained) → DENY → **(enemy 3rd troll OR no selected-species tree
left OR selected-species count sustainably non-decreasing over K turns)** → FARM → (S-1 abort
sensor) → WOOD.

Rulings recorded:
- Denial is suspected load-bearing for rating (supported: N6's weak arm lost −0.754, both
  seats) and is PRESERVED in full until a doorway condition fires.
- The two new doorways are the owner's denial STOP conditions, stated in writing for the first
  time: job done (species eliminated) or futility (enemy sustains the species against our
  chopping). Futility is measured by the SIMPLE tracker: count selected-species trees;
  sustained non-decrease over K turns while we actively deny = futile. No ownership inference.
  (The bot's sole PLANT site :1256 can briefly plant a carried lemon/plum in endgame
  conversion; the K-persistence absorbs such blips.)
- "3rd troll ends denial" KEPT for now — composite condition; whether denial should continue
  against a 3-troll enemy is an explicit LATER experiment, not this one.
- State-machine reading accepted with its risk: we may leave denial incomplete. Owner: "I'm
  ready to take this risk."
- Timing framing: FARM replaces the aggressive-chopping fallback that today follows denial.
- Containment property to preserve in the rewrite: **Spec B = Spec A with only the 3rd-troll
  doorway** — the A-vs-B measurement prices exactly the two new doorways.

**S-1 RULED 2026-08-15: both-in-collection.** Build the SCORE-DELTA sensor (b) now —
snapshot both scores at FARM entry; abort to WOOD when enemy score grows faster than ours
for K consecutive turns after warmup W. The PROVENANCE sensor (a) stays fully specified in
the spec as the named future variant (faithful to the literal per-farm rule; adopted only
if measurement shows (b) aborts too often). Owner phrasing supporting (b): "more profitable
for the enemy than for us" is an overall-profit statement.

**M-1 RULED 2026-08-15 (final of the five owner decisions):**
- **Procedure:** interleaved ABABABABAB, one submission per ~2 h (a mature 160-game read
  settles in ~2 h, measured 2026-08-12), one block ≈ 20 h.
- **Verdict object:** the 95% confidence interval of the PAIRED difference (adjacent A/B
  pairs averaged — drift cancels within pairs), never two separate per-bot intervals.
- **Rule, n-independent:** winner when |Δ| ≥ 1.96·SE(Δ), SE(Δ)=σ√(2/n), σ=1.501
  (n=5: ≈1.9 pts; pooled n=10: ≈1.3); **materiality floor |Δ| < 1.0 → stop as
  immaterial** (fixed in points by design — the standing value bar, not a statistical
  bound); between → extend one ABAB block, **max two extensions** (30 runs, SE≈0.55),
  then the floor forces the stop.
- **Honesty clause:** campaign reports its own empirical paired-difference spread beside
  the planning σ; gross disagreement = "re-measure σ" flag, never a license to choose
  the flattering number.
- **Night-1 pairing: Spec A vs current resident** (`98628e98…`). A-vs-B (pricing the two
  new doorways) runs only if A earns it.

Spec files rewrite to the full ruling set (Spec A state machine, S-1 score-delta with
provenance variant, M-1) is now UNBLOCKED — one revision pass.

## The owner's sequence (both specs share it) — superseded by the ruling above where they differ

gather resources → train the second troll → select lemon or plum → deny (chop) the
selected species near the enemy → banana farm → **abort** to aggressive all-out chopping
when the enemy collects more from our farm than we do.

- **Spec A — unconditional.** Farming follows denial as the normal course of the game.
  Prior art: D89a blueprint
  (`data/analysis/live-agent-6553250/d89a-banana-seed-factory-blueprint-2026-07-21.md`),
  mean +79.441 margin, catastrophic tail (worst pair −235).
- **Spec B — conditional ("if third troll").** Enter farming only when the enemy fields a
  third troll. Prior art: the CBF design
  (`docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`) with its latched
  DENY → FARM → WOOD machine, warm-up 30 turns / 5-consecutive-turn abort persistence.

## Requirements on both specs

1. **Base:** the readable resident `98628e98…` (`cgauto/submissions/
   submitted-agent6593838-readable-no-orchard.rs`). The 2026-08-07 CBF spec must be
   RE-BASED: its line references and grafting plan target the old compact file, and the
   readable base has no orchard code left, so D89a mechanics come in fresh.
2. **Standing owner rule:** no banana action before our second troll is trained
   (threshold zero). Spec A must show its entry condition satisfies this.
3. **Abort sensor:** state exactly what is measured (banked-banana deltas per the CBF
   spec, vs total-score deltas as the named variant) and why; frozen constants, no tuning
   dials.
4. **Shared skeleton:** the two specs must be written so stages share code — one state
   machine, one farm, one abort; only the FARM entry condition differs. Say explicitly
   which lines differ.
5. **Anti-oscillation:** transitions latched one-way in both; the denial bonus follows the
   machine state, never the live troll count (no silent re-enable).
6. **Behavioural acceptance gates** per spec (train / deny / sustained farm cycle / abort
   fires AND does not misfire / byte-identity where the machine has not left its first
   state / monotonicity), inheriting Banana R2's lesson: implementation-validity gates and
   observed-failing tests precede any value panel.
7. **Measurement plan stub:** one night = 8 mature runs = 4 per arm interleaved A/B
   resolves ~2-point differences (σ = 1.501); state which comparison the first night buys
   (A vs B, or winner vs resident) — owner decides the pairing at stage-6 go-ahead.

## Out of scope

Implementation, panels, candidates, Arena. The D89a leak (opponent gained even more than
we did) is bounded by design, not repaired — `NOT_REPAIRABLE` verdict stands unappealed.
