# E4 secure-orchard mother tie audit

Date: 2026-07-30
Verdict: **`KEEP_LEXICOGRAPHIC`**

## Question

The live secure-orchard initializer chooses the home-door mother with maximum enemy-door
distance, then breaks an exact primary tie by lexicographically smaller cell. Would
choosing the other equal-best mother improve terminal local value?

This audit changes only that secondary comparator in a temporary source. It is not a
generic BFS/pathfinding study, rating predictor, candidate, or Arena result.

## Structural scope

The exact 0..999 reused Bronze census reproduces 57 geometry-eligible seeds in each
symmetric seat (114 side-maps): 94 sides have one best mother and 20 sides—the same ten
seeds in both seats—have exactly two. The exhaustive value panel therefore needs only:

- ten tied seeds × six frozen opponents × control/alternate = 120 paired rows, each with
  both seats;
- 16 unique-best sentinel seeds × `motion` × control/alternate = 32 paired rows.

All 152 keys complete. No fresh, sealed, official, or confirmation map was opened.

## Runtime integrity correction

The first jobs-8 computation correctly stopped before writing a result because all 16
sentinels differed. Repeat-control diagnosis showed that the alternate was not the cause:
the immutable `motion` opponent uses a wall-clock-bounded 550/28 ms RHEA loop and
randomized Rust `HashMap`/`HashSet` seeds.

Lock v2 therefore applies a temporary child-process-only runtime shim: monotonic time
advances in fixed one-ms observations and `getrandom`/`getentropy` return a fixed stream.
No control, alternate, or opponent source byte changes. Eight independent Rust collection
probes then have one order, and four full seed-19 repeat-control cells are exact.

Under lock v2:

- all 16/16 sentinels are exact in policy streams, opponent streams, terminal states, and
  outcomes;
- stderr and malformed-command counts are zero;
- complete jobs-1 and jobs-8 payloads are byte-exact after excluding only `jobs`;
- tied, sentinel, and delta row hashes match independently.

## Mechanism

The comparator is active, not dead code:

- policy streams diverge on all 10/10 tied seeds;
- 51/60 seat-0 cells and 44/60 seat-1 cells diverge;
- all six opponent families contain a divergence.

`ACTIVE_TIE` passes every frozen mechanism gate.

## Value

Reversing the secondary comparator loses **8.55 paired margin on the tied panel**. Since
only ten of the 1,000 census seeds can change, the exact 1,000-map-weighted delta is
**−0.0855 margin**.

Both tied-panel seat means are negative: **−7.667** and **−9.433**. Every family is
negative: motion −2.30, taskplan −6.05, race −0.80, yield −1.60, ringfix3 −26.65, and
chopharvest −13.90.

The alternate also changes tied-panel own score by −10.80 and opponent score by −2.25
(weighted −0.108 and −0.0225). Wood edge moves only +0.133 on tied maps, or +0.00133
weighted, while terminal margin worsens.

## Decision

The mechanism is broad, but its causal sign is wrong in both seats and all six families.
The frozen nonpositive-weighted, negative-seat, and worst-family gates independently return
**`KEEP_LEXICOGRAPHIC`**.

Keep the current comparator. Do not build a persistent alternate, candidate, selector, new
map panel, or Arena cycle from E4.

Machine summary:
`data/analysis/live-agent-6553250/e4-orchard-mother-tie-audit-result-2026-07-30.json`.
Analyzer:
`cgauto/e4_orchard_mother_tie_audit.py`.
