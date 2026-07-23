# Provenance-aware opponent-crop suppression — Phase 17 protocol, 2026-07-18

## Field discriminator

Read-only arena and replay calls were made for the current restored resident, agent `6559583`.
No game was started and no source was submitted. The live snapshot is rank 45/107 in Legend at
22.1, not the earlier rank-20 plateau.

The latest 80 finished battles contain 44 wins, two ties, 22 ordinary losses, and 12 catastrophic
losses with final margin at most -100. Those 12 cells are 15% of the sample but contain 76.315% of
all negative margin. Exact replay attribution gives the causal score component:

| Cohort | Opponent-created crops | Our contact rate | Our crop wood | Opponent crop wood | Opponent crop fruit |
|---|---:|---:|---:|---:|---:|
| Wins | 24.20 | 60.33% | 19.73 | 16.66 | 21.82 |
| Ordinary losses | 31.32 | 30.85% | 12.86 | 39.36 | 33.50 |
| Catastrophic losses | 50.17 | 26.84% | 20.17 | 100.67 | 60.50 |

Catastrophic opponents finish with 80.31 more wood than non-catastrophic opponents; 76.42 of that
gap is wood collected directly from their planted trees. Essentially all opponent crops are
within a 20-turn ETA of a current resident worker when they appear, with catastrophic median ETA
5.13, yet only 12.58 of 50.17 crops are contacted. This is a scheduling/ownership failure, not a
raw reachability failure. ETA ignores displaced work, so it nominates a mechanism but does not
justify a policy by itself.

Machine-readable evidence:
`data/analysis/live-agent-6553250/recent-resident-field-census-2026-07-18.json`.

## Mechanism

The research controller preserves the exact Yamo/secure-orchard policy and records plant cells
between observed turns. A newly appeared tree is classified as ours if our preceding selected
commands attempted `PLANT` on that cell; otherwise it is classified as opponent-created. Cells
are forgotten when the tree disappears. The candidate adds a bounded score bonus only to the
resident's existing tree candidates for tracked opponent crops and only within a configured
current-worker ETA. It does not add a worker, create supply, replace direct work, run rollouts, or
change the default `SecureOrchardBot::new()` behavior.

Default tracking was checked on seeds 1300--1309 against the exact full resident parent: paired
margin, wood, and every command-count delta are zero.

## Frozen discovery matrix

Seeds 1300--1329 are discovery only. Every profile runs both seats against CompactGold, adaptive
GoldElite, GoldElite, MyBot, PrinterBot, Scheduler, ScriptBoss, and SilverBoss. The ten profiles
were fixed before outcomes:

| Profile | Flat target bonus | ETA limit | Earliest turn | Minimum opponent crops seen |
|---|---:|---:|---:|---:|
| `b100_e6` | 100 | 6 | 1 | 1 |
| `b250_e6` | 250 | 6 | 1 | 1 |
| `b500_e6` | 500 | 6 | 1 | 1 |
| `b250_e10` | 250 | 10 | 1 | 1 |
| `b500_e10` | 500 | 10 | 1 | 1 |
| `b1000_e10` | 1000 | 10 | 1 | 1 |
| `b250_e20` | 250 | 20 | 1 | 1 |
| `b500_e20` | 500 | 20 | 1 | 1 |
| `b500_e10_t50_s4` | 500 | 10 | 50 | 4 |
| `b500_e10_t75_s8` | 500 | 10 | 75 | 8 |

A discovery profile qualifies only if all of these hold over 480 paired cells:

- at least 48 cells select an opponent crop;
- mean paired margin delta at least +2;
- 5%-trimmed paired margin delta positive;
- mean own-score delta at least -2;
- mean opponent-score delta at most -4;
- at least six of eight opponent mean margin deltas nonnegative;
- worst opponent mean margin delta at least -5.

If several qualify, choose by worst-opponent mean, trimmed mean, raw margin, own-score preservation,
then lower bonus and ETA. The exact chosen profile, with no threshold changes, must pass the same
gates on discovery-disjoint seeds 1330--1359. If none qualifies or replication fails, close this
priority architecture. Do not inspect seeds 402--999 or the sealed official-map holdout.

## Discovery result

The 20-thread runner completed 480 seed-seat-opponent scenarios for every profile (4,800 profile
cells). It sustained approximately 1,982% CPU while active. Results were evaluated only after the
matrix and evaluator tests were complete:

| Profile | Active | Mean margin | Trimmed margin | Own score | Opponent score | Nonnegative opponents | Worst opponent | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `b100_e6` | 383 | +5.150 | +4.641 | +0.744 | -4.406 | 6/8 | -4.900 | pass |
| `b250_e6` | 398 | +7.694 | +6.847 | -2.948 | -10.642 | 5/8 | -11.017 | fail |
| `b500_e6` | 400 | +7.312 | +6.514 | -4.198 | -11.510 | 5/8 | -11.333 | fail |
| `b250_e10` | 405 | +9.898 | +8.294 | -4.929 | -14.827 | 6/8 | -11.033 | fail |
| `b500_e10` | 406 | +9.342 | +7.530 | -7.294 | -16.635 | 5/8 | -15.500 | fail |
| `b1000_e10` | 406 | +8.533 | +7.007 | -7.388 | -15.921 | 4/8 | -17.650 | fail |
| `b250_e20` | 401 | +9.035 | +7.097 | -5.640 | -14.675 | 4/8 | -10.583 | fail |
| `b500_e20` | 401 | +8.798 | +6.625 | -8.233 | -17.031 | 4/8 | -12.950 | fail |
| `b500_e10_t50_s4` | 306 | +6.588 | +4.125 | -4.356 | -10.944 | 5/8 | -3.550 | fail |
| `b500_e10_t75_s8` | 244 | +2.271 | +2.694 | -1.881 | -4.152 | 4/8 | -5.633 | fail |

Only `b100_e6` clears every gate. Stronger and broader bonuses often suppress more opponent score,
but they displace too much resident production and become opponent-fragile. This monotone cost is
useful evidence that the winning treatment is a bounded scheduling nudge, not a general instruction
to chase enemy trees.

Machine-readable discovery evidence:
`yamo-opponent-crop-priority-discovery-1300-1329.tsv` and
`yamo-opponent-crop-priority-discovery-1300-1329.json` in this report directory.

## Unchanged replication and combined audit

The exact `b100_e6` profile then ran on the predeclared seeds 1330--1359. No source, parameter,
opponent, threshold, or evaluator changed:

| Block | Cells | Active | Mean margin | Trimmed margin | Own score | Opponent score | Nonnegative opponents | Worst opponent | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Discovery | 480 | 383 | +5.150 | +4.641 | +0.744 | -4.406 | 6/8 | -4.900 | pass |
| Replication | 480 | 369 | +4.571 | +4.201 | -1.706 | -6.277 | 7/8 | -0.217 | pass |
| Combined audit | 960 | 752 | +4.860 | +4.411 | -0.481 | -5.342 | 7/8 | -2.092 | pass |

The combined effect is positive from both seats (+3.502 from seat zero and +6.219 from seat one).
It is principally denial: opponent score falls 5.342 while resident score falls only 0.481. The
median cell is unchanged, but the treatment changes behavior in 78.33% of cells and gains +6.205
margin conditional on a command divergence.

The catastrophic-tail check below is descriptive and was not used for profile selection. Across
the combined 960 cells, margins at most -100 fall from 132 under control to 103 under the profile;
32 control catastrophes are rescued and three new ones are introduced. Mean margin change on the
132 control-catastrophic cells is +22.561, worst-decile absolute margin improves from -183.813 to
-173.344, and total negative-margin mass falls from 25,486 to 22,066. One individual candidate
cell is still worse than the control minimum (-274 versus -254 overall), so the profile reduces
tail frequency and mass rather than eliminating tail risk.

Machine-readable replication evidence:
`yamo-opponent-crop-priority-replication-1330-1359.tsv` and
`yamo-opponent-crop-priority-replication-1330-1359.json` in this report directory.

## Verdict

The provenance-aware `b100_e6` mechanism is the first post-plateau controller change in this
sequence to pass both a prospectively frozen discovery block and an unchanged fresh replication.
The result validates a local research mechanism, not arena transfer. The only justified next
implementation is the exact 100-point bonus for tracked opponent-created crops within ETA six.
Do not tune another bonus, ETA, start turn, or crop-count threshold. Candidate construction,
standalone size/latency validation, and any arena protocol belong to a separate phase.

## Authorization boundary

This phase authorizes research source, local generated-map evaluation, telemetry, and reports.
It does not authorize a deployable candidate, controlled platform games, arena submission, or a
change to `cgauto/api_submit.py`. The resident artifact remains the 62,725-byte file with SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
