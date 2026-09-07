# Phase 0: what already exists, and what remains unproved

2026-09-07; chatgpt_1; task 20260907-two-project-analysis-and-plan, extension E2. Read with RECHECK-2026-09-07.md. Evidence pins: M = tarstars/troll_farm@67b2acc1e828cf25a7e6e76c2814dfcd3268a45c; N = tarstars/separate_troll_farm@badf27efee7eca794c149f0707c087f7ed1eb0ff; W = M:neighbour/separate_troll_farm/working-storage/.

## Decision

**DUPLICATE_HYPOTHESIS for the proposed generic TURNOVER programme.** Standalone allocation, remembered crop ownership, mixed fruit/wood jobs, same-kind refill and seed transactions have already been implemented in several combinations. Their existence is not proof that every invariant is correct, and their losses are not proof that productive orchards cannot win. It does mean that another controller justified only by those feature names is not a new experiment.

The narrower native-policy reconstruction remains **UNKNOWN**, not disproved: the native transitional flag, second flag and target semantics have not been recovered to an executable specification. Merely adding an unknown native label is not a falsifiable replacement programme either. Do not authorize a fresh generic rewrite from this audit.

**Next hypothesis: supply promised by a funding plan is not protected by the commands that actually execute.** Inspect the retained complete-funding trace, including which player destroyed which species, before proposing a repair. This hypothesis can be refuted cheaply without new games. A missing lemon is observed; self-destruction is a suspect, not an established cause.

## 1. Complete-funding run: first read, decisive limits

Source: W:claude-runs/20260907T065010Z-749733-1/PRIMARY-REVIEW.md. Its reported independently checked sample is 16 unique paired rows. Parent outcomes 7/6/3 give 10 match points; candidate 8/5/3 give 10.5, where a draw is half a point. The parent has no command issue; the candidate adds one move_blocked. No third worker was paid for or spawned. No 192-pair panel or complete export certificate followed.

On the traced branch the proposed bill is [6,3,3,0,3,0], while stock advances from [0,0,8,4,1,1] at turn 60 to [6,0,8,4,3,3] at turn 76. Plum and iron acquisition occurred. Lemons did not materialize, and the plan cancelled. Eight banked apples already exceed the three-apple requirement, so demanding simultaneous ripe plum/lemon/apple trees is not the correct witness.

The primary review identifies parent-controlled chopping while another worker funds the bill: worker 3 chops (13,5) on turns 66–68 and (11,0) on 74–75. It does not establish those trees' species or whether our worker or the opponent removed the required source. Its code inspection says only the current turn's target is reserved and unoverridden workers retain parent commands. **That is enough to require a trace audit, not enough to publish a causal diagnosis.**

The successor corrects the earlier macro's own-side rollout to use the actual parent policy, but retains one opponent continuation. It therefore implements parts of an acquisition plan, not a proved two-player renewable funding lifecycle. Its +0.5 match point cannot override the new movement fault or the missing completed purchase.

## 2. Nine requested properties and evidence standard

I = IMPLEMENTED in the named scope; A = ABSENT or contradicted in that scope; U = UNKNOWN from the inspected source/report. I never means independently executed in this session. C = direct code inspection; R = primary result/review describes the implementation or trace; H = historical closure record only. Partial components are stated in the notes rather than silently upgraded to the complete invariant.

Columns are the original PLAN section 5 properties:

(a) renewal seed survives DROP/TRAIN; (b) own crop replacement after harvest/felling; (c) fruit and wood can run together; (d) eligibility of health-zero fallen resources; (e) cargo-limited wood collection; (f) real MINE/PICK/DROP acquisition rather than a prefunded TRAIN fixture; (g) opponent harvest/chop interference is represented; (h) unattainable bills do not starve useful work indefinitely; (i) native transitional/second-flag and chop-target semantics.

**Correction to (d): it is not established as a reachable-state requirement.** M:sim/engine.py, apply_chop, distributes wood to choppers when health reaches zero and removes that plant immediately. M:docs/mechanics.md describes the death-time award. The exact official/adapter domain of an enduring health-zero collectible tree needs a witness before an exclusion is called a bug. U below means this premise or its applicability is unverified; it does not demand adding a fictitious salvage action. The separate harvest-zero worker exclusion in the ledger dispatch really was a different defect.

| Controller / assessed scope | a | b | c | d | e | f | g | h | i | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| N next_bot, current committed economy | U | I | I | U | I | I | I | I | A | C1/R1 |
| N V543 / V564 dense-economy antecedents | U | I | I | U | U | I | I | A | A | R1/R2 |
| W dispatch ledger 045048 | U | A | I | U | I | U | U | U | A | R3 |
| W forestry dispatch 050904 | U | I | I | U | I | U | U | U | A | R4 |
| W fruit dispatch 053105 | U | I | I | U | I | U | U | U | A | R5 |
| W timed dispatch 060006 | U | I | I | U | I | U | U | U | A | R6 |
| W initial policy-anchored macro 062139 | U | U | I | U | U | A | U | U | A | R7 |
| W complete funding 065010 | U | U | I | U | U | I | U | I | A | R8 |
| W orchard 024202 / seed-payback 034410 | U | U | U | U | U | A | U | U | A | R9 |
| N home-growth, new kernel authority only | A | A | A | U | I | A | I | A | A | R10 |
| M A2-1 from-scratch economy scheduler | U | I | I | U | U | I | I | U | A | H1 |
| M port v2 | U | I | A | U | I | I | I | U | A | H2 |
| M port v3.1 | U | I | A | U | I | I | I | U | A | H2 |
| M b100 / banana R2, multiple invalid builds | A | I | I | U | U | U | U | U | A | H1 |
| M champion-prefix macros, rows 3-8/3-9 | U | I | I | U | I | A | I | U | A | H3 |

The table does not claim that all nine properties must be present in a two-worker controller: a deliberate no-third-worker experiment should not receive a strategy failure merely because (f) is absent. Home-growth's As refer to what its one-CHOP override adds, not to features inherited from V439. Native semantics (i) are absent from the implemented approximation, not disproved in the real strong bot.

## 3. Why the cells have those labels

**C1: N:next_bot/economy.rs**, whole-file Git blob 5c1eb47ee3dd12131b77024b689d890ce72ed88e. Inspect planned_spec, source_capacity, production_goal, choose_goal, emit_goal and decide. Seed/Plant/Harvest/Chop/Drop/Mine are real jobs; ordinary fruit and wood coexist; wood value is clipped to free cargo; acquisition uses bank and carried stock, source reachability and a bill-abandonment estimate. The same-turn working_stock ledger subtracts proposed train costs and seed picks. Those are implemented components.

But source_capacity adds three potential fruits for each remembered tree without a realized delivery timetable. Plant ownership is inserted when a command is emitted, before final movement resolution/referee acceptance, and coordinate-based reconciliation is not a proof of generation-specific ownership. Goal validity and nominal payback are heuristics. Thus (a), the whole cross-turn conservation invariant, is U despite the real reservation component; (h) is I only for the explicit cancellation mechanism, not proof of freedom from all starvation. Successful cancellation still needs a useful legal continuation. No native T/second-flag mechanism is present.

**R1: N:NEXT-BOT-RESULTS-2026-09-05.md and FIELD-CALIBRATION-RESULTS-2026-09-05.md.** The extracted V564 control matched its prior 900-turn streams. Safe productive continuations repair a concrete zero-wood path but each win 1/3 fresh real-agent blocks versus the older reference's 2/3. Before the repair, V543/V564 can harvest through an unattainable lemon bill without a single CHOP against putibuzu. This directly supports A for (h) in the antecedents and forbids treating isolated decision fixtures as complete economic-cycle proof.

**R2: N:ADAPTIVE-R1FA-RESULTS-2026-09-04.md; V564-V565-HIGH-CAPACITY-THIRD-RESULTS-2026-09-04.md; CRITICAL-REVIEW-2026-09-05.md.** Actual scaling/planting occurs, not just a trained-worker fixture. Four-worker output and higher own score do not establish more match points. The old same-turn TRAIN prohibition is itself superseded by the later train-egress correction. V543's 384-pair outcomes 341/2/41 versus 340/4/40 are equal in match points; its later rank 155 is not evidence that its local opponents model the field.

**R3–R8: W:claude-runs/<run>/PRIMARY-REVIEW.md**, run IDs respectively 20260907T045048Z-386364-1, 20260907T050904Z-441221-1, 20260907T053105Z-507322-1, 20260907T060006Z-594612-1, 20260907T062139Z-661886-1, 20260907T065010Z-749733-1. The ledger build planted zero ring crops versus parent 1,197 because one-capacity planting was priced at zero and harvest-zero planters were excluded. Its compact also exceeded 100,000 UTF-16 units. The forestry repair implements seed-to-wood work, but its advertised known-map ablation was synthetic. The fruit build predicts an impossible early delivery; the timed build corrects a real fixture's two-fruit delivery from a nine-turn promise to twelve turns. Primary 192-row match-point totals are parent 170 versus ledger 139, forestry 146.5, fruit 142.5 and timed 137. These are different mechanisms/defects, not four clean independent failures of every orchard representation.

The initial macro has no acquisition plan and is command-identical to the parent on both reported panels; its own-side rollout uses model_commands instead of the actual parent. Complete funding corrects that latter boundary and acquires actual resources, but never completes the purchase and adds a move conflict. That is why its (f) is I for acquisition while the complete lifecycle remains unproved.

**R9: M snapshot WORKSTATE.md and W's corresponding orchard reviews.** The initial orchard fixture prefunds the bill before harvest; the seed-payback successor is reported with one failing test and no complete panel. The source/trace inspection of these two runs is less complete than R3–R8; U is intentional. Their summaries do not establish real funding.

**R10: N:HOME-GROWTH-RESULTS-2026-09-05.md and home_growth.rs.** The report describes a bounded single-cell kernel: at most one selected CHOP is replaced by a same-cell MOVE, with arrival and bankability guards. It does not own future seed stock, global traffic, worker funding or complete crop replacement. The reported full familiar panel is 173/5/14 for both arms, margin +2.3385, zero changed outcomes. A single-cell timing improvement is not a standalone renewal controller.

**H1: M:docs/CONSTRAINTS.md, workforce/scaling and substrate sections.** A2-1 actually acquired and banked bill fruit but missed its locked completion gate, 582/2,048 = 28.42% versus 40%. The banana R2 succession includes an explicit seed-surplus violation, an incorrect growth-aware conversion boundary, a scripted witness that did not drive the real candidate, and a 225-turn carrying loop. Grouping the whole sequence as a valid negative value test would be false. I marks observed components; unproved or contradicted invariants stay U/A.

**H2: M:chatgpt_2/port-postmortem/RESULTS.md; codex_1/norxondor-port/DESIGN-2026-09-02.md; coordination/GRAVEYARD.md.** The port contains real planting, harvesting, funding, chopping and banking through inherited primitives. It does not contain native thinning/target semantics and makes fruit/wood phases exclusive. A seven-living-tree cap plus deficient slot turnover is not a seven-lifetime-tree prohibition: its measured 13.01 cumulative plants rule out that literal claim. The attempted early switch changes a scalar, not the missing mixed-work loop.

**H3: M:chatgpt_1/champion-prefix-orchard/ and claude_1/orchard-repro/ as referenced by coordination/HANDOVER-2026-09-07-port-reopened.md.** These are deliberately no-third-worker planting/felling interventions after the parent opening. The independently expanded pool of 48 planting policies has no positive mean on the tested development set; the best reported mean is -0.46 with interval [-4.51,+3.60]. This closes that pool and prefix, not all opening economies. The parent's own long no-command streaks forbid a universal absolute stall threshold.

## 4. The experiment that remains identifiable

Freeze the exact complete-funding candidate, parent and reported changed game. Reconstruct the prefix before turn 60; enumerate each required currency, banked/carried stock, living source, earliest collect-and-bank event, planned reservations and actual effective commands. Through cancellation, annotate every tree creation/removal with species, generation, responsible actor and whether the event had been included in admission.

The first decision is a read-only fork:

- If our retained parent continuation destroys an indispensable source the admission model counted as available, retain one narrowly scoped supply-protection hypothesis, with an independently valid control and a measured opportunity cost.
- If the opponent destroys it or the required delivery was never reachable, close the self-destruction hypothesis. The next question is forecast/admission validity or opponent-risk pricing, not an automatic protection patch.
- If the trace cannot be reconstructed from the retained artifacts, report the missing file and hash. Missing data is not a successful cycle and not a new strategy result.

No branch above authorizes a bot. A later build needs a new charter naming the exact repaired transition and a prospective terminal match-point comparison. Do not force a third worker, mature tree count or early bank score as the success condition.

## 5. What was and was not executed

This is an executed source/document audit, not execution of the audited bots. The matrix covers every controller family named by E2; confidence differs explicitly by cell. W:COPY-RULE.txt says TSV/logs and most readable run sources were pruned, so not every source/trace witness is present. No value result or production certificate was independently regenerated here. Existing result claims remain attributed to their authors/reviewers; the coordinator can replay them where retained full data exist. The current seal was not opened or privately verified. None of those limits justifies a duplicate implementation.
