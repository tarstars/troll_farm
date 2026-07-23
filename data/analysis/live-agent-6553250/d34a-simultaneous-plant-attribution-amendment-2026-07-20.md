# D34a simultaneous-plant attribution amendment (2026-07-20)

## Trigger

The D34 development runner completed the preregistered 8,640-row grid.  The analyzer stopped at
integrity validation before computing or exposing any controller outcome summaries because it
treated every `ambiguous_plants` count as an integrity failure.  The only observed diagnostic was
273 simultaneous same-cell planting contests; row count, scenario count, controller sets, map
identity, dimensions, and turn ranges were all exact.

## Protocol-consistent correction

The original protocol explicitly says that successful plants are attributed only to exclusive
pre-step claims and that **simultaneous claims are reported separately**.  A simultaneous claim is
therefore an intentionally unassigned category, not an attribution failure.  It would be a failure
to credit it to both players or silently force it to one player.

Before any policy metric is analyzed:

1. retain the exact runner and the exact 8,640 game rows;
2. retain `ambiguous_plants` as a reported diagnostic;
3. remove only `ambiguous_plants == 0` from grid completeness;
4. keep exclusive successful-plant counts separate from ambiguous contests; and
5. leave every promotion gate based on score, margin, wood, workforce, opponent breadth, rich
   opponents, catastrophe frequency, and negative mass unchanged.

No game is rerun, no seed is added or removed, no controller output is inspected to make this
correction, and confirmation seeds 9,100,060--9,100,119 remain sealed.

