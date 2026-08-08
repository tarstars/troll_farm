# I-30 specification — paired schedule/opponent-production exposure

Date: 2026-08-08  
Author: `chatgpt_1`  
Task: `20260808-phase1-work-allocation`, item 6  
Intended implementer: `claude_1`  
Execution reviewer: `local_claude_1`  
Status: **normative Phase-1 measurement specification; no candidate value threshold frozen here**

## 1. Problem and scope

The existing Banana invariant set and D-6 can detect a direct failure: we create fruit that the
opponent harvests. They do not detect the more general paired failure in which our policy changes
the competitive schedule and the opponent produces or banks more from **its own or natural
sources**. D89a demonstrates why this distinction matters: its aggregate opponent-score increase
of `+82.863281` is reproducible, while the historical theft-versus-opponent-production split is
not reproducible because the source-provenance rows were never committed.

I-30 closes the instrumentation blind spot without repeating that unsupported decomposition. It
requires every Banana-changing candidate to expose, under exact paired execution:

1. total opponent terminal-score change;
2. gross opponent deposits originating from our assets (direct theft/exploitation);
3. gross opponent deposits originating from opponent-created or natural assets (indirect schedule
   opportunity);
4. score-bearing resources the opponent spends on TRAIN;
5. an exact conservation identity linking those flows to terminal score.

I-30 is additive to D-6. D-6 remains the direct opponent-harvest safety detector. I-30 detects the
case where D-6 is zero but opponent production still expands.

This specification freezes **semantics, accounting, statuses, outputs and bite-tests**. It does
not choose a numerical value threshold. The owner or a separately frozen value protocol must do
that before any candidate verdict. An active candidate with a measured but unthresholded I-30 term
is `GATE_UNREADY`, not PASS.

## 2. Normative invariant

### I-30 — schedule/opponent-production evaluability and bound

For every deterministic candidate/parent pair in which the Banana layer changes behaviour:

1. the pair identity and all transitive inputs are hash-bound;
2. opponent score-bearing acquisition and spending are recorded in an exact event ledger;
3. the per-pair conservation residual is exactly zero;
4. provenance classified as `unknown` is zero for all score-bearing opponent deposits;
5. the paired schedule term is computed and reported raw;
6. a hash-pinned owner-frozen bound exists and is evaluated;
7. the instrument has passed the mandatory positive and negative bite-tests in §10.

A gate must not return ACCEPT when any clause above is missing. Missing evaluability is
`GATE_UNREADY`; an unexercised required path is `UNPROVEN`; exceeding a frozen bound is FAIL.

The invariant does **not** require the paired schedule term itself to be zero unless the later
frozen protocol chooses zero. This avoids smuggling a new value policy into measurement repair.

## 3. Exact paired execution contract

Each pair must share all of the following:

- map bytes and map SHA-256;
- seat;
- opponent source/binary SHA-256 and opponent configuration;
- engine/referee source SHA-256;
- initial inventories, units, plants and RNG seed/state;
- turn cap and termination rule;
- toolchain and harness SHA-256;
- every detector/analyzer/config SHA-256.

The only allowed difference is candidate versus parent bot bytes and the deterministic state
changes caused by those bytes. Every result embeds both source and compiled-binary hashes.

Per game, store candidate and parent command-stream hashes. For the mandatory parent-vs-parent
negative control, source, binary and command hashes must all be equal. Equality of terminal scores
or inventories is not a sufficient identity proof.

A pair mismatch is a transport/instrument error and yields `GATE_UNREADY`; it is never silently
dropped from the denominator.

## 4. Activation and populations

A pair is `banana_active` when at least one of these holds:

- the candidate emits a Banana command attributable to the changed layer that the parent does not;
- the candidate enters a Banana-specific controller state that the parent does not;
- a successful own Banana plant, harvest, chop, pick or bank event differs between candidate and
  parent;
- the candidate and parent command streams first diverge at a declared Banana integration seam.

The implementation must report:

- all paired games;
- `banana_active` games;
- inactive exact games;
- activation cause and first divergence turn.

Inactive exact games remain in the overall denominator with zero paired deltas. A candidate that
claims a Banana mechanism but activates in no exercise fixture is `UNPROVEN`, not PASS.

## 5. Event ledger

### 5.1 Score-bearing resource atoms

The ledger tracks every unit of PLUM, LEMON, APPLE, BANANA and WOOD that can enter the opponent's
bank. IRON is tracked for TRAIN accounting but has score weight zero. Score weights are frozen to
the engine rule:

```text
PLUM=1, LEMON=1, APPLE=1, BANANA=1, WOOD=4, IRON=0
```

Each carried score-bearing atom receives:

```text
resource_kind
source_event_id
source_asset_id
source_class       # ours | opponent | natural | unknown
source_creator     # player 0 | player 1 | natural | unknown
acquired_turn
acquired_verb      # PICK | HARVEST | CHOP
```

The referee or a deterministic shadow ledger follows atoms through carry and DROP. Mixed cargo
must not destroy provenance. If the engine does not define an order for consuming indistinguishable
atoms, the ledger may treat them as a multiset; only counts by source class are required.

### 5.2 Asset provenance

- A map-seeded tree or plant is `natural`.
- A planted asset's `source_creator` is the player that successfully issued PLANT, independent of
  the seed's earlier provenance. Record `seed_source_class` separately for diagnosis.
- Fruit harvested from an asset inherits that asset's creator class.
- Wood from CHOP inherits the chopped asset's creator class.
- A loose item inherits the tag of the event that created or dropped it.
- Any source that cannot be proved remains `unknown`; proximity, target selection or ownership
  guesswork must not relabel it.

This definition makes an opponent crop planted using a stolen seed an opponent-created asset. The
seed acquisition is direct exploitation; later fruit/wood is opponent production enabled by the
schedule. Both remain visible.

### 5.3 Bank and TRAIN events

Record every successful opponent DROP into the tent by resource kind and source class. Record the
exact score-bearing resource bill consumed by every opponent TRAIN. No provenance decomposition of
TRAIN spending is needed for the primary identity; total resource spending is sufficient.

Record initial and terminal opponent inventories and scores, plus terminal turn. Initial paired
states must be identical.

## 6. Per-pair quantities

For a run `r` (candidate or parent), define score-equivalent opponent deposits:

```text
DEP_OURS(r)     = deposits whose source_class is ours
DEP_OPP(r)      = deposits whose source_class is opponent
DEP_NATURAL(r)  = deposits whose source_class is natural
DEP_UNKNOWN(r)  = deposits whose source_class is unknown
TRAIN_SPEND(r)  = score weight of resources consumed by opponent TRAIN
```

All are gross score-equivalent amounts. Define paired deltas as candidate minus parent:

```text
D_DIRECT   = ΔDEP_OURS
D_SCHEDULE = ΔDEP_OPP + ΔDEP_NATURAL
D_UNKNOWN  = ΔDEP_UNKNOWN
D_TRAIN    = ΔTRAIN_SPEND
D_OPP      = opponent_terminal_score(candidate)
             - opponent_terminal_score(parent)
```

The primary indirect schedule/opponent-production term is:

```text
SCHEDULE_WINDfall = D_SCHEDULE - D_TRAIN
```

With identical initial inventories and complete provenance, the exact accounting identity is:

```text
D_OPP = D_DIRECT + SCHEDULE_WINDFALL
```

For diagnostic output before provenance is proven complete:

```text
D_OPP = D_DIRECT + D_SCHEDULE + D_UNKNOWN - D_TRAIN + RESIDUAL
```

I-30 requires `D_UNKNOWN == 0` and `RESIDUAL == 0` in every evaluated pair. Arithmetic uses
integers, so no floating tolerance is permitted. A nonzero residual or unknown source is an
instrument failure (`GATE_UNREADY`), not a candidate failure and not a report-only warning.

Also report, but do not substitute for the score flows:

- successful opponent PLANT/HARVEST/CHOP/PICK/DROP/TRAIN count deltas;
- first opponent productive-action turn delta;
- productive opponent turn-count delta;
- terminal-turn delta;
- opponent live-asset count and ripe-fruit exposure over time;
- direct opponent interactions with our assets.

These diagnose the causal schedule but do not determine the accounting identity.

## 7. Relationship to D-6 and existing invariants

D-6 and I-30 cover different classes:

| case | D-6 | I-30 |
|---|---:|---:|
| opponent directly harvests our crop | fires/records | `D_DIRECT > 0` |
| opponent plants and harvests more of its own crops because our schedule changed | may remain zero | `SCHEDULE_WINDFALL > 0` |
| opponent gains more from natural assets because we stopped contesting them | may remain zero | included in `D_SCHEDULE` |
| opponent score rises only because it trains less | may remain zero | visible through `-D_TRAIN` |
| accounting/provenance missing | cannot diagnose | `GATE_UNREADY` |

A candidate may pass D-6 and still fail a later frozen I-30 bound. Conversely, I-30 never converts
a raw D-6 episode into acceptance.

## 8. Status model

The implementation emits one of these I-30 statuses:

- `NOT_APPLICABLE` — candidate and parent are exact and no Banana mechanism is claimed; identity
  hashes prove it.
- `UNPROVEN` — a required semantic branch or positive fixture has never been exercised.
- `GATE_UNREADY` — pair identity, provenance, conservation, source/config hashes or the frozen
  numerical bound is missing/invalid.
- `PASS` — all accounting and bite-tests pass and the raw aggregate satisfies the owner-frozen
  bound.
- `FAIL` — accounting is valid and the owner-frozen bound is exceeded.

`MEASURED_UNTHRESHOLDED` may be emitted as a diagnostic sub-status, but the enclosing gate maps it
to `GATE_UNREADY`. It is never equivalent to PASS.

The output always preserves raw values, even when status is not PASS.

## 9. Aggregate report contract

Report separately for all pairs and `banana_active` pairs:

- number of maps, pairs, seats, opponent families and active games;
- mean `D_OPP`, `D_DIRECT`, `D_SCHEDULE`, `D_TRAIN`, `SCHEDULE_WINDFALL`;
- positive-windfall games and positive-windfall mass;
- p10/p50/p90 and worst per-pair values;
- per-opponent-family and per-seat means;
- per-map means and a pre-registered map-cluster 95% interval;
- games and event episodes as distinct units;
- unknown-source and conservation-residual counts;
- complete SHA manifest and exact bound/config identifier.

No post-hoc exclusion is allowed. Stalled/error pairs remain visible and make the result
`GATE_UNREADY` unless the frozen protocol predefines their handling.

The JSON embeds the per-pair quantities and enough event identifiers to reproduce each aggregate.
Large raw ledgers may be stored separately, but their SHA-256 and immutable path must be in the
result.

## 10. Mandatory bite-tests

The implementation is not adoptable until all fixtures execute through the real parser, referee
ledger and analyzer.

### Negative controls

1. **Exact parent-vs-parent:** all hashes and commands equal; every delta and residual is zero.
2. **Directly inert candidate:** command streams differ only in a non-state-changing diagnostic
   path; terminal and flow deltas are zero.
3. **No Banana activation:** status `NOT_APPLICABLE`, not a fabricated exercised PASS.

### Positive controls

4. **Direct theft only:** candidate creates one our-origin ripe crop that the opponent harvests and
   banks; `D_DIRECT` is positive, `SCHEDULE_WINDFALL` is zero, D-6 exercises.
5. **Indirect opponent production only:** candidate changes our schedule so the opponent
   successfully plants/harvests/banks one additional opponent-origin crop while never touching our
   assets; D-6 remains zero and `SCHEDULE_WINDFALL` is positive.
6. **Natural opportunity:** candidate stops contesting a natural asset and the opponent banks its
   output; the delta appears in `D_SCHEDULE`, not `D_DIRECT`.
7. **TRAIN-spend offset:** gross opponent deposits are equal but candidate causes one additional
   opponent TRAIN bill; `D_TRAIN` closes the terminal-score identity with the correct sign.
8. **Mixed cargo:** one DROP contains atoms from ours, opponent and natural sources; each class is
   counted exactly once.
9. **Longer-game schedule:** candidate extends the game and the opponent completes an extra own
   production cycle; terminal-turn delta and `SCHEDULE_WINDFALL` both expose it.
10. **D89-like blind-spot fixture:** all existing 29 behavioural invariants and D-6 are satisfied,
    but the opponent banks more from its own assets; I-30 must not return PASS under a bound that
    excludes the synthetic windfall.

### Fail-closed controls

11. candidate/parent source or command hash mismatch in a declared self-pair → `GATE_UNREADY`;
12. one untagged score-bearing atom → `GATE_UNREADY`;
13. nonzero conservation residual → `GATE_UNREADY`;
14. absent bound/config hash on an active candidate → `GATE_UNREADY`;
15. remove the indirect-production calculation deliberately → the blind-spot fixture must fail,
    proving the test bites the intended logic rather than a neighboring check.

Tests must assert exact integer values, not merely nonzero status.

## 11. Bound freeze — deliberately separate

This specification does not select among competing value policies. Historical artifacts contain
at least three incompatible choices:

- an absolute mean opponent-score ceiling (`<= +1` in D89a);
- a leak-ratio bound (D91c);
- the later owner direction to judge candidate value primarily by margin rather than absolute
  opponent gain.

Choosing one here would move the value goalpost during measurement repair. The implementation must
therefore accept a hash-pinned bound object, for example:

```json
{
  "schema_version": 1,
  "population": "all_pairs | banana_active",
  "metric": "mean_schedule_windfall | mean_d_opp | leak_ratio | compound",
  "operator": "<=",
  "threshold": 0,
  "family_constraints": [],
  "tail_constraints": [],
  "owner_decision_path": "coordination/messages/...",
  "owner_decision_blob": "40-hex"
}
```

The values above are illustrative schema fields, not a proposed threshold. Before candidate use,
the owner freezes the object before seeing candidate results. The analyzer reports every raw metric
regardless of the chosen one.

## 12. Implementation boundary and acceptance checklist

`claude_1` may implement the ledger, analyzer, fixtures and JSON schema under Phase 1. It must not
change a bot, candidate, parent, value protocol, host game corpus, TestSession, submission, restore
or Arena state.

The implementation handoff is reviewable only when it includes:

- source paths and full hashes;
- event schema and per-pair JSON examples;
- all fifteen bite-tests;
- exact parent-vs-parent result;
- one synthetic D89-like result showing D-6 zero and I-30 positive;
- explicit `MEASURED_UNTHRESHOLDED -> GATE_UNREADY` behavior;
- no numerical candidate threshold presented as owner-approved.

Adoption requires the assigned execution review by `local_claude_1`. No self-authored result may
be cited as an accepted gate verdict before that review.

## 13. Summary

I-30 does not claim the unreproducible historical split. It creates the telemetry that would have
made that split reproducible:

```text
opponent terminal delta
  = direct deposits from our assets
  + deposits from opponent/natural assets
  - opponent TRAIN spending
```

The exact paired `SCHEDULE_WINDFALL` term catches the blind spot where D-6 is silent and the
opponent's own production expands. Accounting correctness is raw-zero and immediately enforceable;
the numerical safety bound is owner-frozen separately. Until both measurement and bound are valid,
the gate is `GATE_UNREADY`, never silently green.
