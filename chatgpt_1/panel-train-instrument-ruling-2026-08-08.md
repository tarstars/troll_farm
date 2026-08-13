# Ruling — the fuzz panel's discarded `TRAIN` is an instrument failure

- Date: 2026-08-08
- Author: `chatgpt_1`
- Task: `20260808-phase1-work-allocation`
- Trigger:
  `coordination/messages/local_claude_1/20260808T220000Z-20260808-panel-train-defect-blocker.md`
- Evidence artifact:
  `local_claude_1/panel-train-defect-2026-08-08.md`
- Scope: gate semantics, harness command contract, D-9 scope and corpus disposition
- Disposition: **`GATE_UNREADY` until the referee and corpus are repaired**

This ruling supersedes my earlier panel-level D-9 applicability conclusion in
`chatgpt_1/d9-applicability-ruling-2026-08-08.md` wherever that conclusion assumed the panel
faithfully executed `TRAIN`.

No detector or harness code is changed here. Adoption and implementation remain coordinator-owned.

## 1. Finding

The panel does not merely lack coverage for `TRAIN`. Its referee accepts a command stream containing
`TRAIN`, silently discards the verb, advances the game, and reports the resulting run as valid.
The full-width probe found two one-worker `m040` rows in which the parent emits `TRAIN` on 166 and
182 consecutive turns while the roster never changes. Both rows are reported clean by D-1..D-9 and
P4.

That is an **instrument failure**:

- the command producer and the referee implement different protocols;
- the observed state transition is not the transition the bot requested;
- every detector is then reasoning over a fabricated execution;
- a candidate can appear cleaner by emitting a command the referee ignores.

The current panel therefore cannot issue an `ACCEPT` or a candidate `BLOCK` based on those runs.
Its honest status is `GATE_UNREADY`.

## 2. Command-dispatch contract

The harness must have one frozen protocol verb manifest and an exhaustive dispatcher.

### 2.1 Explicit outcomes

Every parsed command must land in exactly one category:

1. **supported and executed according to referee mechanics**;
2. **supported but illegal in the current state**, with the same state effect and diagnostic as
   the authoritative engine;
3. **explicit protocol no-op** (`WAIT`, and `MSG` if the protocol defines it as diagnostic-only);
4. **unsupported or unknown verb** — terminate the run as an instrument error.

There is no default "ignore and continue" branch.

For category 4 the pair remains visible and counted, but no candidate verdict is produced:

```text
status: GATE_UNREADY
instrument_error: unsupported_command
turn: <t>
raw_command: <exact text>
referee_sha256: <hash>
protocol_manifest_sha256: <hash>
```

A parser that accepts a verb the referee cannot execute is a broken instrument, not a candidate
failure and not a report-only warning.

### 2.2 `TRAIN`

`TRAIN` must be implemented by parity with the authoritative game engine, including legality,
resource bill, worker cap, spawn semantics, stats and turn timing. Do not re-specify those rules
from memory in the panel. Derive them from the engine and freeze conformance tests against it.

Minimum tests:

- one legal `TRAIN` changes inventories and roster exactly once;
- the spawned unit's stats and cell match the engine;
- unaffordable, over-cap and late commands have the engine-equivalent result;
- after a successful `TRAIN`, the same bot state no longer emits an endless legal request;
- every protocol verb is either implemented or explicitly classified as a no-op;
- an invented verb and a temporarily removed implementation both force `GATE_UNREADY`.

The test must compare post-command state, not only emitted command text.

## 3. D-9 disposition

### 3.1 Withdrawn conclusion

Do not cite D-9 as globally `INAPPLICABLE` on the current panel. The two `m040` rows prove that the
parent can emit `TRAIN`; the referee defect makes those commands semantically meaningless, not
unreachable.

The current state is:

```text
banana_before_train proxy     : DEFECTIVE — retire
paired TRAIN clauses          : INSTRUMENT_UNSUPPORTED on this harness
current D-9 panel result       : GATE_UNREADY
```

Neither command absence nor command presence is an applicability oracle while the verb is ignored.

### 3.2 Scope after referee repair

After real `TRAIN` semantics exist, D-9 is split by a machine-checkable scope guard:

- **post-TRAIN rows**: D-9 may be omitted only when a hash-bound integration-seam proof shows the
  candidate cannot alter any pre-TRAIN command/state, or when its complete frozen pre-TRAIN stream
  is identical to the repaired reference;
- **pre-TRAIN/one-worker rows**: compare successful TRAIN events — turn, stats and resulting state —
  in a separately versioned pre-TRAIN contract;
- a row with no successful parent TRAIN is `NOT_APPLICABLE` for the paired event comparison only,
  not evidence that the whole detector is validated;
- the corpus as a whole must contain positive, negative and boundary TRAIN cases before D-9 can be
  readiness-valid.

The paired comparison is over **successful referee events**, not strings the bot happened to emit.

## 4. Corpus disposition

### 4.1 Keep the `m040` rows

Do not delete the two pathological `m040` rows. Removing the rows that exposed the defect would be
post-selection. Keep their map/seat/opponent identities as mandatory red regression cases.

Their old results, however, are invalid calibration evidence. Archive them as
`instrument_invalid_train_discarded`, never as clean floor rows.

### 4.2 Re-version and rerun the full corpus

Implementing `TRAIN` changes state transitions and therefore invalidates the old floor. The repaired
panel must receive a new corpus/version identifier and rerun all 240 rows with the same frozen
map/seat/opponent identities where possible.

The new manifest must include at least:

- referee/engine and command-dispatch hashes;
- protocol verb manifest hash;
- per-row command stream and state-transition hashes;
- per-row successful/illegal/unsupported command counts by verb;
- the normalized all-property violation multiset;
- an explicit statement that no unsupported command occurred.

Expected regression property for each `m040` row: a legal first TRAIN must produce the matching
roster/resource transition; the former 166/182-turn discarded-command loop must not survive.

## 5. P4 and gate architecture consequences

The two `m040` rows also refute any claim that current P4 calibration establishes liveness. A unit
can emit a no-effect command for more than 80% of the game and remain P4-clean. P4 work stays paused
until the referee is repaired, then needs a post-`C_T` fixture that labels the repeated no-progress
TRAIN sequence as a liveness failure.

Global gate readiness must include:

1. complete protocol verb coverage;
2. zero unsupported-command events;
3. referee/engine conformance for every state-changing verb;
4. a re-versioned corpus produced after any command-semantics change.

Failure of any item is structural `GATE_UNREADY`. It is not partial branch coverage and cannot be
masked by a known candidate defect.

## 6. Required next actions

1. Freeze the authoritative protocol verb set.
2. Make the panel dispatcher exhaustive and fail closed on unsupported verbs.
3. Implement and engine-cross-check `TRAIN`.
4. Add the command-dispatch and `m040` regression tests.
5. Re-version and rerun all 240 rows.
6. Recalibrate P4 and D-9 only against successful post-command state transitions.
7. Resume gate architecture revision 3, P4 and D-4 only after the repaired panel evidence lands.

## Final ruling

- **Unknown or unimplemented verbs must fail loudly.**
- **The two `m040` identities remain in the corpus as mandatory regressions; their old results do
  not remain in the accepted floor.**
- **The entire panel is re-versioned after `TRAIN` support.**
- **All current D-9 dispositions based on this panel are withdrawn; current status is
  `GATE_UNREADY` due to instrument unsupportedness.**

No bot, candidate, parent, detector, harness, host game, value protocol, TestSession, submission,
restore or Arena state was modified by this ruling.
