# Apple orchard cost in readable lines

## Answer

Under one deterministic readable expansion, physically removing the apple-orchard feature removes
**586 code lines**. The exact live E7a source expands to 2,507 physical lines (2,502 code lines),
while the same-parent orchard-stripped source expands to 1,921 physical lines (1,916 code lines).
That is 23.4% of the readable code under this layout. The canonical minified result remains
15,013 characters, or 23.9% of the live submission.

| Same-parent form | Physical lines | Code lines | Compact characters |
|---|---:|---:|---:|
| Exact E7a with orchard | 2,507 | 2,502 | 62,820 |
| Orchard activation disabled, code retained | 2,500 | 2,495 | 62,581 |
| Orchard physically stripped | 1,921 | 1,916 | 47,807 |

Disabling the activation branch accounts for seven readable lines. Removing the implementation that
then becomes unreachable removes another 579 lines.

## What was physically removed

| Orchard-exclusive group | Canonical readable lines |
|---|---:|
| Phase, geometry, timing, and wrapper-state types | 25 |
| Site selection, activation economics, planting, camping, protection, and maintenance helpers | 402 |
| Per-turn orchard driver implementing the `Bot` interface | 117 |
| Worker/tree reservation channel, import, and `main` wiring | 42 |
| **Total** | **586** |

Generic apple parsing, harvesting, chopping, carrying, banking, and denial remain because the base
policy uses them independently of the protected orchard.

## Why this does not use the old 6,024-line file

`rust/src/bin/yamo_orchard_live.rs` is protected and was not changed. More importantly, it is not
the readable parent of the deployed 62,820-character lineage: it is 275,377 bytes and contains
substantially more code. Comparing line deletions there would not match the already measured live
feature.

Instead, the builder adds only whitespace and a four-line header to each exact compact same-parent
source. Compacting every readable copy reproduces its known parent hash exactly after restoring the
lineage's trailing newline. This makes the 586-line number reproducible rather than an estimate.

## Verification

- all three readable sources compile optimized and handle empty input cleanly;
- all three exact compact parents pass 10/10 semantic fixtures;
- readable exact E7a matches 25/25 packet games and 7,234/7,234 commands;
- activation-disabled differs only in known orchard game `897833045`, turn 79;
- readable stripped matches readable activation-disabled in 25/25 games and 7,234/7,234 commands;
- the protected source remains SHA-256 `fff6669b...`;
- no Arena or TestSession action occurred.

Readable LOC depends on formatting, so the report states the layout explicitly: one statement per
line; four-space blocks with each closing brace under its opener; spaced operators, separators and
comparisons, with arithmetic, borrows and generics left tight; lines over 100 columns split at
top-level commas, method-chain dots or boolean operators; and the same four-line generated header in
all variants. The byte/character cost is formatting-independent; the line cost is exact under this
recorded expansion.

An earlier layout of this report (a line break after every brace and semicolon, with no intra-line
spacing or wrapping) put the same deletion at 375 lines, 20.3% of readable code. The layout above is
the readable one, and under it the line share (23.4%) tracks the formatting-independent character
share (23.9%) closely, which the earlier layout understated.
