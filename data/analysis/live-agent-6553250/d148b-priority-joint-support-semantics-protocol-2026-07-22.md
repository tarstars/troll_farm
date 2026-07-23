# D148b priority-joint exact-root semantics repair — frozen protocol

Date: 2026-07-22  
Status: frozen after D148a stopped at exact mechanics, before interpreting D148 transfer or writing
joint targets

## Scope of the repair

D148a's YT operation completed cleanly and every joint-population, selected-replay, candidate-feature,
terminal-parity, accounting, and provenance check passed. Six exact 8-map shards passed outright.
Exact shards 2 and 6 failed only the inherited absolute `at_least_600_roots` gate; neither failed an
actual simulation, accounting, finite-feature, control-parity, root-integrity, paired-return, or
failure-counter gate.

That absolute floor came from D113/D133's 16-map analytical blocks. D148 kept it unchanged while
halving the distributed shard size to eight maps. Treating `600 roots / 16 maps` as `600 roots / 8
maps` silently doubled the required root density and contradicts D148a's stated use of established,
zero-support-aware mechanics.

D148b may repair only that map-count mismatch. It must not change the corpus, schedules, selected
pairs, terminal values, candidate features, exact arms, transfer definitions, or any D148a transfer
gate. The D133b task-support repair remains in force: task support is descriptive structural
availability, not a mechanics failure.

## Frozen repaired mechanics gates

- verify byte hashes for the frozen D148a result, download record, protocol, and all reconstructed
  corpus artifacts before analysis;
- preserve every inherited exact-mechanics gate except the absolute `at_least_600_roots` name;
- replace it with the same historical density, `600 / 16 = 37.5` roots per map: every 8-map exact
  shard must contain at least 300 roots;
- each consecutive pair of 8-map shards (the four D148 transfer blocks) must contain at least 600
  roots;
- the complete 64-map exact corpus must contain at least 4,800 roots and at least 80,000 arms;
- require exactly 1,024 unique baselines, all eight prescribed 8-map blocks, and an exact best of
  control/one-use arms for all 1,024 tasks;
- rerun exact teacher interpretation for all eight blocks and require its aggregate signal and
  safety gates to pass; and
- independently rerun D148 population, manifest/replay, and 443-feature candidate validation and
  require them to reproduce the D148a passing summaries.

If any non-root inherited exact gate fails, or any replacement density/coverage gate fails, stop as
a mechanics failure. There is no further semantic repair authorized by this protocol.

## Frozen transfer decision

Only after every repaired mechanics gate passes, compute the unmodified D148a comparison between
the best sampled executed pair and the exact best of control/one-use arms. Apply exactly D148a's
predeclared aggregate, family, crop, worker, and four-block transfer gates. Write joint targets once
from that interpretation.

If transfer passes, open D149 grouped/cross-fitted two-stage fitting while keeping maps
`9,844,200--9,844,215` sealed. If transfer fails, close the D148 population as nontransferring. D148b
cannot open the validation panel, qualify or submit a candidate, change the resident, or interact
with Arena.
