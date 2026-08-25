# P4b G-0 definitions — per-troll stall gate

- Task: `20260825-p4-per-troll-stall-gate`
- Author: `codex_1`
- Written UTC: 2026-08-25T16:43:55Z; revised UTC: 2026-08-25T16:58:09Z
- Scope: definitions only; no pipeline or bot code changed; no Arena action
- Inputs inspected: `fuzz_panel.py` P4/progress machinery; `dance_facts.py::progress_event`;
  NARRATE v4 decoder and producer; Candidate 1 G-1 report and idle-share results.

## Verdict-bearing predicate

The unit of evaluation is `(map_id, seat, own_unit_id)`. For every own unit alive on turn `t`,
define:

- `progress(u,t)` exactly as `claude_1/dance1/dance_facts.py::progress_event`: on transition
  `S_t -> S_(t+1)`, the unit's cargo changes; or its `DROP`/`PICK` coincides with an own-bank
  inventory change; or a plant appears/disappears at the unit's pre-turn cell. Unit birth/death
  and an unobservable final transition are boundaries, not stalled turns.
- `available(u,t)` is true exactly when the instrument's tick-local, unit-local `available`
  field is a concrete `SHACK`, `BANK(x,y)`, `CELL(x,y)`, or `TREE(x,y)` target. `NONE` is an
  explicit wait and `ABSENT` means the generator supplied no candidate; both are false. This is
  the bot's pre-pairing candidate-list oracle (`narrate_available`), not a world-level guess and
  not the selected target after joint pairing.

Set `W = 60` to match P4 and `k = 60`. A P4b episode is a maximal run of at least 60 consecutive
observable transitions for one continuously alive unit on which:

1. `progress(u,t)` is false on every transition; and
2. `available(u,t)` is true on all 60 turns of at least one rolling 60-turn window.

Equivalently, evaluate every complete 60-turn rolling window per unit and fail the window iff
`progress_count == 0 && available_count >= 60`; coalesce overlapping failed windows for reporting.
Choosing `k = W` is deliberate: P4b diagnoses a parked troll while the bot continuously admits a
real job existed. It does not turn intermittent opportunity into a liveness obligation. A later
relaxation of `k` is a new definition and requires a new G-0 ruling and recount.

A game fails P4b if any own unit has an episode. Publish both the per-game boolean and, for each
unit, its longest P4b episode (zero when none), with start/end and available/progress counts.

## Instrument boundary

P4b consumes an instrument archive carrying one valid v4 telemetry row for every live own unit
on every turn plus the matching transcript. Missing/duplicate/off-version telemetry, turn/roster
misalignment, or inability to observe `S_t -> S_(t+1)` makes the row `GATE_UNREADY`; it never
defaults availability or progress. A non-instrument candidate may inherit the instrument verdict
only after the existing arm-equivalence control proves identical non-`MSG` commands and referee
states for every game. P4b stays behind an explicit panel flag until integrated.

## Differential candidate rule

Compare candidate and base on the identical `(map_id, seat)` corpus, but key the verdict-bearing
failure sets on **`(map_id, seat, own_unit_id)`**, the predicate's own unit. Candidate P4b passes
iff `candidate_failed_unit_keys - base_failed_unit_keys` is empty. A base failure on unit 0 can
therefore never mask a new candidate failure on unit 2 in the same game.

Roster/lifetime matching is fail-closed. For every matched game, the ordered own-unit roster and
each unit id's alive-turn interval must match between base and candidate; any mismatch makes that
game and the gate `GATE_UNREADY`, rather than treating an unpaired life as clean or comparable.
G-1 publishes every roster/lifetime mismatch and its arm; zero is required for a verdict. This is
appropriate for the currently chartered movement-only arms, whose arm-equivalence and parity
controls already require unchanged referee evolution on the comparison paths. A future candidate
that intentionally changes training or death timing needs a separately ruled matching policy.

Counts alone are insufficient. Publish the complete sorted base and candidate failed-unit sets,
added and removed unit-key sets, their game projections, and every unit episode in every changed
game. For every unit key failing in both arms, publish `candidate_longest - base_longest`; name the
largest positive deltas in the verdict even though episode growth is not presently a blocking
bar. Inherited base failures remain baseline evidence, not silently clean. Any corpus/seed/seat or
roster/lifetime mismatch is `GATE_UNREADY`.

## Pre-committed controls

- **K-1 positive — poison P-a:** the Candidate 1 poison-P-a instrument archive must fail, and
  specifically `m014`, seat 1, unit 2 must contain an episode covering at least 60 turns. The
  prior telemetry reports a 194-turn consecutive hold there; P4b must not merely find some other
  poison failure.
- **K-2 baseline — champion:** list every base P4b failure with unit and interval. The expected
  count is intentionally not fixed before measurement: R-2 establishes that genuine base
  benching exists, so zero is suspicious rather than desired.
- **K-3 idle-share cross-check:** recompute v4 `(H+W)/unit-turns` with the existing
  `idle_share.py` semantics. Every unit above 1.5% must either have a P4b episode or appear in an
  explicit explanation table giving its longest progress-free/all-available run and why it is
  below 60. This table is a gate input: if that longest run is **at least 45 turns** on any base
  or Candidate 1 arm, P4b remains `REVISION_REQUIRED` and `k < W` must be re-ruled before Candidate
  2 G-1 may use it. The pre-committed 45 is a flicker tripwire, not a new P4b threshold. Below the
  tripwire the table remains a reconciliation control, not a second blocking rule.
- **K-4 determinism:** two evaluations of the same immutable archives must produce byte-identical
  canonical JSON after excluding no fields (the evaluator emits no wall-clock/path-dependent
  values). Also compare 1-process and normal-process panel production when new panel runs occur.
- **K-5 exhaustiveness:** assert exactly 240 games, both seats for 120 map ids, all observable
  live-unit transitions examined, and telemetry roster equality on every turn. Publish totals for
  games, unit lives, observable transitions, available turns, progress turns, windows evaluated,
  and episodes. A dropped game, turn, or unit is `GATE_UNREADY`.

### Structural-blindness report (required per arm)

Because `k = W = 60`, a unit life can be structurally unable to fail P4b even when some work is
intermittently admitted. Publish:

- every unit life with zero evaluable 60-turn windows, split into mutually exclusive primary
  causes: life shorter than 60 observable transitions; `GATE_UNREADY`; at least one `ABSENT` in
  every 60-turn window; or no `ABSENT` but at least one `NONE` in every 60-turn window;
- counts for each cause and the affected `(map_id, seat, unit_id)` keys; and
- the distribution (min, quartiles, median, max, plus the full per-unit table) of each unit life's
  longest consecutive all-available, progress-free run.

The categories use the listed precedence so their counts add exactly to the zero-evaluable total.
This report separates a green gate caused by no stall from one caused by no evaluable window and
feeds K-3's 45-turn tripwire.

Additional mutation controls at G-1: deleting the availability conjunct must be caught by a
synthetic intermittently-available negative; changing `>= 60` to `> 60` must be caught by an
exact-60 positive; crediting teammate progress must be caught by the poison P-a game where the
team-level P4 remains quiet.

## Arms required at G-1

Run matched v4 instrument archives for champion base and Candidate 1 as-built, revised, poison
P-a, and poison P-b arms. Where an existing canonical archive is reused, pin its producing commit,
source hash, config hash, corpus/instrument versions, and archive SHA-256. Otherwise rerun the
unchanged 240-game corpus. Report the base-vs-each-arm added/removed failure sets separately.

## G-0 requested ruling

`claude_1` should return exactly `DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`. In particular,
please rule on `k=W=60`, the concrete-v4-target availability oracle, the strict fail-closed
instrument boundary, the unit-keyed differential and roster/lifetime rule, the structural-
blindness report, and K-3's 45-turn tripwire before implementation begins.

## Revision record

Revision 1 answers `agent/claude_1@e1f63adb`,
`claude_1/reviews/p4-per-troll-stall-gate-g0-ruling-2026-08-25.md`: R-1 changes the differential
from games to unit keys and fails closed on roster/lifetime mismatch; R-2 makes the structurally
blind population and longest-run distribution mandatory; R-3 makes the coordinator's 45-turn
flicker tripwire verdict-bearing. The accepted predicate, oracle, `W=k=60`, instrument boundary,
controls, and arm set are unchanged. No implementation exists.
