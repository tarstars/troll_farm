# Adversarial review — P4 post-`C_T` referee-state rule

- Reviewer: `chatgpt_1`
- Task: `20260808-phase1-work-allocation`, item 3
- Incoming handoff:
  `coordination/messages/claude_1/20260809T003000Z-20260808-p4-post-ct-handoff.md`
- Reviewed artifact commit:
  `047ccc5f0f66011458607ea0975207b0fb5884dc`
- Reviewed paths:
  - `claude_1/pipeline/p4-post-ct-rule-2026-08-08.md`
  - `claude_1/pipeline/fuzz_panel.py`
  - `claude_1/pipeline/test_fuzz_panel.py`
- Review mode: exact committed-blob/adversarial review; no private-host execution claimed
- Final verdict: **`REVISION_REQUIRED`**

## Executive conclusion

The final-turn boundary defect is real. A transcript containing `S_1..S_T` and `C_1..C_T`
cannot infer the result of `C_T` from `S_T`; using the referee object after the command has been
applied is the correct direction. Extending `stall_windows` through turn `T` and treating a
final inventory/cargo change as progress is a useful local correction.

The artifact is not adoptable as a calibrated P4 gate. Its complete 240-game measurement was
produced by the panel referee now known to parse and silently discard `TRAIN`. Two `m040` games
therefore emit a no-op `TRAIN` for 166 and 182 turns while every existing property, including P4,
reports clean. That invalidates the corpus as evidence that the residual P4 windows are genuine or
that the rule changes zero legitimate verdicts.

There is also a semantic defect independent of TRAIN: `work_remaining()` is documented as an
exact test that the world offers a resource action, but it actually returns true for any reachable
plant regardless of ripeness, worker capability, free capacity, payoff horizon, or whether an
action can make the inventory/cargo progress P4 measures. The report itself leaves the decisive
question open — whether a reachable choppable tree is a liveness obligation — while the code has
already answered it “yes.” Twenty-one of the thirty reported windows depend on that answer.

The post-`C_T` code should be retained as a candidate boundary fix, but P4 remains
`GATE_UNREADY` until the referee is repaired, the obligation/progress contract is frozen, and the
measurement is rerun on a re-versioned corpus.

---

## Accepted findings and implementation direction

### A1. The final-turn observability gap is genuine

`progress_turns()` observes only `S_t -> S_{t+1}` for `t < T`. Without a post-command state,
turn `T` can neither be credited with progress nor counted as a no-progress turn. This is a real
asymmetry and should be closed.

### A2. Candidate-side post-state is the right source

`run_pair()` retains `ref_c` after `C_T` has been applied. Using that candidate referee state,
rather than the parent or an inferred command effect, preserves the absolute/non-comparative P4
rule.

### A3. Zero verdict changes can be a valid outcome

A correctness repair need not change the current floor. “0 flips” is not itself a failed
experiment. The issue is whether the instrument and semantic contract were valid enough for that
negative result to mean what the report claims.

### A4. The games-versus-windows correction is useful

The report consistently distinguishes 29 games from 30 P4 windows and identifies 32 as the D-1
game count. That reporting discipline should be retained.

---

## P4R-1 — all floor conclusions are instrument-invalid under the broken TRAIN referee

The artifact reruns the parent-vs-parent floor through the same `FuzzReferee` that does not execute
`TRAIN`. The later full-panel reachability audit found two one-worker `m040` rows in which the bot
emits `TRAIN` on every turn from 35 or 19 through turn 200, while the referee silently ignores it.
Those rows report:

```text
block=False
D-1..D-9 = 0
P4 = clean
```

A command stream that spends 83–91% of the game issuing an unsupported no-op is exactly the kind of
liveness failure P4 is intended to expose, yet the floor calls it clean. The panel cannot currently
establish either of these report claims:

- “all 30 residual windows are genuine stalls”; or
- “the post-`C_T` fix changes no legitimate verdict.”

The current numbers may still reproduce deterministically, but they reproduce a non-conformant
referee. Reproducibility is not validity.

**Required repair:** implement an exhaustive command dispatcher and engine-conformant `TRAIN`,
hard-error every parsed but unsupported command, re-version the corpus, retain both `m040` rows as
mandatory red regressions, and rerun the before/after P4 comparison. Old floor counts remain
archival evidence of the broken instrument only.

---

## P4R-2 — `work_remaining()` is not the exact actionability predicate its contract claims

The function returns true when:

1. any own unit carries any item; or
2. any plant cell is reachable by any own unit.

It does **not** require that a legal progress-producing action exists. It ignores, among other
things:

- harvest power and fruit ripeness;
- chop power and whether a chop can complete before the horizon;
- free carrying capacity;
- whether a loaded unit has a reachable bank door or legal planting cell;
- resource kind and legal PLANT target;
- whether the only reachable plant is opponent-owned or strategically irrelevant;
- whether the action can change the own inventory/cargo quantity P4 calls progress.

A reachable plant is therefore only a geometric opportunity proxy. The docstring's statement that
it is an exact test that the world “still offers the own player a resource action” is false.

The artifact itself exposes the consequence: 21/30 windows are justified only by “chop available,”
and asks whether a reachable choppable tree is a liveness obligation. That is not a side question.
It is the semantic premise already encoded in `work_remaining()`.

**Required ruling:** freeze the P4 obligation contract before adoption. Either:

- define an exact executable actionability oracle using the referee rules and worker state; or
- explicitly define P4 as a broader geometric-service obligation and defend why that is the owner
  rule.

Until then the P4 branch is `UNPROVEN`, not calibrated.

---

## P4R-3 — “legal CHOP available” does not establish the progress quantity P4 measures

P4 defines progress as an own-inventory change or an own-unit cargo-vector change. A legal CHOP
that damages a tree without felling it changes neither. Movement toward a bank, target acquisition,
health reduction, and other real work also do not count.

The report therefore mixes two different predicates:

```text
obligation evidence: a legal resource action exists
progress evidence: inventory or cargo changed
```

A controller can execute productive CHOP commands for several turns and still accumulate a P4
stall. Conversely, a harmful bank PICK changes both inventory and cargo and is counted as progress.
The 60-turn horizon may make some multi-turn actions safe in the current maps, but that is a
measurement-specific observation, not a semantic proof.

**Required repair:** state and independently test which outcomes count as liveness progress. At
minimum add fixtures for:

- non-final and final CHOPs that reduce health but do not fell;
- monotone banking movement without immediate cargo change;
- harmful PICK from the bank;
- cargo loss or unit disappearance;
- successful PLANT and DROP;
- reachable plant with no capable/free worker.

Do not use “an action was available” as proof of “inventory/cargo progress was owed” without an
explicit bridge between them.

---

## P4R-4 — missing post-state fails open

`eval_p4(..., post_state=None)` silently restores the old behavior and omits turn `T` from the
obligation. Once post-`C_T` evidence is part of the required P4 contract, absence of that evidence
is an instrument-readiness failure, not a valid alternate mode.

A future caller can therefore produce a superficially valid result while lacking the exact state
this repair says is required. This conflicts with the gate architecture's fail-closed principle.

**Required repair:** make the post-state mandatory in the production gate, or return an explicit
`GATE_UNREADY`/coverage record when it is unavailable. A compatibility helper may retain the old
behavior only outside verdict-producing paths and must be named accordingly.

---

## P4R-5 — the load-bearing analysis and mutation evidence is not committed

The report's central evidence comes from scratch-only files:

- `analyze.py`;
- `classify2.py`;
- `postct_scan.py`;
- `mutate.py`;
- before/after game archives and slim result JSON.

Only hashes and prose summaries are committed. Another reviewer cannot reproduce the reported
30-window classification, 29/29 replay equality, actionability result, or “8 caught / 0 survived”
mutation claim from artifact commit `047ccc5f…` alone.

The committed unit tests do exercise the helper functions, which is valuable, but they are not a
substitute for the full-panel classification and mutation ledger the conclusion relies on.

**Required repair:** commit the deterministic analyzers, exact mutation list/runner, normalized
machine-readable before/after summaries, and content hashes for the archived game payloads. Ensure
the rerun is against the repaired referee and the result embeds the candidate, parent, referee,
parser, config, map generator, and analyzer hashes.

---

## P4R-6 — the proposed D-7 final-turn exception would hide a real terminal loss

The report calls the naive post-`C_T` D-7 episode on `m019-s0` a false positive because the final
command is `PICK 0 BANANA`, then suggests excusing any resource “acquired with no remaining turn to
discharge it.”

A final PICK from the bank is not equivalent to a final HARVEST. It removes a score-bearing banana
from inventory and leaves it in cargo at terminal scoring. The action can reduce terminal score and
is a genuine value loss. Widening the final-six-turn exception from fresh harvest provenance to any
acquisition would make that loss invisible.

**Required repair:** do not adopt the proposed broad exception. Final-turn ledger semantics must
distinguish at least:

- newly harvested value with no remaining action opportunity;
- bank withdrawal that destroys terminal inventory score;
- successful seed consumption;
- failed/unsupported command;
- cargo already old before the final turn.

The post-`C_T` D-7 work should remain paused until the referee executes every command and the
terminal scoring semantics are frozen.

---

## P4R-7 — the post-state is only trustworthy when command execution is proven

`post_ct_state(ref_c)` serializes the final referee object, but the object itself does not record
that every command in `C_T` had an implemented transition. The TRAIN defect demonstrates that a
state can be deterministic and parseable while silently omitting the command's effect.

P4 needs an execution-validity input alongside the world state:

```text
all parsed commands recognized and dispatched
all action preconditions/referee outcomes recorded
no command silently ignored
```

Without this, post-state equality can mean either “the command made no progress” or “the referee did
not implement the command.” Those are opposite conclusions.

---

## Required next revision

1. Repair and re-version the panel referee first; hard-error unsupported commands.
2. Freeze an exact P4 obligation/actionability and progress contract.
3. Make post-`C_T` state and command-execution validity mandatory for verdict production.
4. Commit the classification and mutation tooling/results.
5. Rerun all 240 rows, including the two `m040` red regressions.
6. Report P4 windows separately by:
   - executable progress-producing obligation;
   - geometric opportunity only;
   - unsupported-command/instrument error;
   - terminal boundary.
7. Keep the D-7 final-PICK case blocking unless an owner-frozen terminal-score rule says otherwise.

## Final disposition

**`REVISION_REQUIRED`.**

The `S_T -> post-C_T` boundary mechanism is directionally accepted and should not be discarded.
The current calibration, “30 genuine stalls” conclusion, and adoption claim are not valid under the
broken referee and unresolved P4 semantics. P4 remains `GATE_UNREADY` pending the repairs above.

No panel implementation, detector, bot, candidate, parent, host run, value protocol, TestSession,
submission, restore, or Arena state was changed by this review.
