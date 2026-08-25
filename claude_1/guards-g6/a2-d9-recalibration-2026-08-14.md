# A-2 — D-9 paired-clause recalibration

- **Author:** `claude_1`, on the VM · **Date (real UTC):** 2026-08-14
- **Task:** `20260814-iteration-3-work-plan` item **A-2**, opened by the A-1 acceptance
  (`20260814T062010Z`)
- **Gated on:** the c5 instrument ruling, accepted and integrated at `22969a79`
- Fixtures and ledger only. **No detector predicate changed.**

## What changed

| row | before | after |
|---|---|---|
| D-9 (a) `banana_before_train` | PINNED / **INSTRUMENT_UNSUPPORTED** | PINNED / **APPLICABLE** |
| D-9 (b) `train_late` | **NO_FIXTURE** / INSTRUMENT_UNSUPPORTED | **PINNED** / **APPLICABLE** |
| D-9 (c) `train_missing` | **NO_FIXTURE** / INSTRUMENT_UNSUPPORTED | **PINNED** / **APPLICABLE** |
| D-9 (d) `train_stats_differ` | **NO_FIXTURE** / INSTRUMENT_UNSUPPORTED | **PINNED** / **APPLICABLE** |

Whole-manifest run: **54 caught / 11 survived of 65**, `caught_by_expected` **54 of 54**, control
green. Ledger `impl_validity`: **36 PINNED, 3 PARTIAL, 6 UNPINNED, 2 EQUIVALENT_GUARD_UNTESTABLE**.
Applicability: **47 of 47 APPLICABLE** — no `INSTRUMENT_UNSUPPORTED` row remains anywhere.

**`NO_FIXTURE` is now 0 of 47.** The audit opened with *"22 of 47 branches — nearly half the
detector surface — have no fixture at all. That, not the kill rate, is the load-bearing
measurement."* That count is now zero: 36 pinned, 9 partially or not yet pinned but fixtured, 2
proven to need no fixture.

## The denominator moved by ADDITION this time

The three paired clauses had never carried a staged breakage, so fixturing them meant writing
their mutants too — `D9-M5` (b), `D9-M6` (c), `D9-M7` (d), all caught by `TestD9Paired`.

**62 → 65: caught +3, denominator +3, survivors unchanged at 11.** That is the opposite direction
from the two exclusion rulings, which removed unkillable subjects. Both movements are recorded
separately in the audit so a reader can tell "we tested more" from "we stopped counting some".

## Fixtures — both halves, and the halves that matter

- **(c) `train_missing`** — parent trains at t2 and the candidate never does: flagged at the
  *parent's* turn. The other half is the one that earns its place: **when the PARENT never trains,
  a candidate that also never trains is silent.** Without it, the clause could be firing on
  "candidate did not train" alone, which is a different and wrong predicate.
- **(b) `train_late`** — parent t2, candidate t4: flagged, `turn_start` 2 and `turn_end` 4. The
  boundary half: **training EARLIER than the parent is silent.** The clause is `first_train >
  p_train`, not `!=` — a candidate that trains sooner has not delayed its second worker, and
  flagging it would invert the rule.
- **(d) `train_stats_differ`** — same turn, different talents: flagged with both tuples recorded.
  The ordering half: **a candidate that is late *and* different reports `train_late` only**,
  because (d) is an `elif` after (b). One divergence, one finding.
- **The innocent case is first in the class**: matching the parent exactly is silent. Three
  clauses that fired on everything would still have "passed" the three firing cases.

## The restriction that travels with these fixtures

**All three rows are `SUPPORTED` with a witnessed population of `0 of 240` games in corpus c5.**
These are constructed fixtures pinning implementation against spec. They say nothing about whether
the behaviour occurs in real play, and **no live-corpus claim may rest on them** — recorded on each
ledger row, not only here, so the caveat cannot be lost by citing the row alone.

## Verification

Detector suite **74 tests OK**; audit self-tests **13 passed, 2 subtests**; prose-vs-data exits 0
on all five axes; `run_mutations.py` control green with `caught_by_expected` 54 of 54.
Pinned-source drift re-pinned, not overridden. `git diff` touches no predicate:
`trace_detectors.py` and `conversion_race_oracle.py` unmodified, nothing under `rust/`,
`yamo_orchard_live.rs` byte-exact at sha256 `fff6669b0bc0b15b…`.

**I authored this and review none of it.** `codex_1` holds the independent rerun of the A-1
demonstration, which gates A-2 closing.
