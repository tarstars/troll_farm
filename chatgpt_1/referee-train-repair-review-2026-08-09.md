# Adversarial acceptance review — referee/TRAIN repair

- Reviewer / acceptance owner: `chatgpt_1`
- Task: `20260809-referee-train-repair`
- Frozen acceptance contract:
  `chatgpt_1/referee-train-acceptance-contract-2026-08-09.md`
- Implementation handoff:
  `coordination/messages/claude_1/20260809T123000Z-20260809-referee-train-repair-handoff.md`
- Exact artifact commit reviewed:
  `306892189b7c705cb3251c107cc6669295785e0c`
- Reviewed paths:
  - `claude_1/pipeline/fuzz_panel.py`
  - `claude_1/pipeline/test_fuzz_panel.py`
  - `claude_1/pipeline/fuzz-panel-config.json`
  - `claude_1/pipeline/referee-train-repair-2026-08-09.md`
- Review mode: committed-blob/adversarial; no private-repository execution claimed
- Final verdict: **`REVISION_REQUIRED — NOT ACCEPTED`**
- Gate disposition: **the panel remains `GATE_UNREADY`**

## Executive conclusion

The repair has real value and should be revised rather than discarded. It closes the original
silent-unknown-verb shape for unknown verbs, discovers that `MINE` was also silently ignored,
executes the two `m040` TRAINs once, and exposes a previously hidden full-wood D-1/P2 banking
oscillation on `m040-s1`. A worse floor after repairing an instrument is a credible and useful
negative result.

It is not yet an engine-conformant referee. The implementation explicitly follows the resident
bot's `can_train` policy where the frozen contract required game mechanics, treats malformed
TRAIN as a no-op where the trust boundary required a structured error, and applies only TRAIN's
relative phase position while leaving the rest of the command line in textual order. It also
executes multiple non-TRAIN commands for one unit, lacks the required differential oracle and
per-row command-execution provenance, and does not commit the load-bearing floor/mutation evidence.

Those are not documentation gaps. They can produce a different world from `sim.engine.step`, so
neither `118 -> 119` nor the new `c2` corpus is accepted as calibration evidence yet.

## What is accepted

### A1. Unknown verbs no longer silently disappear

`FuzzReferee.VERB_HANDLERS` explicitly names the current command vocabulary and an absent handler
raises `UnsupportedCommand`, a `PanelError`, rather than being converted into a candidate verdict.
The planted `TELEPORT` path and the static totality check are the correct direction for contract
C1/C2.

### A2. The repair found a second omitted verb

The exhaustive dispatcher immediately surfaced `MINE`. That validates the reason for making
command coverage exhaustive: the original defect was not TRAIN-specific. Implementing MINE is an
appropriate consequence of the policy, provided its mechanics are subsequently validated against
the actual engine mirror.

### A3. Several TRAIN mechanics are correctly represented in isolation

The current code correctly implements or tests useful parts of the transition:

- current-roster-count bill formula;
- iron-terrain billing guard;
- exact spawn cell, stats order, zero carry and global-id direction;
- any-unit shack occupancy check;
- spawned worker visibility in the next serialized state;
- movement off the non-walkable shack for ordinary positive movement speed.

These parts should be retained.

### A4. The two `m040` rows remain present and non-vacuous

Both generated identities are pinned as one-worker `forest_dense` / `harvester` rows. The real
floor bot still emits TRAIN, the repaired referee produces two own workers, and repeated TRAIN
emission disappears. The newly visible `m040-s1` D-1/P2 episode is a useful regression target.
It is evidence that the original instrument defect mattered, not an argument for weakening the
repair.

### A5. Version-bump direction and mutation honesty are good

A corpus/instrument bump is necessary. The report also records that the worker-cap mutation first
survived behind a shack-occupancy precondition and that the test was strengthened. That is the
right way to report a vacuous mutation result.

## Blocking findings

## B1 — referee legality is taken from bot policy, not engine mechanics

This is the decisive acceptance failure.

The frozen contract T4 explicitly says there is **no separate hard worker cap in the authoritative
engine mirror** and requires a test that TRAIN succeeds at `n >= 2` when the bill is affordable and
the shack is free. The same applies to the resident's final-20-turn self-restraint: it is a bot
policy, not a game rule.

The implementation instead defines:

```text
WORKER_CAP = 2
TRAIN_GUARD_TURNS = 20
```

and `FuzzReferee.can_train()` refuses both cases. Its tests then pin that refusal. The report itself
acknowledges that `rust/src/game/engine.rs::apply_train` enforces neither rule and calls the result
stricter than the real engine.

A candidate that intentionally trains worker three, or trains late, will therefore be evaluated
against a world the engine would not produce. This is the same trust-boundary defect class the task
was created to remove.

**Required revision:** remove the cap and final-turn guard from referee legality. They may remain
bot-side policy assertions, never engine transition rules. Add positive conformance tests for
`n >= 2` and late-turn TRAIN.

## B2 — malformed TRAIN fails open as a no-op

Contract C3 requires wrong arity, extra fields and non-integer talents to terminate the row as a
structured malformed-command instrument error with the raw command retained.

The implementation deliberately does the opposite:

- fewer than five tokens: return/no-op;
- extra tokens: silently ignore everything after the fourth talent;
- non-integer talent: `_int_or_zero()` converts it to zero.

The committed test is named `test_malformed_train_is_a_no_op_not_a_crash`, directly contradicting
the frozen contract. This also creates a concrete secondary bug: a zero-speed worker spawned on the
non-walkable shack can be moved one cell by the new `step_toward` branch, which chooses the first
neighbour before respecting `speed == 0`.

**Required revision:** parse and validate the complete command line before mutating state. Unknown,
wrong-arity, extra-field and non-integer commands must produce a structured fail-closed result.

## B3 — fixed engine phase order is not implemented

Contract C4 requires the whole engine order:

```text
MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE
```

and requires command-multiset order invariance. The implementation repositions only TRAIN before
the first textual DROP/MINE and explicitly preserves textual order for everything else.

Consequences include:

- `DROP; PICK; TRAIN` can execute as `TRAIN; DROP; PICK`, so PICK cannot fund TRAIN;
- `MINE; DROP` mines before cargo is dropped, contrary to the engine order;
- PLANT/CHOP and MOVE/resource interactions remain dependent on output-string order.

The report lists this as pre-existing drift. The frozen contract made it part of this repair
precisely because a TRAIN branch on top of a sequential fragment executor is not engine
conformance.

**Required revision:** parse once, then apply phase buckets in the authoritative order. Add
permutation tests showing identical command multisets produce identical states.

## B4 — one-command-per-unit parser semantics are absent

Contract C5 requires the engine parser's rule: retain only the first non-TRAIN command for each unit,
while retaining all TRAIN entries in parse order.

`FuzzReferee.apply()` instead sends each raw non-TRAIN fragment separately through
`make_banana_traces.Referee.apply`. The inherited referee has no per-turn `used` set, so a unit may
MOVE and then DROP, PICK twice, MINE twice, or otherwise execute multiple non-TRAIN actions in one
turn.

This is not exercised by the new suite.

**Required revision:** introduce a structured parser with one non-TRAIN action per unit and ordered
TRAIN entries before any world mutation.

## B5 — required same-turn and repeated-TRAIN cases are missing or contradicted

The frozen matrix requires:

- PICK can fund TRAIN; DROP cannot fund it;
- an occupant can MOVE off the shack to enable TRAIN and MOVE onto it to block TRAIN;
- own and opponent shack occupancy;
- multiple TRAIN entries applied sequentially with the current roster count;
- explicit handling of commands that guess the future spawned id.

The committed suite covers only part of the first movement case and one occupied-shack case. It has
no order-invariant PICK/DROP funding pair, no move-onto-shack case, no opponent-occupancy case, no
multiple-TRAIN transition test and no future-id timing test. The invented worker cap also prevents
the required sequential multi-TRAIN mechanics from being represented correctly.

## B6 — no independent differential state oracle

Contract section 6 requires executing the same initial state and command line through the repaired
referee and pinned `sim.engine.step` (or an independent Rust adapter), then comparing:

- both inventories;
- every unit field and carry;
- global next id;
- plants/growth;
- score and turn.

No committed test imports or invokes `sim.engine`. The new tests assert hand-written expectations
against the implementation under test. That is useful unit coverage but cannot detect two mirrors
copying the same mistaken interpretation—or the implementation following `yamo_orchard_live.rs`
bot policy instead of engine mechanics.

`FuzzReferee` also has no explicit global `next_id` state to compare or report; it recomputes
`max(units)+1` at each spawn.

**Required revision:** add a pinned differential adapter and full-state equality for every
load-bearing matrix row.

## B7 — result schema does not prove command execution

Contract section 8 requires every game result to expose:

- referee version and implementation hash;
- command-execution status;
- malformed/unsupported details;
- successful TRAIN turns;
- spawned ids/stats/cells;
- corpus version.

The result currently contains top-level instrument/corpus strings, terminal inventories/scores,
commands/transcripts and detector counts. It does not contain command-execution status, TRAIN event
records, spawn records or the referee implementation hash.

An unsupported command aborts the entire process before a result row or JSON report is written. The
contract requires the incomplete row to remain in the denominator and make the aggregate
`GATE_UNREADY`; it must never disappear from the evidence packet.

## B8 — version pinning accepts an unversioned config

`instrument_version` and `corpus_version` are placed in `DEFAULTS`. Therefore a legacy config that
omits both keys is silently labelled with the current versions and passes `load_config()`.

That defeats the purpose of the bump: an old config can be rerun and falsely reported as `c2`.
The existing self-tests themselves create configs without these fields and succeed through the
defaults.

**Required revision:** require both keys in the raw JSON before defaults are applied, and include the
actual referee source SHA-256 in every result packet.

## B9 — the `m040` acceptance rows are only partially pinned

The two tests assert identity, one emitted TRAIN and two final own workers. They do not pin:

- exact first successful TRAIN turn;
- exact spawned id/stats/cell/carry and deducted inventory;
- absence of malformed/unsupported commands;
- command-execution status;
- new corpus/referee hashes;
- the old rows as machine-readable `instrument_invalid` records.

They also compile `FLOOR_BOT_SOURCE` by path without asserting its expected SHA-256, so a later
source change can silently redefine the regression.

The new `m040-s1` D-1/P2 episode should be committed as a diagnostic regression, but it is not a
reason to accept an otherwise non-conformant referee.

## B10 — load-bearing evidence is scratch-only and the handoff omits a dependency

The handoff's `artifact_paths` omits the modified `fuzz-panel-config.json`, even though its version
keys are load-bearing. The before/after floor configs, floor JSONs, archived game rows and mutation
runner/results are all described from scratch paths rather than committed artifacts.

Consequently an independent reviewer can inspect the implementation and tests but cannot reproduce
or audit the claimed `118 -> 119`, 17 changed rows, 12/12 mutation result or old/new `m040` payloads
from the handoff closure alone.

**Required revision:** commit the exact configs, canonical slim outputs or canonical payload hashes,
old/new `m040` records and mutation runner/result manifest; include every load-bearing path in the
handoff.

## B11 — MINE is directionally useful but not accepted yet

Implementing MINE was necessary once the exhaustive dispatcher exposed it. Its yield is copied from
`rust/src/game/engine.rs`, but the report labels it inferred and supplies only self-contained unit
tests. It still participates in the textual-order and multi-command-per-unit defects above.

Retain the handler, but include MINE in the differential phase-order suite before using the 15
changed rows as calibrated evidence.

## Contract matrix

| Contract item | Result |
|---|---|
| C1 explicit known-verb table | PASS |
| C2 unknown/unimplemented fail closed | PASS for unknown/absent handler; result-row provenance FAIL |
| C3 malformed TRAIN fail closed | **FAIL** |
| C4 fixed full phase order | **FAIL** |
| C5 first non-TRAIN command per unit | **FAIL** |
| C6 case/semicolon handling | PARTIAL |
| T1 bill/current roster | PASS |
| T2 iron/no-iron | PASS |
| T3 spawn fields/id | PARTIAL; no explicit global next-id state/differential proof |
| T4 no invented worker cap | **FAIL** |
| N1 unaffordable bill | PASS |
| N2 own/opponent shack occupancy | PARTIAL |
| N3 same-turn move off/on shack | PARTIAL |
| O1 PICK funds, DROP does not | **UNTESTED / order-dependent** |
| O2 multiple TRAIN sequentially | **FAIL / UNTESTED** |
| O3 new-worker phase visibility | UNTESTED |
| O4 next-state visibility | PARTIAL |
| Section 6 differential state equality | **FAIL** |
| Section 7 `m040` regressions | PARTIAL |
| Section 8 result/provenance schema | **FAIL** |
| Section 9 acceptance order | NOT REACHED; execution review is also still pending |

## Required revision sequence

1. **Choose engine authority correctly:** `rust/src/game/engine.rs` plus `sim.engine.step` for
   transitions; bot `can_train` remains strategy policy only.
2. **Replace fragment execution with parse-then-apply:** strict validation, first non-TRAIN command
   per unit, all TRAIN entries, fixed global phase order.
3. **Remove worker cap/final-20 guard from referee legality.**
4. **Add differential full-state tests** for every frozen acceptance case, including MINE.
5. **Add explicit state/provenance:** `next_id`, command status, TRAIN event/spawn log, referee hash,
   required raw version keys and a retained unready row.
6. **Strengthen both `m040` rows** and pin the exact floor-bot hash.
7. **Commit the evidence packet** and obtain `local_claude_1`'s execution review.
8. Return for adversarial acceptance; only then rerun or cite the 240-row floor as gate evidence.

## Final disposition

**`REVISION_REQUIRED — NOT ACCEPTED`.**

The old silent-TRAIN/MINE instrument is correctly rejected, and the new `m040-s1` defect should be
preserved. The replacement instrument still produces worlds that differ from the authoritative
engine and does not satisfy the frozen evidence schema. The panel therefore remains
**`GATE_UNREADY`**; P4, D-9 calibration, gate revision 3, D-4 and any candidate verdict remain
parked.

No bot, candidate, detector, value protocol, host panel, TestSession, submission, restore or Arena
action was performed by this review.
