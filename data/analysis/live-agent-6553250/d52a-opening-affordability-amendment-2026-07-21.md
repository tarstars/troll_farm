# D52a opening-affordability amendment — frozen before execution (2026-07-21)

## Outcome-blind finding

Before any D52 trajectory was executed, the frozen current-substrate V2 parent catalog was checked
only for first-turn TRAIN presence. The initial inventory does not afford the configured worker on
every map:

- `legend_v2_hp2_cheap_farm` emits `(2,2,2,1)` on 46/160 maps; and
- `legend_v2_balanced_cheap_farm` emits `(2,2,1,1)` on 71/160 maps.

The other 114 and 89 parent rows respectively defer training. Therefore protocol gate 2, as
worded—"every first command contains the config's exact frozen TRAIN spec"—is impossible under the
frozen maps and conflicts with the scheduler's exact affordability rule. This was discovered from
the pre-existing D50 parent file, before compiling or running the D52 matrix. No D52 result was
available.

## Replacement for gate 2

For every `(game_id, V3 config)` cell, compare first-turn TRAIN presence and spec with the matching
current-substrate farm parent:

- hp2 configs use `legend_v2_hp2_cheap_farm`;
- balanced configs use `legend_v2_balanced_cheap_farm`;
- parent and V3 must either both defer TRAIN or both emit it; and
- every emitted V3 TRAIN must equal the config's frozen first spec exactly.

Consequently the exact expected totals are 46 immediate TRAIN rows for each hp2 config, 71 for each
balanced config, and 468/1,280 across the eight-policy matrix. Starter-unit commands need not match
because role allocation is the treatment.

All other protocol mechanics, thresholds, files, maps, repeated-run requirements, decision rules,
and prohibitions remain unchanged. The parent catalog is pinned at SHA-256
`2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.
