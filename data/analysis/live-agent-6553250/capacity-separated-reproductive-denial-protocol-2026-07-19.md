# Capacity-separated reproductive denial — frozen protocol, 2026-07-19

## Hypothesis

The rejected two-worker controller made crop denial mechanically effective but economically
zero-sum: its only chopper abandoned private production, while redundant rival seeds replaced the
destroyed crops. An existing complete renewable architecture with two producer/funders and two
choppers can preserve one private wood loop and spend only the second chopper on denial. Capacity
separation should retain the architecture's large own-score gain while suppressing enough rival
reproduction to clear the adaptive-Gold veto.

## Fixed base policy

Use the existing `GoldElite::adaptive()` policy and an exact same-build shadow. No catalog search
or parameter change is allowed. Its frozen behavior is:

- dense initial forest (at least 12 plants): maximum four workers, one extra cheap producer, two
  `(2,2,0,2)` choppers, native hold/build boundary at turn 100, farm cap 24;
- sparse initial forest: its native lean two-worker policy; and
- all training, funding, planting, harvesting, banking, private targeting, and endgame logic
  remain base commands.

## Fixed denial scheduler

Reuse the exact birth-provenance and first-fruit simulator from the closed pre-fruit experiment.
Before turn 100 or while fewer than two pure choppers exist, emit the exact base policy. Once two
exist:

- the lowest-ID pure chopper is permanently protected from denial and keeps its base command;
- only the highest-ID pure chopper is eligible;
- a carrying denial chopper keeps its base banking/work command;
- an empty denial chopper may replace its own command with MOVE/CHOP only for an attributed
  opponent crop that exact simulation can kill before first fruit and that an opponent harvester
  can reach by the first-fruit tick; and
- preserve a feasible commitment, otherwise order by first-fruit tick, kill tick, then cell.

No worker-count, density, turn, crop, distance, or value threshold may be fitted. Turn 100 and
density 12 are inherited base-policy boundaries, not new treatment parameters. Telemetry records
capacity-ready turns, separation violations, activations, selected targets, disappearance before
fruit, and fruiting failures. Any activation with fewer than two pure choppers or any replacement
of the protected lower-ID chopper is a separation violation and fails integrity.

## Frozen partitions

- Integrity: consumed seeds 0--29, eight opponents, both seats, exact repeated executable.
- Discovery: fresh seeds 2020--2079, eight opponents, both seats.
- Confirmation: seeds 2080--2139, opened only after a complete unchanged discovery pass.

Profiles are exact resident, exact adaptive renewable base, and capacity-separated denial. Each
fresh phase has 960 common scenarios per profile. Seeds 1960--2019 remain sealed for the rejected
two-worker controller and are not reassigned.

## Integrity gates

All must pass:

- complete expected grid and all games complete;
- byte-identical repeated integrity TSV;
- at least 95% assigned chopped-wood provenance for every profile;
- zero base/shadow command mismatches;
- zero capacity-separation violations; and
- every inactive candidate cell exactly equal to the adaptive base on all outcome/provenance
  fields.

## Discovery gates

Candidate minus exact resident across 960 cells:

- mean margin at least +10 and 5% trimmed mean at least +5;
- mean own score at least +50 and own inventory wood at least +10;
- nonnegative mean margin on at least six of eight opponents;
- worst opponent mean margin at least -5; and
- adaptive-Gold mean margin nonnegative.

Mechanism/capacity gates:

- at least 100 activated cells overall and 30 against adaptive Gold;
- at least 30 targets disappear before fruit;
- every activated game has at least one capacity-ready turn and zero separation violations;
- against adaptive Gold, candidate minus adaptive base opponent score at most -50, successful
  plantings at most -10, and opponent self-crop wood at most -20; and
- against adaptive Gold, candidate minus adaptive base own score at least -30.

## Confirmation and stop rule

Confirmation repeats all gates unchanged except the trimmed-mean floor rises to +10. Any discovery
failure closes this exact architecture without changing the inherited hold boundary, density
boundary, worker specs, target order, or timing rule. A two-block pass authorizes packaging and a
fresh official-prefix mechanism audit, not direct submission.

