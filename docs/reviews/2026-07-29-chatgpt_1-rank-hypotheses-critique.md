# Review of `docs/rank-hypotheses-2026-07-29.md`

Reviewer: `chatgpt_1`  
Base: `session-2026-07-01` at `a50276b5e0f5b33dcef1965723707269222e7037`  
Scope: read-only critique; no resident, experiment, sealed-data, or Arena changes.

## Executive verdict

The document is useful and unusually honest about closures, but its ordering is wrong.

- **Best immediate work:** H5, H3, H8. These are cheap read-only audits that can invalidate expensive programmes.
- **Best strategic route:** H2. It is not merely another hypothesis; it is the direct consequence of the terminal synthesis: the current architecture is closed, so a new coherent bot is the remaining high-ceiling programme.
- **Do not run H1 as proposed.** It bundles four closed levers into one 256-map experiment. A failure would be uninterpretable; a success would not identify which complement is load-bearing. It is effectively an under-specified Architecture-2 graft, not a clean first experiment.
- **H7 is mechanically misstated.** Enemy units do not body-block or path-block our units; move collisions resolve per player, and opposing units may share a cell. Replace it with an audit of cross-player *action* interference (shared harvest/chop, race, duplication), not physical blocking.
- **H9 and H12 are operations, not rank-improvement hypotheses.** H9 is a risky measurement prerequisite; H12 is already-active maintenance.
- **H11 is near-closed.** It cites opponent-family failures as map evidence and conflicts with D63's failed static map-feature selection.

The portfolio should distinguish three categories instead of ranking all twelve on one axis:

1. **Read-only falsification:** H5, H3, H8, revised H7, audit-only H4/H6/H11.
2. **Owner programme decision:** H2; possibly a redesigned H1 only as an Architecture-2 prototype.
3. **Operations/maintenance:** H9, H12.

## Current-state correction

This review uses `docs/STATE.md`, not the obsolete July-10 champion line. The live resident is agent `6561795`, source `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, last recorded rank 43/110 at 21.97. The terminal synthesis says the current architecture's improvement space is closed after D170b, D172a, D173a/b, D174a, D175a, B3.6, and B4.6.

The hypothesis document says ~43/112 and later mentions league 110→112. That pool-size datum is not aligned with the current STATE snapshot; future revisions should cite one timestamped snapshot and avoid mixing pool counts.

## H1. Joint economy package — **reject as the first experiment; redesign or merge into H2**

The complementarity argument is real: D173, D174 and D175 each exposed a missing complement. But the proposed test is not scientifically clean.

Problems:

1. **Four simultaneous changes destroy attribution.** The package changes worker capability, roster cap, planting priority, and banking. If it loses, we learn nothing about whether the idea is wrong or one component dominates negatively. If it wins, we still do not know the minimal causal package.
2. **It reopens four closed classes with a smaller panel than the closures used.** D173 used 2,048 paired episodes and D175 used 4,096. A 256-map four-way bundle with family/tail gates is an optimistic power reduction without justification.
3. **`banking support` is undefined.** The exact job, trigger, resource, ownership, and collision semantics must be specified before freezing anything.
4. **The package may reproduce prior composition failures.** D92 and the earlier re-architectures show that coupling plausible parts does not automatically close the economy loop.
5. **It is architecturally inconsistent.** Adding four subsystems to a suppression-first policy while retaining its old scheduler is exactly the graft pattern the terminal synthesis rejects.

Better path:

- First construct a **read-only joint upper bound** on existing official states: actual training bill, crop creation, harvest capacity, and bankability under the proposed package.
- If the bound is material, use a staged factorial/funnel: capability+planting, cap+real funding, then the full package on a fresh held panel. Do not tune failed arms.
- Prefer implementing the complete loop as the first Architecture-2 baseline rather than contaminating the resident.

Verdict: high ceiling, low interpretability, too risky for D176 as written. **Demote below H2.**

## H2. Architecture-2 — **approve as the main strategic programme**

This is the strongest high-ceiling proposal because it follows the repository's terminal conclusion instead of arguing around it. The resident stays untouched while a coherent economy is designed from turn one.

The proposal needs harder milestone gates:

1. Reproduce referee and resident evaluation parity before optimizing.
2. Match resident equal-roster performance and tail safety.
3. Demonstrate early bounded production, nonzero own-crop reap, and actual fruit-funded training in one closed-loop scheduler.
4. Demonstrate survival against 3–4-worker opponents, not merely higher own production.
5. Require same-panel dominance before any Arena discussion.

The design target must be **behavioral invariants**, not direct imitation of a named bot: early planting, bounded live crops, harvest-capable labor, transactional bills, immediate legal TRAIN, and suppression that remains coordinated with production.

Verdict: **promote to the primary owner decision.** The six previous rebuild failures lower the prior, but they do not close a new representation built around the newly measured invariants.

## H3. No-loop quartet — **approve; highest-priority repository audit**

This is the best cheap hypothesis. It tests whether the terminal narrative is too broad by studying stronger agents that apparently share the resident's two-worker/no-loop macro shape.

Required controls:

- Match by opponent workforce, opponent identity/strength, seat, map, and game duration.
- Revalidate the `no-loop` label from commands and crop fates rather than aggregate rates.
- Separate policy value from maturity/matchmaking-pool effects.
- Compare specs, carry capacity, tree-size mix, banking latency, target provenance, and score trajectory.

The claimed 35-point 2v3 survival gap is descriptive until these controls hold. Still, either result is valuable: a transferable execution mechanism or proof that the quartet is not a causal peer group.

Verdict: **run first or second, in parallel with H5.**

## H4. Opponent-scaling denial — **audit only; experiment is premature**

The warning signal is strong, but `opponent reached worker 3` does not imply that a cheap deniable bill remains available when we observe it.

The first step must answer:

- What exact PLUM/LEMON/APPLE/IRON bill was paid?
- Which source cells or banked units supplied it?
- Which of those resources were reachable and contestable by us before payment?
- Would the required denial action displace higher-value suppression or banking?
- Is the opponent's supply redundant enough that removing one tree/fruit changes nothing?

The distinction from Phase 21 is not yet established. A timed global bonus can still be the same closed scoring intervention with a narrower clock. Only proceed if a read-only deniability census shows material bill mass that one available action can causally remove.

`Iron-source interference` is also underspecified and must be grounded in referee mechanics before being treated as a lever.

Verdict: **keep as a diagnosis, not a candidate.**

## H5. Top-player postmortems — **approve; do immediately**

This is the best cost-adjusted item. It can falsify the project's inferred model before more expensive work.

Cautions:

- Public postmortems may describe contest-final code, not the current practice-ladder resident.
- Authors often report high-level intent rather than the exact scheduler, bill, or failure modes.
- Absence of a postmortem is not negative evidence.

Use published descriptions to generate or reject mechanisms, then check them against replays and referee rules. Do not treat prose as a ground-truth implementation.

Verdict: **priority 1.**

## H6. Targeted subgame lookahead — **promising audit, but the premise is not yet proven**

The proposal assumes the size-at-felling and kind-mix gap is caused by one-ply greed. B4.6 does not prove that. The gap can arise from worker specs, capacity (`cc=1` performs many fells), role allocation, or the global schedule.

Also, lookahead does change effective behavior even when it uses the same terminal metric: horizon, rollout policy, and terminal approximation become a new objective. A 2–3-ply horizon may be too short for growth, banking and opponent response.

Correct first step:

- Sample real resident decision states where the live scorer chose size-1 or low-value trees.
- Compute an exact or high-fidelity bounded continuation over a carefully limited action set.
- Measure oracle disagreement value, family breadth, and worst-case latency before implementation.
- Reject if the upper bound is small or concentrated in consumed states.

Verdict: **good read-only execution audit; implementation only after a material oracle gap.**

## H7. Physical interference — **reject as stated; replace with action-interference audit**

The mechanic premise is wrong. `docs/mechanics.md` states that movement collisions resolve separately for each player and enemy units may share cells with ours. Therefore enemy body-blocking, door camping, and path denial do not physically block our movement in the usual sense.

What is real:

- cross-player co-location on harvest/chop targets;
- last-fruit duplication;
- shared chopping/race timing;
- target disappearance and wasted travel;
- our own intra-team door/path conflicts, already studied by motion/B3.6 work.

A revised hypothesis could audit whether strong agents deliberately exploit **action contention** or co-location timing. Do not build a body-blocking controller.

Verdict: **rewrite before any work.**

## H8. Worker-2 timing — **approve; high-priority cheap audit**

This is one of the cleanest open questions. D160/D174 focus on worker 3; a five-turn worker-2 lag can be an execution or intentional-economy effect.

The audit must distinguish:

- actual bill affordability;
- TRAIN legality and shack occupancy;
- travel/door evacuation;
- resource reservation for the resident's opening;
- whether an earlier worker would have a productive legal job;
- counterfactual cost of consuming the bill earlier.

If the bill is affordable and TRAIN legal at turn 2 but the scheduler waits until 7–8, this becomes a rare execution-class candidate. If not, the hypothesis closes cheaply.

Verdict: **priority 3, ahead of any new economy experiment.**

## H9. Identical-source A/A — **remove from the hypothesis portfolio**

This cannot improve the bot. It only reprices a source on the current pool and carries a known multi-day standing cost. STATE explicitly forbids churn and records a failed same-code A/A.

Use capacity A/A only as the mandatory first phase of an already-authorized promotion protocol. Do not spend standing merely to answer curiosity about the current absolute score.

Verdict: **operations prerequisite, not an experiment; no standalone run.**

## H10. Spatial-planes learner — **valid sanctioned long shot; low prior**

This is the only clean reopening named by D172a, so it belongs on the shelf. However, the claim that incremental cost is small is too optimistic. It requires a new spatial observation pipeline, model/training path, exact parity checks, runtime/size validation, and blockwise held evaluation.

Use the existing exact labels and preserve every D172 gate. Do not touch the sealed panel unless a frozen successor protocol authorizes it. A cheap spatial probe or small frozen architecture comparison should precede a full GPU programme.

Verdict: **allowed, but behind H3/H5/H8 and the H2 owner decision.**

## H11. Map-conditioned configuration — **near-closed; evidence is currently misclassified**

The proposal cites `compact_gold` failures as map-structured evidence, but `compact_gold` is an opponent family, not a map class. That does not establish map-conditioned value.

More importantly, CONSTRAINTS records that static opening/map features failed workforce-policy selection: discovery AUC 0.830 fell to validation 0.479 (D63), and D91's map selector lacked support. A new global map gate is therefore close to a closed branch.

A read-only decomposition is harmless if it:

- conditions jointly on opponent family/roster and map;
- uses out-of-map held blocks;
- tests a pre-existing causal variant rather than correlating score with map richness.

Reopen implementation only with a new representation or replicated conditional treatment effect, not another richness threshold.

Verdict: **low-priority audit; do not present as a likely candidate.**

## H12. Pool-drift surveillance — **keep as maintenance, not a rank hypothesis**

The cron and maintenance posture already implement this. Weekly summaries can correct stale facts and trigger a written reopening, but they do not directly improve rating.

Define explicit triggers (new agent with repeated same-source dominance, material cohort-shape change, or rank-bar movement) so surveillance does not become endless archaeology.

Verdict: **sensible standing operation; remove from the ranked experiment list.**

## Corrected sequence

### Immediate, parallel, read-only

1. **H5** — public postmortem/source search.
2. **H3** — controlled no-loop quartet audit.
3. **H8** — worker-2 affordability/legality/timing audit.
4. **Revised H7** — action-contention audit, only if H3 points there.
5. **H6** — bounded-lookahead upper-bound audit.
6. **H4** — opponent-bill deniability census.

### Owner decision after those results

7. **H2** — Architecture-2 programme. This is the highest-ceiling route.
8. **Redesigned H1** — only as a staged Architecture-2 prototype or after a positive joint upper bound; never as the proposed four-change resident bundle.
9. **H10** — spatial learner long shot if the owner prefers a learning route.
10. **H11** — only if a robust map-conditioned treatment effect appears.

### Not experiments

- **H9:** promotion-runbook prerequisite only.
- **H12:** maintenance surveillance.

## Integration recommendation

Do not replace `docs/rank-hypotheses-2026-07-29.md`; preserve it as the integrator's proposal. Add this review beside it and update the backlog pointer to distinguish:

- `audit-ready`: H5, H3, H8;
- `needs rewrite/preflight`: H4, H6, H7, H11;
- `owner programme`: H2, possibly redesigned H1/H10;
- `operations`: H9, H12.

No new candidate or frozen experiment should be opened from H1 until the integrator resolves the H1-vs-H2 architecture boundary.
