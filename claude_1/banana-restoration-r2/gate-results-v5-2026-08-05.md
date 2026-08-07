# Gate results v5 — banana-restoration-r2 round-5 GREEN (R-5 banking livelock fixed)

Date: 2026-08-05
Task: `20260802-banana-restoration-r2`, round-5 phase 2 (GREEN): repair the
MULTI_UNIT_COORDINATION defect diagnosed in `diagnosis-r5-2026-08-05.md`
(RED evidence: `red-evidence-9f5ef833-2026-08-05.md`).
Toolchain: rustc 1.97.1, `--edition=2021 -O` (NO `-Awarnings`), Python 3 stdlib
only, fully deterministic.

## Candidate

- NEW: `candidate-banana-r2.min.rs`, **77,299 bytes**, sha256
  `47c98f5354ec89ea032c425394287ee24955c75846690d3527ee60ee2d167834`
- OLD (round-5 RED): 77,397 bytes, sha256
  `9f5ef8336c5268927dd3aef873a1a348dd9e0bb43c2cc1e505b14730352db8a2`
  (canonical artifact commit `b358124f`)

## The fix (block-i1.rs only, the C8 third protection layer)

The confirmed mechanism (diagnosis H3): C5's third layer passed
`banana_forbidden = {mother}` into
`MoisanBot::resolve_move_conflicts_with_priority_and_forbidden`, vetoing the
non-priority full carrier's one-step landing on the mother every second turn.
On maps where the diagonal mother is the BFS-min articulation cell of every
door route this produced the parity-stable accept/detour oscillation (the
host's 225-turn episode; locally the 38-state `(4,2)<->(3,2)` cycle).

**Design decision (against I-29's text).** I-29's protection intent is that
the banana wrapper reserves exactly one protected cell so the mother is not
chopped, planted over, or disturbed — it says nothing about movement across
the cell, and standing on a plant's cell is a legal game action (units
CHOP/HARVEST from the plant's cell; `control-r5-compliant` transits (2,2)
legally). Each protection concern is already carried by a dedicated layer:

- CHOP/HARVEST on the mother by a non-resident: the C5 SECOND layer WAITs
  every such verb (block-i1.rs, on_mother/harms_mother post-edit) — D-8 chop
  protection untouched, NOT reopened;
- PLANT-over: illegal on an occupied plant cell, and candidate-side the I6
  retain filter removes every `Target::Cell == protected` candidate — I-13
  NOT reopened;
- camping-as-a-goal: the I6 retain filter removes every
  `Target::Tree|Bank|Cell == protected` candidate, so no non-resident ever
  SELECTS the mother as a movement destination.

Therefore the mother was **removed from the movement-forbidden set
entirely** (the first of the two sanctioned options): the C8 call is now
`MoisanBot::resolve_move_conflicts_with_priority(view, &mut commands,
{resident})` — resident move priority retained, transit landings legal.

Why not the second option (destination-veto at the resolver stage): tried
and rejected on evidence. The inner `MoisanBot::resolve_move_conflicts`
REWRITES every accepted move to its one-step landing BEFORE the wrapper's
post-edit runs (research line ~1015), so at the C8 stage the command target
IS the landing — a "destination == mother" veto is indistinguishable from
the old landing veto and re-livelocked the carrier (observed: `MOVE 2 3 2`
then WAIT forever at (3,2), still no DROP). Destination-level exclusion
belongs at (and already exists in) the I6 candidate layer.

No test, regression check, detector, oracle, ledger, or pre-review tool was
modified.

## Ladder

### 1. Build — PASS

`python3 build_banana_candidate.py`: all mechanical asserts green (parent
sha `a8eb3b2b...` verified, anchors unique, per-block compact round-trip,
insertions unique/pairwise non-substring, inverse transform restores the
parent byte-for-byte). I1 insertion 14,128 bytes; total 77,299 (< 100,000
budget). New sha recorded above.

### 2. Compile — PASS

`rustc --edition=2021 -O` (no `-Awarnings`): exit 0, **zero warnings**
(empty stderr), both compact and research sources. Empty stdin: clean exit 0.

### 3. R-5 FAIL -> PASS (the round-5 red/green flip)

| bytes | R-5 two-worker-full-cargo-banking |
|---|---|
| OLD `9f5ef833...` (rebuilt from git `b358124f`, sha re-verified) | **FAIL, exit 1** — both violations of the red evidence reproduced verbatim (38-state `(4,2)<->(3,2)` alternation turns 3-40 + horizon clause). Test unchanged. |
| NEW `47c98f53...` | **PASS, exit 0** — `bank_turns {"2": 6}`, `episodes: []` |

Actual banking turns on the NEW bytes (committed
`traces/r5-two-worker-banking-commands.txt`):

```
t1 MOVE 2 5 2   (6,2)->(5,2)
t2 MOVE 2 4 2   (5,2)->(4,2)
t3 MOVE 2 3 2   (4,2)->(3,2)
t4 MOVE 2 2 2   (3,2)->(2,2)  <- legal TRANSIT across the protected mother
t5 MOVE 2 1 2   (2,2)->(1,2)  <- the (1,2) door
t6 DROP 2                      <- banks; wood credited t7
```

Strictly monotone door approach (I-20), commitment persists to the DROP
(I-19), full carrier banks within the 30-turn horizon (I-21). The resident
u0 WAITs on its door reservation throughout; the mother is never chopped,
harvested, planted over, or camped.

### 4. Full regression suite on NEW bytes — exit 0

`regression_tests.py all --binary <47c98f53 build>`: R-1, R-2a, R-2b, R-3a,
R-3b, R-4, R-5 all PASS — verdicts unchanged from the v4 ledger for
R-1..R-4. Controls: all compliant controls PASS; `control-r3a-doomed` and
`control-r5-oscillator` FAIL as designed (both FAIL-direction non-vacuity
controls retained).

### 5. TIER-P / TIER-C / detectors / t1-t6 — PASS, zero byte drift

- TIER-P 7/7 PASS, fixtures **byte-equal** to the committed
  `tier-p-golden.json` (committed golden untouched in git).
- TIER-C 8/8 PASS (`tier-c-results-v5-2026-08-05.json`).
- `python3 -m unittest test_trace_detectors`: **28/28 OK** (unmodified).
- `python3 conversion_race_oracle.py`: self-test OK.
- t1-t6 regeneration (`make_banana_traces.py` default, `--dynamic`,
  `--round3`, exits 0/0/0): **all committed trace files byte-identical**
  (`sha256sum -c` all OK; `git status traces/` clean apart from the two NEW
  r5 files). Analysis of why no trace can move: the change is observable
  only when a non-resident mover's one-step landing (or detour cell) equals
  the protected mother. In t1/t2 the second worker's routes never cross the
  diagonal mother (door routes are orthogonal-adjacent to the tent and the
  mother is diagonal-only by construction); in t3/t4 the flip releases the
  protection before any such geometry arises; t5/t6 are scripted. Hence
  byte-identity, and no per-diff I-29/I-13/D-8 justification is owed.

### 6. Readable research source — PASS

`rustfmt --edition 2021 --emit stdout < candidate-banana-r2.min.rs >
research-banana-r2.rs`: 3,423 lines, 152,095 bytes, sha256
`599313bc98dc540344cb511ba28b7abecd6590acb53fc3d0fa69966b8abb55cb`.
Compiles standalone with zero warnings. Behavioral equality:

- TIER-P 7/7 fixtures byte-equal to the same committed golden; TIER-C 8/8
  PASS on the research source;
- closed-loop referee re-runs t1 (300), t2 (60), t3 (20), t4 (20):
  transcript+commands **byte-equal** to the committed traces;
- r3a/r3b/r4/r5 scenarios: research-vs-compact paired runs **byte-equal**;
  the research-driven r5 run is also byte-equal to the committed green
  trace.

### 7. Pre-review — **CLEAR, exit 0**

Config: the R-5 pair's `old_source_git` already pins the OLD bytes
(`git:b358124f:...candidate-banana-r2.min.rs`, sha re-verified =
`9f5ef833...`), and the I-19/I-20/I-21 claims already cite
`traces/r5-two-worker-banking-commands.txt` — now committed, produced by
`regression_tests.py r5-bin --outdir traces` from the NEW bytes. Post-fix
claims updates only (banana-r2-claims.json): the three R-5 falsifying_check
narratives now state FAIL-on-old-bytes / green-on-47c98f53 with the t6
banking DROP, and the I-10a claim names the current bytes.

`python3 pre_review.py --config banana-r2-task-config.json --report
pre-review-r5-green-2026-08-05.md` -> **CLEAR (0 findings), exit 0**:

- trace-provenance, single-model: clear;
- red-reason: all 5 pairs RED for the right reason on their old bytes,
  including `R-5-vs-9f5ef833` (exit 1, all 5 signature regexes matched);
- claims-coverage: I-19, I-20, I-21 each covered by existing
  **candidate-driven** evidence (plus I-9/I-10a/I-7/D-8 as before); all
  required deliverables present; ledger class MULTI_UNIT_COORDINATION
  covered by the configured red-reason check.

Report: `claude_1/pipeline/pre-review-r5-green-2026-08-05.md`.

## Notes

- Only `banana_blocks/block-i1.rs` changed functionally; regenerated
  artifacts: `candidate-banana-r2.min.rs`, `candidate-banana-r2-manifest.json`,
  `research-banana-r2.rs`; new artifacts: the two committed r5 green trace
  files, `tier-c-results-v5-2026-08-05.json`, the pre-review report, and
  this ledger.
- Trace byte changes: **none** (t1-t6 all byte-identical to committed).
