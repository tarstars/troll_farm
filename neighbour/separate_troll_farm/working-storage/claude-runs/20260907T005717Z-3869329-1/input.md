# First-hire wood investment with realistic capacity and collection cost

Budget50 minutes. NEW claude_candidate_hirewood* family/tests only. Parent/canonical/
other families/neighbor unchanged. Offline only, no platform/commits/agents/holdout.
Read CLAUDE.md/EVALUATION.md and use existing source/evaluation helpers.

Lumber run20260907T003456Z-3804114-1 tied170points,0issues,slightscore gain; do not
promote. Primary found its key board fixture ms1 cc4 hp1 chop1 although the actual
starter is cc1. Gross tree-size/damage ratio is not banked return when capacity caps
wood; source uses min(size,freecapacity), so the cited starter weakness isn't proved
addressed by its maturity discount. Do not claim growth is always advantageous or
repeat the capacity4 fiction. A fixture for cc4 has only that narrower scope.

Target the measured first-hire investment instead. Saved official901697520: ours
TRAIN2/2/0/2 atturn8, tonigineer2/2/0/3 at18. Latest field ledger says actual trained
worker wood/chop .50 vs .65 (verify per-unit/banked accounting from existing ledger,
not gross tree size). Both have2workers; a higher chopping investment is a plausible
mechanism, not proven from this single observational comparison. Parent has bank-side
regeneration already; don't invent its absence or add an idle-only wrapper.

Implement ONE map-aware first-hire spec-selection improvement aimed at banked wood
throughput net of resource acquisition, delayed hire, training fruit expenditure
and finite forest access. Inspect current opening_objective/selection/funding code,
then replace the relevant decision coherently. Compare real movement/carry/chop
tradeoffs; harvestpower may remain parent's0 for this wood-only study. Greater chop
is not automatically better, and initial iron resources are finite even if worth0
points. Include actual growth-aware felling cost, min(size,freecapacity), travel and
return/banking. No arbitrary max-stat purchase or unrelated policy bundling.

Keep funding decisions stable while collecting a chosen bill, with justified abort/
fallback rather than stock-dependent oscillation. One deterministic selection rule,
prospective PLAN with actualdate-u before measurement, no parameter sweep. Runnable
candidate must actually change a first-hire decision under a realistic field-like
resource state; no fully prepaid late-hire stand-in or cc4 starter fixture.

Real controller+referee tests: acquire missing iron/fruit when investment justified,
pay exact bill, spawn correctstats, obtain/bank real wood; demonstrate a case where
extra power repays delay and another where baseline fast-hire wins/fallback applies.
Use real initial1/1/1/1 and capacity-limited yields. Check late/barren/blockedreturn,
opening target stability, no invalid jointmoves. Primary reviews causal scope.

Frozen parentpolicyflat SHA25695ee691ee1b26e074ac90851575a6a56d5b0bec738ff3851cd141585d85c6d23.
Exact standalone<=100000UTF16, absoluteRust1.90, explicit run-local cargo target-dir
and actual artifact hashes; guarded pruning ifneeded. Serial16stream<50ms and exact
readable/compact equality FIRST. Then one192pairs9947500..9947507,12opponents,both
seats, ALLOW_ANY_MAP_SEED=1 set beforelaunch; baselinearrays must match gap210944Z.
Fixed positive whole-panel W+0.5D AND zero allcandidateissues gate. Allfailures stay
in denominator; report fullmetrics/per-opponent and actualfirst-hire activation.
One heavyjob at a time, collectPIDs/preservefailedlogs; PROGRESS realstages.
RESULT<=400words: changed investment rule/hashes, realistic proof, checks/paired
result, evidencepaths, limitations, one next action. No additional audit framework.
