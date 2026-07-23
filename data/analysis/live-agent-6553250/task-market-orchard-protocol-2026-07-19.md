# Task-market orchard scheduling — frozen protocol, 2026-07-19

## Question and causal hypothesis

Can the resident retain its proven private APPLE mother while avoiding the catastrophic opportunity
cost of permanently reserving the starter?

The hypothesis is that secure-orchard setup is valuable, but post-repayment harvest is an ordinary
terminal-value task. After the first mother apple has been banked and replaced the planted seed,
the starter should return to Yamo's unchanged candidate set. A ripe-mother harvest competes inside
the same joint assignment instead of being forced by the outer wrapper.

This is the global-task-market architecture explicitly left eligible by the independent orchard
replication. It is not the closed universal release controller: the mother stays protected and its
ripe fruit remains a continuing candidate.

## Frozen intervention

The exact resident remains byte-for-byte represented by `SecureOrchardBot::new()`. The research
constructor changes behavior only after successful seed repayment:

1. use the exact resident geometry, activation, PICK, PLANT, growth waiting, first HARVEST, and first
   APPLE DROP sequence;
2. mark repayment when the active starter issues that first DROP while carrying APPLE on the mother
   door; market scheduling begins on the following observed state;
3. keep the APPLE mother protected from normal targeting and from other-worker transit;
4. stop `external_idle_unit` reservation after repayment and restore the starter's unchanged inner
   candidates;
5. if the mother is alive and ripe, the starter is empty with harvest capacity, a banked trip fits
   before turn 300, and a path exists, add exactly one mother task to its candidate set;
6. the task harvests `min(fruits, harvest_power, free_capacity)` apples and is scored
   `250 * bankable_apples / (travel + HARVEST + DROP turns)`; and
7. let the existing joint target/stock compatibility selector and movement-conflict resolver choose
   it. A selected apple is banked by the unchanged carried-fruit policy.

The factor 250 is dimensional conversion, not a fitted coefficient: existing chop candidates use
`1000 * wood / turns`, terminal wood is worth four points, and terminal APPLE is worth one. There is
no turn, score, opponent identity, crop count, fruit count, or harvest-history threshold. Do not
catalog alternative multipliers after seeing outcomes.

## Controls, telemetry, and integrity

Compare the exact resident with only the task-market candidate on paired common maps. A candidate
instance also runs an exact-resident shadow without affecting the game.

Record activation and repayment turns, market-active turns, offered and selected mother tasks,
selected HARVEST actions, forced setup actions, pre-market shadow mismatches, scores, wood, workers,
plant/fruit/wood provenance, terminal plants, and terminal turn.

Require:

- complete paired grids and complete games;
- byte-identical 20-worker repeat;
- exact resident outcomes unchanged against the prior lineage/species reference where grids overlap;
- zero candidate/shadow command mismatches before the first market-active turn;
- zero market turns or offers before repayment and zero forced starter overrides after repayment;
- every offer on a live ripe APPLE mother with an empty capable starter and a bankable terminal trip;
- every selected mother task previously offered on that turn;
- exact resident outcomes for every candidate cell without repayment; and
- at least 95% assigned wood and fruit provenance.

An integrity or representation failure repairs the implementation; it does not reject the
hypothesis.

## Consumed mechanism screen

Use seeds 0--99, both seats, all eight fixed opponents, with 20 workers and an exact repeat. This is
1,600 paired cells per profile. Fresh seeds remain closed unless all integrity checks pass and:

- at least 20 cells reach seed repayment;
- at least 50 ripe-mother offers and 10 selections occur;
- active-cell mean margin delta is at least -5.0;
- active-cell 10% trimmed mean margin delta is at least -2.0;
- active-cell mean own-score delta is at least -5.0; and
- the mean of the worst 5% active margin deltas is at least -30.0.

These are gross-safety and activation gates. They cannot qualify the candidate.

## Fresh discovery

If the mechanism screen passes, use untouched seeds 2380--2439, both seats, all eight fixed
opponents: 960 paired cells. Confirmation seeds 2440--2499 stay sealed.

Discovery passes only if candidate minus resident has:

- overall mean margin at least +0.5;
- overall 10% trimmed mean margin nonnegative;
- active-cell mean margin at least +8.0 and mean own score at least +5.0;
- more improved than regressed active cells;
- at least three positive opponent-family means and no family below -3.0;
- nonnegative adaptive-Gold family mean; and
- active worst case at least -25 and active tenth percentile at least -10.

Report activation breadth, offer-to-selection rate, first-repayment cohorts, own/opponent score
decomposition, worker/wood changes, opponent heterogeneity, and complete active delta distribution.

## Confirmation and transfer

Confirmation uses seeds 2440--2499 unchanged. It must retain overall mean margin at least +0.5,
nonnegative 10% trimmed mean, active mean margin at least +5, active own score at least +3, more
active improvements than regressions, three positive families, worst family at least -3,
nonnegative adaptive-Gold mean, active worst case at least -25, and active tenth percentile at
least -10.

Passing confirmation authorizes source-size, exact-resident parity, runtime, and arena-transfer
audits only. It does not authorize submission or any mutation of submission `41012883` / agent
`6560353`. Failure closes this single terminal-value-rate task formulation without multiplier,
turn, opponent, or score-threshold tuning.

