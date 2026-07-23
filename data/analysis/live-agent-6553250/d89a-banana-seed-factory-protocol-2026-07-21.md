# D89a banana seed-factory — frozen prospective protocol (2026-07-21)

## Intervention

Implement the accompanying D89a blueprint as a research constructor on
`SecureOrchardBot`. `SecureOrchardBot::new()` remains the exact control and the new behavior is
disabled by default. Preserve opening and training commands until the second worker is observed.
The candidate then applies the frozen starter farm and trained wood/logistics roles; no map,
opponent, score, turn, tree-count, supply, species, or outcome selector may be added.

Use all initial banked BANANAs as the bootstrap goal. Prefer a water-adjacent reserve cell, then
minimum home-door distance, maximum opponent-door distance, and lexicographic cell. Other planting
cells use minimum farmer distance, minimum home-door distance, maximum opponent-door distance, and
lexicographic cell. Protect exactly one live reserve crop. Harvest tracked owned BANANA crops only,
preferring the reserve, then bank-sourced crops, then conversion crops by travel and cell order.

The trained worker keeps the resident-selected command when it is CHOP, DROP, MOVE, or WAIT and
does not target the reserve. Otherwise replace it with the highest-scoring existing resident
chop/bank candidate under unchanged scores and deterministic ties.

## Telemetry and parity

Run a resident shadow on each candidate state. Record activation/first activation turn, initial
BANANA budget, bootstrap attempts/successes, reserve cell/promotions/losses, tracked live crops,
own-crop harvest selections/successes, renewable PLANT attempts/successes, role rewrites,
preactivation command mismatches, worker counts, full action/state hashes, provenance, scores,
wood, plants, crop harvests, catastrophes, and terminal reason.

Require focused source tests for default parity, exact activation boundary, initial-budget
accounting, successful/failed plant reconciliation, reserve exclusion/promotion, harvest-to-plant
state persistence, and trained-role filtering.

## Prospective panel

Use unopened official maps `9,914,032--9,914,047`, both seats, and the unchanged eight
complete-economy opponents. This yields 256 resident/candidate pairs and 512 rows per repeat. Run
once with one worker and once with 20 workers, sort by `(seed, seat, opponent, profile)`, and require
byte identity.

Maps `9,914,048--9,914,063` are sealed confirmation. D87 confirmation maps
`9,914,016--9,914,031` remain sealed and may not be borrowed.

## Frozen integrity and activation gates

All must pass:

1. complete exact repeats, valid commands, complete/stalled games, exact resident repeat parity,
   and at least 95% fruit/wood provenance;
2. zero candidate/shadow mismatch before the first observed two-worker activation;
3. all inactive pairs exact in action hash, canonical state hash, and terminal result;
4. paired worker counts always equal and candidate training commands match the shadow through
   activation;
5. at least 160/256 tasks activate, both seats and all eight opponents activate;
6. at least 75% of active tasks successfully bootstrap at least three BANANAs; and
7. at least 64 active tasks successfully harvest a tracked own crop and subsequently replant its
   BANANA, with zero trained-worker successful HARVEST or PLANT.

Integrity permits only a mechanical repair. Activation failure closes this exact controller; do
not lower the batch, broaden species, or add a map selector.

## Frozen value and safety gates

On all 256 discovery pairs require all:

1. overall mean margin delta >= +1.0 and map-cluster 95% lower bound >= 0;
2. active mean margin delta >= +4.0 and own-score delta >= +2.0;
3. more active improvements than regressions and active regression rate <=40%;
4. at least six of eight opponent-family means nonnegative and worst family >= -5;
5. active p10 >= -20 and active worst >= -60;
6. catastrophes do not increase and negative-margin mass ratio <=1.0;
7. active own wood and own-crop harvested fruit are both positive versus resident; and
8. candidate opponent score does not rise by more than one per active task on average.

Report bootstrap-only tasks separately from sustained renewable tasks. If every discovery gate
passes, open sealed confirmation under the same gates except active mean margin >= +3 and own score
>= +1. Passing confirmation permits source-size/runtime qualification only. Any value or safety
failure rejects the exact controller without tuning consumed maps.

No gate authorizes TestSession, submission, resident replacement, or Arena writes.
