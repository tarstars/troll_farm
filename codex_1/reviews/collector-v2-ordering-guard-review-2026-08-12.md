# Collector-v2 ordering guard review — 2026-08-12

- Reviewer: `codex_1`
- Pinned implementation: `b713ea40a0a88e95be2cbf04e38b747135053a9f`
- Scope: direct oldest-first ordering guards added after cross-review
- Verdict: **ACCEPTED**

The new tests pin the load-bearing contract directly: `Cursor.unseen` returns the complete,
deduplicated unseen set in ascending order, including after the seen set removes the lowest IDs.
They use several candidate populations, including current-shape nine-digit IDs. D9 removes the
sort from `Cursor.unseen`, so loss of that contract is mechanically observable without depending
on the downstream cap test or incidental set iteration order.

Independent execution at the pinned commit:

- Offline collector suite: 86 passed.
- B4 mutation drive: 25 defined, 25 applied, 25 caught, zero survivors, exit 0.

No production behavior changed; this strengthens evidence for binding design point 5 and clears
the ordering-test weakness identified in cross-review.
