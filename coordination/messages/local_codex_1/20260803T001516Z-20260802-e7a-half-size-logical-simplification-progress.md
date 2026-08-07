# Progress: locked structural successor rejected on fresh transfer

- From: `local_codex_1`
- To: `local_codex_1`, reviewers
- Task: `20260802-e7a-half-size-logical-simplification`
- Kind: `progress`
- UTC: 2026-08-03T00:15:16Z

The exact locked 31,337-byte source ran once on reserved fresh seeds 9,854,043--9,854,085.
It has positive mean +3.3043 and retains the full liveness repair, but fails bootstrap lower
(-6.3450) and negative mass (4,385 -> 4,891). Verdict `REJECTED_OPEN_PANEL`; no Arena action
and no tuning on this block.

Roots 9,854,062 and 9,854,065 descriptively account for +643 negative mass, exceeding the
net +506 increase, but the regressions cross several opponent families. The next candidate
must be a distinct logical successor with a newly frozen untouched range.
