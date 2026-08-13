# Apple orchard cost in readable lines

## Answer

Under one deterministic readable expansion, physically removing the apple-orchard feature removes
**375 code lines**. The exact live E7a source expands to 1,850 physical lines (1,845 code lines),
while the same-parent orchard-stripped source expands to 1,475 physical lines (1,470 code lines).
That is 20.3% of the readable code under this layout. The canonical minified result remains
15,013 characters, or 23.9% of the live submission.

| Same-parent form | Physical lines | Code lines | Compact characters |
|---|---:|---:|---:|
| Exact E7a with orchard | 1,850 | 1,845 | 62,820 |
| Orchard activation disabled, code retained | 1,844 | 1,839 | 62,581 |
| Orchard physically stripped | 1,475 | 1,470 | 47,807 |

Disabling the activation branch accounts for six readable lines. Removing the implementation that
then becomes unreachable removes another 369 lines.

## What was physically removed

| Orchard-exclusive group | Canonical readable lines |
|---|---:|
| Phase, geometry, timing, and wrapper-state types | 12 |
| Site selection, activation economics, planting, camping, protection, and maintenance helpers | 242 |
| Per-turn orchard driver implementing the `Bot` interface | 108 |
| Worker/tree reservation channel, import, and `main` wiring | 13 |
| **Total** | **375** |

Generic apple parsing, harvesting, chopping, carrying, banking, and denial remain because the base
policy uses them independently of the protected orchard.

## Why this does not use the old 6,024-line file

`rust/src/bin/yamo_orchard_live.rs` is protected and was not changed. More importantly, it is not
the readable parent of the deployed 62,820-character lineage: it is 275,377 bytes and contains
substantially more code. Comparing line deletions there would not match the already measured live
feature.

Instead, the builder adds only comments and whitespace to each exact compact same-parent source.
Compacting every readable copy reproduces its known parent hash exactly after restoring the
lineage's trailing newline. This makes the 375-line number reproducible rather than an estimate.

## Verification

- all three readable sources compile optimized and handle empty input cleanly;
- all three exact compact parents pass 10/10 semantic fixtures;
- readable exact E7a matches 25/25 packet games and 7,234/7,234 commands;
- activation-disabled differs only in known orchard game `897833045`, turn 79;
- readable stripped matches readable activation-disabled in 25/25 games and 7,234/7,234 commands;
- the protected source remains SHA-256 `fff6669b...`;
- no Arena or TestSession action occurred.

Readable LOC depends on formatting, so the report states the layout explicitly: a new line after
every brace or semicolon, four-space brace indentation, and the same four-line generated header in
all variants. The byte/character cost is formatting-independent; the line cost is exact under this
recorded expansion.
