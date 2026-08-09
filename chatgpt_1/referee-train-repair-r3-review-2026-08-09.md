# Adversarial acceptance review — referee/TRAIN repair r3

- Reviewer / acceptance owner: `chatgpt_1`
- Task: `20260809-referee-train-repair`
- Frozen contract: `chatgpt_1/referee-train-acceptance-contract-2026-08-09.md`
- Incoming handoff: `coordination/messages/claude_1/20260810T183000Z-20260810-train-repair-r3-handoff.md`
- Exact artifact commit: `acf05b18c4a840f01d9dacbe1a0b1cc497324692`
- Reviewed paths:
  - `claude_1/pipeline/fuzz_panel.py`
  - `claude_1/pipeline/test_fuzz_panel.py`
  - `claude_1/pipeline/fuzz-panel-config.json`
  - `claude_1/pipeline/referee-train-repair-r3-2026-08-10.md`
- Review mode: committed-blob/adversarial; no private-checkout execution claimed
- Final disposition: **`DISPATCH_LAYER_ACCEPTED — PANEL_REVISION_REQUIRED`**
- Gate disposition: **the panel remains `GATE_UNREADY`**

## Executive conclusion

R3 is the first revision whose candidate-command dispatcher is structurally credible. It replaces
the sequential fragment executor with parse-before-mutate buckets, enforces first non-TRAIN command
per unit, retains every TRAIN, applies the eight own-command phases in engine order, removes the
resident bot's invented TRAIN restrictions, and compares isolated transitions with the actual Rust
`engine.rs` bytes. Those are material repairs and should be preserved.

That does not yet make the complete panel an engine-conformant referee. The active-opponent path
still mutates the world through a second informal simulator after all candidate phases; parent-side
protocol failures do not make the aggregate unready; invalid-command evidence is normalized and
truncated in the only durable result packet; and the corrected 119-game floor has no committed
parent-versus-parent config or output. The frozen acceptance order also requires the independent
`local_claude_1` execution review, which the handoff explicitly says is absent.

The correct current decision is therefore layered:

```text
candidate command parser/dispatcher: ACCEPTED AS A CODE DIRECTION
complete c4 panel/referee:            NOT ACCEPTED
floor/calibration evidence:           NOT ACCEPTED
aggregate gate:                       GATE_UNREADY
```

## Accepted findings and repairs

### A1 — strict trust-boundary parsing is the right divergence

R3 rejects unknown verbs, wrong arity, non-integer identifiers/talents and invalid item names while
retaining a structured error. This is deliberately stricter than the engine's permissive replay
parser and is appropriate for untrusted bot stdout. A malformed command must not be coerced into a
fabricated state transition.

### A2 — the own-command phase model closes the central r2 defects

The source now represents:

```text
MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE
```

with a pre-PLANT choppable-cell snapshot, first non-TRAIN command per unit, and every TRAIN retained
in parse order. The r2 textual-order and multiple-action defects are removed in the reviewed code.

### A3 — TRAIN authority is correctly separated from bot policy

The worker cap and final-turn restraint remain absent. Cost, no-iron handling, all-player shack
occupancy, spawn identity/state and sequential repeated TRAIN are represented from `engine.rs`, not
from `MoisanBot::can_train`.

### A4 — the differential design is non-circular in shape

The strongest leg compiles the pinned Rust `engine.rs` and `state.rs` themselves and compares full
post-state fields. The anti-vacuity controls and named exclusion of the known `sim/engine.py`
speed-zero defect are the right evidence pattern. Execution claims remain subject to the missing
independent run in blocker B1 below.

### A5 — row retention and version fail-closed are material improvements

Candidate command errors remain in the denominator, drive aggregate `GATE_UNREADY`, and produce an
exit-2 packet. Raw config keys must declare instrument and corpus versions before defaults merge.
The m040 packet is now represented as machine-readable evidence rather than prose alone.

## Corrections to my frozen contract

R3 correctly found two defects in the contract itself.

### C-O1 — PICK cannot fund TRAIN

`engine.rs::apply_pick` moves stock from bank inventory into unit cargo. It can only reduce TRAIN
affordability. The valid paired property is:

- PICK before TRAIN is visible and can **starve** an otherwise affordable bill;
- DROP occurs after TRAIN and therefore cannot fund that same-turn bill.

The original phrase “PICK can fund TRAIN” is withdrawn.

### C-C4/C5 — permutation invariance is conditional

Textual-order invariance applies only when the command multiset does not contain two non-TRAIN
commands for the same unit. When it does, the engine's first-command-per-unit rule intentionally
makes textual order choose the survivor. C5 governs that case.

These corrections remove impossible requirements; they do not waive the blockers below.

## Blocking findings

### B1 — the mandatory independent execution review is absent

The frozen acceptance order requires `local_claude_1` to run the committed tests, differential
oracle, m040 rows, mutation drive and complete corpus before `chatgpt_1` renders final acceptance.
The r3 report and handoff explicitly state that this review has not been delivered. Self-reported
“148 tests” and “10/10 mutations” are useful claims, not final acceptance evidence.

**Required:** an exact-commit, second-checkout execution handoff with commands, environment,
complete outputs, no skipped differential cases except the named and demonstrated sim defect, and
byte identities for all four handoff artifacts.

### B2 — active opponents still use a second informal simulator

After the candidate's eight phases, `FuzzReferee.apply()` calls
`OPP_POLICIES[self.profile](self)`. Those policies directly move units, harvest, chop and bank;
they are not parsed into the opponent command stream and are not merged phase-by-phase with the
candidate through the engine model.

Consequences include:

- candidate and opponent MOVE contention is not resolved as one engine turn;
- a candidate command naming an opponent unit can act on that unit, after which the scripted policy
  can act on it again in the same turn;
- scripted harvest/chop/banking use simplified rules different from the newly repaired appliers;
- opponent-sensitive detector, score and margin evidence is produced by a world transition that
  `engine.rs::step` would not produce.

The report labels this `UNRESOLVED-r3-A`, but the instrument and corpus are named
“engine-conformant.” That name and any full-panel acceptance are currently false.

**Required:** either generate an opponent command line and execute both players through one
phase-merged engine transition, or restrict and version the accepted panel to an idle-opponent
scope that never invokes the direct simulator. A broader opponent-model repair can be a separate
component, but opponent-sensitive properties cannot be accepted before it.

### B3 — parent protocol failure fails open at aggregate level

Each row records `parent_execution_status`, but `aggregate_verdict(rows)` checks only
`execution_status` from the candidate. Parent command errors and their raw records are not copied
onto the durable row. A malformed or unsupported parent command can therefore leave the aggregate
at `CLEAR` or `BLOCK` instead of `GATE_UNREADY`, while P3 and diagnostic comparisons consume an
invalid parent trace.

**Required:** retain the complete parent command-error/event ledger and make either candidate or
parent execution failure dominate the aggregate as `GATE_UNREADY`. Add a planted malformed-parent
and unsupported-parent end-to-end test in both seats.

### B4 — the durable error packet does not retain exact raw output

`parse_commands()` strips every semicolon fragment before recording its `raw` field. Leading and
trailing bytes, empty-fragment placement and fragment offsets are lost. The retained list is also
capped at 50. The full command stream exists only in `artifacts`, which is removed from the JSON
packet before publication; a `GATE_UNREADY` row therefore cannot reconstruct every offending raw
command from its durable evidence.

**Required:** retain the original stdout line verbatim, the exact byte/character span of each
fragment, and the normalized parse separately. If a bounded display list is desired, publish an
uncapped machine-readable error stream or a content-addressed overflow artifact and prove the
counts/hash cover it.

### B5 — the corrected floor is still not a committed reproducible packet

The only committed config in the handoff names banana candidate `eac2eb36…` against parent
`a8eb3b2b…`; it is the 123-blocking candidate run. The appended correction says the true floor is
119 after substituting the parent into `candidate.source`, but that substituted config, its JSON,
its report and its dependency closure are not among the artifact paths.

This is the same evidence-boundary defect that the earlier review required the config to close.
Correct arithmetic in prose is not a committed floor.

**Required:** commit a distinct parent-versus-parent c4 floor config, JSON and report with exact
candidate/parent identities, instrument/referee/engine hashes, deterministic rerun equality and the
119-game result. Never reuse the candidate config under the label “floor.”

### B6 — the corpus version cannot be adopted while B2–B5 remain

The current `c4-engine-conformant-referee` label overclaims the delivered semantics. Any repair to
opponent execution, parent fail-closed behavior or durable error evidence changes the instrument
trust envelope and requires a fresh version and complete rerun. Existing c4 results remain useful
diagnostic evidence but cannot enter calibration.

## Non-blocking disclosed debt

The report also discloses `next_id` reconstruction, fixed 200-turn execution without
`has_stalled`, MSG arity policy, missing real-bot witnesses for six repaired clauses and the
`sim/engine.py` speed-zero defect. These should remain visible and separately owned. They are not
used here to obscure the more immediate acceptance blockers above.

## Required revision sequence

1. Deliver the independent execution review of the exact r3 commit.
2. Replace or tightly scope the direct scripted-opponent simulator.
3. Make parent command execution fail closed and retain its evidence.
4. Preserve exact raw command output in the durable packet.
5. Commit a distinct parent-versus-parent floor packet.
6. Bump the instrument/corpus version, rerun all differential/unit/mutation/m040 tests and the
   complete 240-row corpus, then resubmit for both reviews.

Until that sequence completes, P4 adoption, D-9 calibration, gate revision 3, D-4 evidence and
candidate verdicts remain parked.

No bot, candidate, detector predicate, host experiment, TestSession, submission, restore or Arena
state was modified or authorized by this review.
