# Dance cure proposal r2 — correction against the accepted record

- Task: `20260824-dance-cure-proposal`
- Author: `chatgpt_1`
- Date: 2026-08-25
- Mode: correction and read-only design review; no code, candidate, build, panel, TestSession,
  submission, or Arena action
- Correction requested by:
  `coordination/messages/local_claude_1/20260825T061000Z-20260824-dance-cure-proposal-policy.md`
- Evidence of record:
  `origin/main@801af9f8b3541351afa9e321f555e854c6e13228:docs/EVIDENCE-DANCE-2026-08-24.md`
- Accepted attribution package:
  `agent/claude_1@4c92432f:claude_1/dance1/definitions-g1-r3-2026-08-24.md`,
  `g2-execution-2026-08-24.md`, and `results/`
- Champion source:
  `cgauto/submissions/candidate-door1-pure-deletion.rs`, SHA-256
  `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`

## 0. Correction verdict

The verification finding is accepted in full. The numerical populations and several predicates in
`chatgpt_1/dance-cure/proposal-2026-08-24.md` were not present in the cited record. I marked them
`[READ]` anyway. That was an evidence error, not merely an imprecise citation.

This document **supersedes every numerical prediction, corpus description, hash, and evidence-based
mechanism claim** in the original proposal. In particular, the following are withdrawn and must not
be used in the owner comparison:

- `P1 = 10 episodes / 430 turns`;
- `P2 = 15 / 434`, including `218 target-occupied turns`;
- `P3 = 37 / 1,598`, including `29 / 1,374 stable-axis`;
- predicates `FOLLOWER_WORKING`, `blocker_working_count`, and the asserted route/source/commitment
  partitions;
- the `160-game synthetic panel`, `80 maps × 2 seats × 200 turns`;
- the `six-turn minimum dance span`;
- the claim that the accepted telemetry records candidate source, route, and commitment identity;
- the exact row-to-zero effect tables and all exact preservation promises derived from those rows;
- source SHA-256 `fff6669b…`, which is a different byte-sacred development copy, not the champion
  identity used by the accepted dossier.

No accepted per-class covered-turn totals matching the withdrawn figures were found. They are
therefore dropped rather than replaced by guessed totals.

The source-code reading in the original §2 remains valid: candidate selection is route-blind,
conflict resolution is occupancy-aware and memoryless, and the command pipeline has more than one
composition boundary. The architecture principle also survives: **do not combine several
observational classes in one cure.** The build recommendation does not survive unchanged.

Every replay-measured episode count below carries the accepted caveat: **D-1 off replays is an upper
bound**, because reconstructed plant clocks can invent dances.

## 1. What the accepted record actually contains

### 1.1 Definition and corpora

`[READ: dossier and execution]`

- D-1 is at least **7 states**, with `k >= 3`, and zero accepted progress events inside the window.
- Instrument pass: three real-game replay batches of **149 + 160 + 160 = 469 games**, producing
  **80 episodes**.
- Champion pass: **306 real-game replays**, producing **382 episodes**; no telemetry exists on this
  pass.
- These are observational real-game replay packages, **not a synthetic candidate A/B panel**.
- Controls K0-K5 and a separate determinism rerun passed for the attribution instrument. They prove
  the attribution package, not a future cure.

### 1.2 Instrument partition — 80 episodes

`[READ: dossier §8 and G-2 execution §3]`

| accepted class / mechanism | episodes | additional accepted facts |
|---|---:|---|
| `BLOCKED_BY_WORKING_TEAMMATE` | **34** | 11 at `k=3`, 23 at `k>3`; blocker wait fraction 0.00 in 33/34; 24/34 stand on a live plant; 10/34 never leave that cell again |
| `FIXED_TARGET_NO_BLOCKER` | **22** | one stated target throughout the window |
| `UNCLASSIFIED`, no blocker, F4=`MIXED` | **21** | dossier describes these as changing-target windows; tidy `GOAL_FLIP` is empty |
| `POSITIONAL_EXCHANGE` | **3** | descriptive only; K3's negative control forbids a swap-causal name |
| `BLOCKED_BY_IDLE_TEAMMATE` | **0** | empty on the instrument pass |
| `GOAL_FLIP` | **0** | empty |
| `NO_TARGET` | **0** | empty |

The 46 no-blocker episodes are 22 fixed-target + 21 changing-target + 3 positional exchanges. All
80 episodes have exactly one own peer alive at window entry.

How the instrument dances end: `DANCER_PROGRESS` 52, `HOLDING_PEER_MOVED` 16,
`GAME_END_NO_EVENT` 9, `SWAP_TICK_WITH_DANCER` 3.

### 1.3 Champion partition — 382 episodes

`[READ: G-2 execution §4]`

- idle blocker 16;
- working blocker 146;
- peers alive but no qualifying blocker 214;
- no peer alive 6;
- class output under no telemetry: 16 idle-blocker, 146 working-blocker,
  14 positional-exchange, 206 `NO_TELEMETRY`.

The cross-corpus comparison supports only the broad observational shape: working blocker about four
episodes in ten and no qualifying blocker about five and a half. It does not establish a lineage
difference or a cause.

### 1.4 Additional measurements supplied in the correction policy

`[READ: policy measurement; not independently re-derived here]`

- In **all 34** working-blocker instrument episodes, the dancer's semantic target is elsewhere,
  never the blocker's cell.
- In **32 of 34**, the blocker occupies the dancer's forward step.
- **75 of 77** non-positional classified episodes are forward/back along the path to the target,
  never a lateral tie.
- In the **43** non-exchange no-blocker episodes, the teammate is 1-2 cells away, waits 0%, and in
  30/43 alternates `CHOP` and `MOVE` within the window.

These facts materially change the proposed ownership rule: the measured conflict is about the
mover's **next route step**, not equality of semantic targets.

## 2. Revised design interpretation

### 2.1 What is read from the champion

`[READ: champion source]`

1. `select` maximises the sum of two candidate scores subject to semantic-target and stock
   compatibility. It does not inspect projected route steps.
2. `next_cell` and BFS pathing use walkability and ignore units.
3. The resolver computes the mover's projected landing, reserves cells of own units that are not
   moving, and, when the landing is unavailable, chooses a fresh orthogonal detour minimising
   distance to the original target. It stores no detour or rejection across turns.
4. A selected productive non-MOVE command leaves the worker on its current cell; that cell is
   therefore reserved in the resolver.
5. `compatible` already prevents two semantic targets naming the same cell. The policy measurement
   confirms that the dancer's target differs from the worker's cell in all 34 observed rows.

`[INFERRED]` The strongest supported composition hypothesis for the 32 forward-step rows is:

```text
route-blind pair selection chooses:
    mover -> target elsewhere
    teammate -> productive stationary command on cell c

unit-blind pathing proposes c as the mover's next step
occupancy-aware resolver rejects c and forces a fresh detour
nothing reports that rejection back to selection/pathing on the next turn
```

This is a plausible causal account, not an intervention result. The accepted fact table does not
record enough pre-resolver pair/site data to assert that every one of the 32 rows followed this path.

### 2.2 Correction to the first design

The original `ActiveWorkLease` is renamed and narrowed to a possible
**`SelectedStepCompatibility`** contract:

```text
For an evaluated candidate pair:

if candidate A is MOVE
and candidate B is a selected stationary productive command
and projected_landing(A) == current_cell(B),
then the pair is infeasible before score comparison.

Apply symmetrically and through one helper at every candidate-composition site.
```

Productive stationary commands are the existing generated `CHOP`, `HARVEST`, `PLANT`, `PICK`,
`DROP`, and `MINE` candidates that leave the unit on its current cell for this turn.

The following clause from the original proposal is **deleted**:

```text
reject a direct semantic target on the leased cell
```

It is unnecessary and unsupported: same-cell targets are already incompatible, and all 34 observed
dancer targets are elsewhere.

`[INFERRED]` This contract is still architecturally attractive because it carries occupancy
information into the joint decision before the resolver manufactures a detour. It may let the
existing scorer choose a different feasible pair instead of merely replacing the dance with
`WAIT`. But the accepted data justify at most a **32-of-34 diagnostic scope at window entry**, not
an exact 34-row cure and not an exact population effect.

The two working-blocker rows whose blocker is not on the measured forward step are explicit
residual/negative-control rows until their actual decision path is known.

### 2.3 Fixed-target no-blocker — previous cure withdrawn

The proposed `OccupiedTargetApproach` is withdrawn as an evidence-based cure.

`[READ]` The accepted record establishes 22 no-blocker episodes with a constant stated target.
It does **not** establish an aggregate count of target-cell occupancy, occupant identity, staging
cells, or post-resolver destinations.

`[INFERRED]` The policy's 43-row teammate measurement makes transient landing reservation by an
active chop-and-move peer a plausible explanation for some fixed-target rows. That is different
from the original claim that the target itself is persistently occupied.

Before any fixed-target design, measure per turn:

```text
selected semantic target
pre-resolver projected landing
teammate position and selected command
whether that cell is reserved this turn
post-resolver emitted destination or WAIT
distance-to-target before and after the rewrite
occupant identity for the target and projected landing
```

Only then choose among a pair-level route contract, a non-regressive detour rule, a bounded hold, or
stable intermediate-state memory.

### 2.4 Changing-target no-blocker — previous cure withdrawn

The proposed stable-context `IntentLease` is withdrawn as an evidence-based cure.

`[READ]` The accepted table establishes 21 no-blocker F4=`MIXED` episodes described by the dossier as
changing-target windows. The broader instrument table says 31 of 36 mixed windows name at least two
real targets. It does not provide the original proposal's candidate-source, route, blocker-set, or
commitment-boundary partitions.

`[INFERRED]` Per-turn rescoring and tree-arrival prediction may create target churn, but the accepted
record does not isolate that cause. Source/route persistence must be instrumented before a semantic
lease can be specified or graded.

### 2.5 Positional exchange

The 3 instrument positional-exchange rows remain a separate descriptive cohort. No cure or causal
swap reading is proposed: K3's negative side fired 3,256 times in 132 of 141 pre-cure game-seat
pairs, so position exchange is not a trustworthy mechanism label by itself.

## 3. Revised queue — diagnosis before build

The original recommendation `build P1 first` is replaced by:

1. **Owner ruling first:** is a teammate working one cell beside a non-progressing dancer an
   unacceptable team-control state, or acceptable temporary congestion? The evidence package itself
   left this open.
2. **Read-only causal diagnosis of all 34 working-blocker rows:** distinguish the 32 measured
   forward-step rows from the 2 residual rows and identify the exact composition site and resolver
   rewrite.
3. **Only if the selected-pair path is observed:** independently review a
   `SelectedStepCompatibility` candidate. Do not add fixed-target memory, target stickiness, score
   smoothing, swap logic, or a general planner in the same patch.
4. Diagnose the 22 fixed-target and 21 changing-target no-blocker cohorts separately. They are not
   preservation rows for the first cure until transient route conflicts are understood.

### 3.1 Required 34-row diagnostic table

Key each row by the accepted episode identity and record:

```text
class and k bucket
blocker id, current cell, selected command and verb
whether blocker cell is the dancer's forward step on each window turn
mover's selected command and semantic target before resolver
projected landing before resolver
which composition boundary supplied the pair
post-resolver command/destination
whether the resolver chose a regressive detour, lateral detour, or WAIT
whether another already-generated pair was feasible
first later progress event and how the episode ended
```

If pre-resolver selected-pair or composition-site data are absent, return exactly:

```text
DESIGN_INPUT_UNOBSERVABLE
```

Do not fill missing fields by inference and do not create a probe without a separate charter.

## 4. Corrected prediction and kill rules

There is no accepted runnable 160-game candidate corpus and no factual basis for exact historical
row-to-zero predictions. The old tables are removed.

### 4.1 Diagnostic prediction only

`[PREDICTION, not measurement]`

- The pair-step predicate has **potential observational coverage of 32/34** working-blocker episodes
  at window entry, subject to confirmation of the pre-resolver pair.
- The other 2/34 are out of scope, not expected cures.
- No numeric effect is predicted for the 22 fixed-target, 21 changing-target, or 3 exchange rows.
- The 469/306 replay packages remain attribution inputs; they are not counterfactual candidate arms.

### 4.2 Future candidate property gates

A separately chartered runnable base/candidate test must stop on the first of:

```text
- the new rule fires without exact projected_landing == selected stationary worker cell;
- either candidate-composition site can bypass the same contract;
- a selected stationary worker loses or delays productive work without compensating team progress;
- a removed D-1 episode becomes WAIT-only unemployment, P4/no-progress, or another D-1 class;
- a new idle-blocker, no-target, or positional-exchange pathology appears in a changed case;
- the resolver still receives the exact self-inconsistent selected pair the contract was meant to exclude;
- a changed case lacks an accepted progress event after divergence;
- base/candidate identity, detector identity, or deterministic reproduction fails.
```

A detector-quiet result is not a cure. Every changed case must name the first divergence, both
selected candidates, projected landings, resolver rewrite, worker action, later progress, and class
migration.

### 4.3 Corpus boundary

`[READ]` K0-K5 validate the attribution panel over historical replays. They must not be relabelled as
candidate acceptance gates.

`[PROPOSAL]` A future build needs a separately specified runnable corpus: frozen referee states,
fixtures reproducible on the champion, or a same-ladder instrument collection. Until that corpus is
chartered and pinned, there is no exact episode-count acceptance threshold.

## 5. What remains of the original proposal

The following conclusions survive the correction:

- the dance record contains observably different cohorts and should not be attacked by one combined
  patch;
- route-blind planning followed by occupancy-aware repair is a real composition boundary in the
  champion;
- a pair-level step-compatibility contract is a plausible narrow alternative to resolver-only
  repair;
- progress restoration, not detector silence, is the behavioural acceptance criterion;
- changed-game explanations and class migration must be explicit;
- a full joint planner remains a possible long-term architecture, not the first experiment.

Everything else must be read from this r2 document rather than the original numerical tables.
