# Dance geometry G-1 fresh-archive review (2026-08-25)

Verdict: **G-1 REPRODUCED; measurements accepted with one explicit class correction for the
owner brief.** The headline whole-row result and controls reproduce. No cure, candidate, or Arena
action is authorized by this review.

## Independent execution

I archived `agent/claude_1@c5727dc642dd2cb4008157058ba80ab8646459f1` into a fresh temporary
directory, archived the declared replay inputs from `origin/agent/local_claude_1` at their repository
paths into a separate read-only input tree, and read `reread_shapes.py` from `origin/main`. I ran:

```text
python3 <archive>/claude_1/geometry1/run_geometry.py \
  --inputs <fresh-input-tree> \
  --reread <origin-main-reread_shapes.py> \
  --out <run1>

python3 <archive>/claude_1/geometry1/run_geometry.py \
  --inputs <fresh-input-tree> \
  --reread <origin-main-reread_shapes.py> \
  --out <run2> --peer <run1>
```

Both executions completed with 105 episodes and zero refusals. The fresh `geometry` and `controls`
files are byte-identical to the delivery:

- `geometry-2026-08-25.json`: `acb2feedd0fe81d399e0c5fcde555993801004d3be05c14ddd1a90baa3c5faf4`
- `controls-2026-08-25.json`: `b11894687d87282b72bc5bb36e7aecfae5f10cfe0d3324029cc5a524e06143a0`

K-4 passes: run 1 and run 2 have identical geometry and controls hashes. The regenerated
`determinism-2026-08-25.json` is not byte-identical to the published file for exactly two named
presentation fields: fresh `run_a`/`run_b` contain the temporary absolute directories, while the
published file contains `run A (published)` / `run B (second run, separate directory)`. Its four
semantic hashes are unchanged: both run hashes are `acb2feed…` for geometry and `b1189468…` for
controls. No count or verdict differs.

Reproduced controls: K-1 191/198 (96.46% under the published population); K-2 217/228 with all 11
exceptions explained; K-3 21/1,852 (1.13%); K-5 105/105, zero refusals; K-6 `R/False` 197,
`R/True` 1 and `H` vacuous; K-7 `8e2159e3…`; K-8 105/105; K-9 865/865. The M-1/M-2 headline
counts therefore stand as delivered, including `blocked_but_road_exists == 0` on both reads and the
older `nobody` partition 27 standing / 33 transient / 8 nothing / 0 undetermined.

## Rulings

### F-1 and the R1 edge: accept one r3 clarification

Add `NON_COST_BEARING_STATUS`, proven by `row.status` being one of the four statuses §R2 marks
non-cost-bearing. Exclude those rows from K-1's `d1 > d0` agreement denominator because that
comparison is deliberately undefined there. Report them beside the denominator, and retain the
stronger independent observable: the teammate occupies the forward cell on all 198 `R` turns.
Thus the cost-bearing K-1 is **191/191**, with seven `TARGET_OCCUPIED` `R` rows reported separately;
this is a population repair, not seven newly agreeing rows.

R1 should say: `n/a` when no cost-bearing turn exists; `0` when at least one cost-bearing turn
exists and none is blocked. Episode `900327649` / seat 0 / episode index 9 has 15
`TARGET_OCCUPIED` rows, zero cost-bearing rows, and must move from `0` to `n/a`. Re-issued pooled
classes are therefore `n/a` **1**, `0` **7**, `1–2` 40, `3–5` 15, `>5` 13, `inf` 29. Only the
v4 table changes (`n/a` 0→1, `0` 2→1); all M-1 blocked-turn counts, M-2 counts, controls, and
substantive findings remain unchanged.

This clarification matches §R1's stated semantics: `0` should mean a measured road existed at zero
extra cost, while `n/a` means the cost question was never measurable. It also prevents a
non-cost-bearing status from being mislabeled `UNOBSERVABLE_RESOLVER_STATE` when its observable
status is already published.

### F-2 / K-10: accepted

K-10 is a standing control: shape joins use source episode index and assert one-to-one before any
table is built. A derived `(game, seat, window_start)` tuple is not an identity because the source
contains a real collision at `900093265` / seat 0 / turn 80. The corrected 34 / 21 / 25 shape
counts are accepted.

### F-3: faithful implementation

Reconstructing `moving_ids` from each chosen target, rather than the post-resolution replay verb,
is faithful to the accepted arm predicate. It needs no definition change.

## Scope

`lateral_exists` remains an upper bound, and D-1 off replay remains an upper bound on every episode
count. This review does not decide a cure or candidate, re-open accepted r3 dance classification,
or authorize Arena work. No replay fetch, TestSession, sealed-map access, or peer-owned write
occurred.

DEFERRED: none. The G-1 fresh-archive replacement card is discharged by this review.
