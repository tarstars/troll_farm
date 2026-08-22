# E7 `typeToCut` per-map audit

Date: 2026-07-31

Verdict: **`HINDSIGHT_RESIDUAL_ONLY`**

## Question

The resident chooses LEMON or PLUM once from initial geometry and uses that species all
game for its denial bonus. Is always choosing the other species better, and how much
terminal value could a perfect per-map choice recover?

## Method and integrity

Control is the exact 62,725-byte live source. The temporary alternate changes only the
unique `type_to_cut` initialization and maps LEMON to PLUM or PLUM to LEMON. It changes no
weight, candidate, scheduler, persistent source, or resident.

The frozen panel uses generated Bronze seeds 0..59, all six immutable local opponents,
both policies, and both seats: 360 seed/opponent cells and 1,440 games. Independent
geometry reproduces LEMON on 35 seeds and PLUM on 25; all 60 symmetric seats agree.

All cells complete. Every first divergence has an exact common prefix and the opponent is
unchanged on that state. The median first divergence is turn 12 (range 1–33). Jobs 1 and 8
have byte-identical normalized payloads and identical value, geometry, divergence, and
oracle row hashes. There is no malformed command or unexpected stderr, and the sacred
resident remains `fff6669b…`.

## Mechanism

The flip changes policy actions in 360/360 cells and in all 720 seat-games. Both seats and
all six families are active, so `ACTIVE_FOCUS` passes every frozen mechanism gate.

## Direct value

Always choosing the other species is strongly harmful: paired margin changes **−12.1736**.
Both seats lose (−7.400 / −16.947), and every family is negative: motion −8.375,
taskplan −8.208, race −11.333, yield −5.950, ringfix3 −18.650, and chopharvest −20.525.

The loss is mainly defensive: own score changes −1.014 while opponent score rises +11.160;
wood edge changes −3.025. Cell effects are heterogeneous (144 positive, 7 zero, 209
negative), but the blanket flip fails magnitude, both-seat, family-breadth, and worst-family
gates. It must not replace the current rule.

## Hindsight ceiling

The frozen oracle averages all six opponent deltas for each seed, then chooses CONTROL or
FLIP once for that seed. It prefers FLIP on 24/60 seeds and gains **+10.5097** seed-balanced
margin. Selected-policy seat gains are +10.886 and +10.133.

The residual is not driven by choosing separately for each opponent: when each family is
held out of selection, its evaluation gain remains positive, from +5.450 to +15.450. All
six leave-one-family-out checks pass. This establishes a large, opponent-family-stable
hindsight residual in the binary decision; it does not establish a prospective map
selector or field-rating gain.

## Decision

Keep the current `typeToCut` default and do not persist the blanket flip. The simple
distance rule is not per-map optimal on this reused local panel, so the residual merits
peer review and a separately frozen prospective-selector decision. Hindsight labels may
not be turned directly into a selector, candidate, source edit, or Arena cycle.

Machine summary:
`data/analysis/live-agent-6553250/e7-type-to-cut-audit-result-2026-07-31.json`.
Analyzer: `cgauto/e7_type_to_cut_audit.py`.
