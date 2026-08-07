# Scan-backed stop analysis after round 36 (claude_1, 2026-08-04)

Head: `claude_1/e7a-incremental-simplification/candidate-r36-delete-orphaned-carry-total.rs`,
**55,799 bytes**, SHA-256 `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`.
Cumulative: **−6,479 bytes from the programme's initial 62,278** (−10.4 %), −7,021 vs exact
live E7a (62,820).

## Why this analysis differs from the round-28 one

The round-28 inventory declared round 30 terminal by structural reading. It was wrong:
rounds 31–36 removed six more blocks worth 411 bytes. This analysis is instead produced by a
committed, re-runnable scanner (`cascade_scan.py`) whose classes are stated below, so the
claim can be audited and re-checked against any future parent.

It is still not a proof of minimality — only a statement that these classes are empty.

## Classes scanned on the round-36 source, and their results

| Class | Result |
|---|---|
| Function parameters with the same literal at every call site | **empty** |
| Constant local bindings | 4 hits, all `let mut` accumulators — rejected |
| Never-read / write-only struct fields | **empty** (round 34 consumed the only one) |
| Enum variants never constructed | **empty** |
| Uncalled functions | 1 hit, `fallback_second_troll` — rejected, passed as a function value to `unwrap_or_else` |
| Constant comparisons / constant boolean operands | **empty** (rounds 23, 31, 32 consumed them) |
| Duplicate or receiver-equivalent function bodies | **empty** (rounds 35–36 consumed the pair) |
| Struct fields assigned exactly one constant | **empty** |

## The one non-empty class, deliberately not consumed

**Single-call functions** (~38 remain, from 25-byte helpers to a 4,681-byte door-clearing
routine). Inlining them would shrink the source by roughly a signature each, but it deletes
no logic — it relocates it, and it would make the largest routines materially harder to read.
The frozen protocol's stated purpose is source simplification, and its round 1 inlined a
single-use *constructor* precisely because that removed unused configurability; a general
single-call function has no such property. Recommend leaving this class closed unless the
owner explicitly wants byte-golf, in which case it should be a separately named programme
with its own justification, not a continuation of this one.

## What the cascade looked like

Six of today's eight rounds existed only because an earlier round created them:

- round 5 (`minimum_worker_speed` field, 2026-08-03) → **round 33** (the parameter it fixed);
- round 10 (`persistent_regeneration` field) → **round 31** (the parameter it fixed) →
  **round 32** (a second parameter, unlocked only when round 31 replaced a forwarded
  argument with a literal);
- round 26 (`opening_options` parameters) → **rounds 29–30** (the locals they shadowed);
- round 35 (duplicate helper) → **round 36** (the orphan it left).

The gap between unlock and deletion was up to 28 rounds, which is why iteration to a fixed
point — re-scanning after every accepted round — matters more than any single inventory.

## Recommended next step

The programme is at a natural terminal point. Rounds 29–36 are unqualified beyond the
per-round gates; the integrator's accumulated checkpoint (516-task development panel, then
the deferred untouched range) is the appropriate close-out, exactly as after round 22.
