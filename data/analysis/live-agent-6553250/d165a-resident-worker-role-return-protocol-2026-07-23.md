# D165a resident-native bounded worker-role return — frozen protocol

Date: 2026-07-23  
Status: frozen before implementation or outcome generation

## Question

D164 finds one current-leader coordination primitive that is both broad and not already tested in
the project's causal grammar: the same worker produces from an own crop, enters suppression of an
opponent-created crop, and later returns to own production. D165 asks the narrow causal question:

> Once the exact resident naturally sends a proven producer into opponent-crop suppression, does
> explicitly returning that same worker to its remembered live production target improve terminal
> value relative to leaving the resident alone?

This is a resident-relative mechanism audit, not a policy search. It does not test permanent
farming, immediate replanting, static opponent-crop targeting, a global policy handoff, resource
reserve tuning, or workforce scaling. It must not train a selector, contact YT or the platform,
open reserved maps, create a candidate or submission, or alter the resident.

## Frozen panel

Use all 64 already-consumed D148/D161 maps, `9,844,136--9,844,199`, both seats, and all eight
frozen `MacroOpponentMode` families: 1,024 paired tasks. Reserved maps
`9,844,200--9,844,215` remain untouched.

Evaluate exactly two policies:

1. `resident`: unchanged exact Yamo/Orchard;
2. `producer_suppressor_return_h016`: exact resident plus the one bounded return episode below.

The complete matrix has 2,048 rows. Run it once with one worker and once with 20 workers and
require byte-identical sorted output. Bulk matrices go under the verified external-backed path
`artifacts/experiments/d165a-resident-worker-role-return`. Compact protocol, lock, analyzer,
aggregate result, and human report remain in the repository.

## Frozen provenance and entry event

Initialize all map-generated crops as `natural`. After each turn, assign every new crop to `own`,
`opponent`, or `joint` from the players' actual same-cell PLANT attempts. Any unclaimed birth is
`ambiguous` and invalidates interpretation.

For each own worker, remember its latest referee-confirmed production target when either:

- its successful PLANT creates an `own` crop at its pre-action cell; or
- its successful HARVEST gains fruit from a crop currently proven `own`.

A treatment is eligible only after that remembered target still contains a live `own` crop and
the same worker naturally executes a successful CHOP against a live `opponent` crop. At entry the
worker must still exist, have positive harvest power and free carrying capacity, and its remembered
target must remain live and own after the suppression turn. Entry is detected only after the
unchanged resident action has passed through the referee.

Each game may arm at most one episode. Failed or ineligible contacts do not arm it, and a completed
or aborted episode never restarts.

## Frozen return controller

The unchanged resident is called on every turn, including every intervention turn, so its internal
state remains warm. The successful suppression action at entry is not changed. Starting on the
next turn, and for at most 16 consecutive action turns:

1. override only the selected worker;
2. if it is not on its remembered production cell, issue deterministic `MOVE id x y` to that
   exact cell;
3. if it is on the cell and the crop has fruit, issue `HARVEST id`;
4. if it is on the cell but the crop is not ripe, issue `MOVE id x y` to its current cell as a
   deterministic hold;
5. preserve every other resident command unchanged and in original order, appending the single
   legal return command after them.

The episode completes only when the selected worker gains fruit by HARVEST from that exact
remembered `own` crop. The very next turn uses the already-warmed resident without rewriting.

Before issuing an override, abort immediately to the unchanged resident commands if the selected
worker is missing, has zero harvest power, has no free capacity, or the target crop is missing or
no longer proven `own`. If completion has not occurred after the referee processes the sixteenth
return action, abort before the next turn. No controller-generated command is allowed after
completion or abort.

The controller never emits TRAIN, PLANT, CHOP, PICK, DROP, MINE, or BUILD, never changes another
worker, never changes the target, never banks cargo to extend the episode, and never starts a
second episode.

## Exact-control and integrity gates

Interpret no value result unless all conditions pass:

1. both runs contain exactly 2,048 unique rows and their sorted TSV bytes are identical;
2. all 1,024 resident rows reproduce the corresponding D161 resident on every shared terminal,
   score, workforce, crop, mechanics, action-hash, and state-hash field;
3. every task terminates with exact reward identity and zero provenance, ambiguous-birth, direct
   command-legality, ownership, horizon, or restart failures;
4. every inactive treatment row is an exact resident terminal/action/state match;
5. every active row matches the resident action-prefix hash and state hash immediately before its
   first override;
6. the resident is called exactly once on every treatment turn, the controller changes only the
   selected worker, emits only MOVE/HARVEST, and makes zero post-completion/post-abort overrides;
7. each episode uses no more than 16 return-action turns and there are zero target changes;
8. terminal, maximum, and successful-TRAIN worker counts match within every pair; and
9. crop ownership accounting remains exact.

A failed integrity item is repaired and the matrix rerun without interpreting value.

## Mechanism-support gate

The exact entry grammar is considered exercised only if:

1. at least 32 of 1,024 treatment tasks activate;
2. activations cover both seats and at least six of eight opponent families;
3. at least 60% of activated episodes complete a referee-confirmed return harvest;
4. every completion uses the same worker and exact remembered target as entry; and
5. at least 90% of controller overrides are legal MOVE, hold, or HARVEST commands, with zero
   failed generated commands.

Insufficient support closes this exact entry/return grammar on the complete consumed panel; it
does not authorize new maps or a looser trigger.

## Frozen causal analysis

Pair treatment and resident by map, seat, and opponent family. Report terminal margin, own score,
opponent score, crop creation, workforce, activation, completion, travel/hold/harvest commands,
abort reasons, catastrophe count, negative-margin mass, strict win/loss/tie counts, paired-delta
quantiles, family effects, seat effects, and map-clustered normal 95% intervals.

Report both:

- the intention-to-treat effect over all 1,024 tasks; and
- the prespecified active-subgroup effect over tasks whose treatment entry is determined before
  any intervention.

No per-task outcome oracle, post-outcome selector, best arm, or horizon comparison is a pass
criterion.

## Resident-relative value and safety gate

D165 passes only if all of the following hold:

1. intention-to-treat mean paired margin is positive and its map-clustered 95% lower bound is
   above zero;
2. active-subgroup mean paired margin is positive and its map-clustered 95% lower bound is above
   zero;
3. mean own-score delta is nonnegative in both the full and active panels;
4. at least six of eight family mean margin deltas are nonnegative, the worst family is at least
   `-4`, and both seat means are nonnegative;
5. strict improvements are at least as numerous as strict regressions in the active panel;
6. candidate catastrophes and negative-margin mass do not exceed resident values;
7. active paired-margin delta p10 is at least `-20` and the worst active delta is at least `-60`;
8. own crop-creation rate falls by no more than two percentage points; and
9. workforce counts remain exactly paired.

A mechanics pass with a value failure closes this exact immediate bounded return. Do not tune the
16-turn horizon, target memory, entry event, or abort conditions on these outcomes. The next
hypothesis must change abstraction—for example, trajectory-valued suppression exit timing—rather
than select a favorable D165 subgroup.

## Infrastructure and decision scope

Run locally because the complete paired matrix is expected to finish in minutes. Verify the
`medium_data` volume and external-backed bulk roots before writing. Record single-worker and
20-worker wall time and CPU utilization. D165 makes zero YT and platform requests. The canonical
YT root remains exactly `//home/delivery_ml/research/tarstars/troll_farm`.

A full pass would open only a separately frozen validation on another already-consumed panel or a
compact implementation review. It does not by itself authorize Arena, candidate generation,
resident replacement, or submission.
