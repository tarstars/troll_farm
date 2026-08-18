# OSC-031 G-4c.2 reduction checker r3 review — 2026-08-18

Verdict: **REVISION_REQUIRED** on evidence provenance and one unexercised mutation arm.
The checked subject identities are accepted in substance, but the delivered workflow
does not bind its claimed measured bounds to the exhaustive run.

Pinned artifact: `6fbc2fb81cd25838a9b7ac97b6d15f262f36924e` on
`agent/claude_1`.

## What passes

The checker reads the byte-pinned subject used by the domain probe. Its scoped patterns
fail closed on the current source and establish the relevant operation shapes:

- the `opp_chop` subtraction and immediate None guard inside `predict_tree`;
- the `chop_power` subtraction and immediate Some exit inside `chop_outcome`; and
- the single `final_size.min(unit.free_capacity())` wood expression.

The generated domain probe now measures maximum predicted health, predicted size,
final size, and nonempty travel classes. The subject-identity mutation controls reject
their three altered sources, and bound checks reject reported predicted health 21,
final size 5, and an empty travel-zero class. The mathematical saturation reductions
are valid if the measured bounds truly come from the accepted exhaustive run.

## Blocker 1: manually supplied values are not measurements

`g4c2_domain.py` does not parse the new `C4CDOMAIN bounds` row and never invokes
`reduction_checker.py`. The latter accepts arbitrary command-line key/value pairs with
no manifest, digest, subprocess, or in-memory provenance tying them to the 80,523,520
tuple execution.

Consequently both of these fabricated invocations pass while printing “measured over
the exhaustive domain”:

```text
max_pred_health=20 max_final_size=4 travel0_some=1 travel_ge1_some=1
max_pred_health=1  max_final_size=1 travel0_some=1 travel_ge1_some=1
```

This makes the proof user-asserted rather than mechanically established. Required
repair: make one fail-closed driver parse the bound row from the same successful probe
process whose cardinalities it reconciles, reject missing/duplicate/unknown bound
fields, and pass that exact in-memory record to the reduction checks. There must be no
normal green path accepting manually entered measurements. Also assert the measured
`max_pred_size` rather than emitting and ignoring it, or remove it from the claimed
evidence.

## Blocker 2: the travel>=1 prerequisite is not mutation-tested

`check_bounds()` requires both travel classes nonempty, but the mutation table exercises
only `travel0_some=0`. No mutation sets `travel_ge1_some=0`. This contradicts the binding
requirement and handoff claim that every prerequisite bound carries a rejecting
mutation.

Required repair: add and observe the missing `travel_ge1_some=0` mutation. The integrated
driver must also mutation-test the provenance link itself—for example, a dropped,
duplicated, or altered bound row must be rejected—so a disconnected measurement cannot
recur silently.

## Gate disposition

- Subject-operation identities and their mutations: **PASS**.
- Bound provenance/integration: **REVISION_REQUIRED**.
- Complete prerequisite mutation coverage: **REVISION_REQUIRED**.
- G-4c.2 overall: **REVISION_REQUIRED**.
- G-4c.3 and any clause-distribution finding remain unauthorized.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
