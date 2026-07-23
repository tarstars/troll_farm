# D163a resident-native resource-control component audit — frozen protocol

Date: 2026-07-23  
Status: frozen before implementation or outcome generation

## Question

D162's one-lane reserve option fails as a third-worker mechanism, but its
crop-safe resident-plus-option envelope has heterogeneous positive value that
almost never comes from training. D163 asks which, if any, resource-control
component has resident-relative causal value independent of workforce scale:

1. directed fruit harvesting and banking;
2. directed IRON mining and banking; or
3. suppression of resident consumption while a fixed reserve is missing.

This is a factorial mechanism audit, not a candidate search. It must not issue
a controller-generated TRAIN, use D162 winners as labels, train a selector,
contact YT or the platform, open reserved maps, create a submission, or alter
the resident.

## Frozen panel

Use the next eight already-consumed D148/D161 maps,
`9,844,144--9,844,151`, both seats, and all eight frozen opponent families:
128 tasks. This panel is disjoint from D162's `9,844,136--9,844,143`.
Maps `9,844,152--9,844,199` remain available for later work. Reserved maps
`9,844,200--9,844,215` remain untouched.

Run the complete matrix once with one worker and once with 20 workers. Require
byte-identical sorted output. The resident control must reproduce the D161
resident on every shared score, workforce, crop, mechanics, action-hash, and
state-hash field.

Bulk matrices go under the verified external-backed path
`artifacts/experiments/d163a-resource-control-components`. Compact protocol,
lock, analyzer, result JSON, and human report remain in the repository.

## Frozen controller

Every policy calls the unchanged exact resident on every turn, including
intervention turns, so KEEP remains warm. The controller activates only when
exactly two own workers exist at its fixed start. It uses the fixed shadow
reserve vector:

```text
[PLUM=3, LEMON=3, APPLE=2, BANANA=0, IRON=3, WOOD=0]
```

If a map has no IRON nodes, its IRON target is zero, matching referee
affordability semantics. The vector is inherited from D162's frozen minimal
bill solely to define missing resources; D163 never emits TRAIN and makes no
workforce-improvement claim.

The three independently toggled components are:

- **F — fruit routing/banking:** at most one suitable worker is redirected
  to bank carried missing target fruit or harvest the largest missing target
  among PLUM, LEMON, and APPLE, using deterministic distance/id tie-breaking.
- **I — IRON routing/banking:** at most one suitable worker is redirected to
  bank carried missing IRON or mine it, using the same deterministic routing.
- **P — consumption protection:** resident PICK/PLANT commands for a target
  resource are suppressed only while its deposited bank is below the fixed
  target.

F and I share one acquisition lane when both are enabled; the largest liquid
deficit wins, then fixed item order. P does not create an acquisition command.
All nonselected legal resident commands remain unchanged. The controller never
synthesizes or suppresses TRAIN. At the deadline it immediately returns to the
already-warmed resident and never restarts.

## Frozen catalog

For each activation turn `72`, `104`, and `136`, evaluate all seven nonempty
subsets of `{F, I, P}` with horizon `32`, plus one shared exact-resident
control:

```text
F, I, FI, P, FP, IP, FIP
```

There are 22 policies and 2,816 rows per complete run. The resident is the
zero-component cell for every activation turn when constructing factorial
contrasts.

## Integrity and mechanism gates

Interpret no value result unless all conditions pass:

1. both runs contain exactly 2,816 unique rows and are byte-identical;
2. the exact resident reproduces D161 on all 128 tasks and all shared fields;
3. every row terminates with exact reward identity and zero provenance,
   ambiguous-birth, controller-command-legality, horizon, or restart failures;
4. every arm matches the resident action/state prefix at its activation turn,
   activates on at least 90% of tasks, runs no more than 32 turns, and never
   restarts;
5. the controller synthesizes and suppresses zero TRAIN commands;
6. every arm/task matches resident successful-train, terminal-worker, and
   maximum-worker counts, establishing a workforce-independent comparison;
7. component purity is exact: F-disabled rows have zero fruit-caused
   overrides, I-disabled rows have zero IRON-caused overrides, and P-disabled
   rows have zero protected commands; and
8. each enabled component is exercised in at least 5% of its arm rows on the
   pooled panel.

A failed integrity item is repaired without interpreting value. A clean
workforce-independence or treatment-exercise failure closes the corresponding
causal interpretation.

## Factorial causal analysis

For each component and each task/start, form the four paired contrasts across
the other two flags. This yields 1,536 paired observations per component.
Report margin, own-score, opponent-score, crop, catastrophe, negative-margin
mass, workforce, family, seat, start, and map-cluster effects. Also report all
two-way and three-way difference-in-differences and every fixed arm versus
resident. No per-task outcome oracle is a pass criterion.

A component passes its causal gate only if:

1. mean paired margin effect is at least `+2`;
2. the map-clustered normal 95% lower bound is above zero;
3. at least six family means are positive and the worst is at least `-4`;
4. both seat means are positive and at least two of three start means are
   positive;
5. mean own-score effect is nonnegative or mean opponent-score effect is
   nonpositive;
6. crop-creation rate falls by no more than two percentage points;
7. catastrophe count and negative-margin mass do not increase;
8. workforce counts remain exactly paired; and
9. its treatment-exercise rate is at least 5%.

## Resident-relative continuation gate

Opening a new held consumed-panel validation requires both a passing causal
component and at least one fixed arm, without outcome-dependent selection
inside a task, that satisfies all of:

1. mean resident-relative margin gain at least `+4`;
2. map-clustered normal 95% lower bound above zero;
3. strict improvements at least equal strict regressions;
4. at least six positive family means and both seat means nonnegative;
5. crop creation within two percentage points of resident;
6. catastrophe count and negative-margin mass not increased; and
7. exact workforce parity.

If a causal component passes but no fixed arm passes, retain only the
mechanism and preregister a state-gated follow-up on another consumed panel.
If no component passes, close this fixed shadow-reserve grammar. Any passing
fixed arm opens only a separately frozen validation on unused consumed maps;
it does not authorize Arena or submission.

## Infrastructure

Run locally because the complete paired matrix is expected to finish in
minutes and requires a one-worker/20-worker determinism check. The external
storage preflight must pass before writing matrices. D163 makes zero YT and
platform requests. The canonical YT root remains exactly
`//home/delivery_ml/research/tarstars/troll_farm`.
