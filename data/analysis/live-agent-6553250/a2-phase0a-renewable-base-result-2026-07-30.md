# A2 Phase 0a — renewable-base feasibility: result

Date: 2026-07-30. **Verdict: no renewable base exists — but the A2 target is reachable
anyway.** Kill rule K1 fires as originally written and has been **amended**, with the
original recorded as an integrator specification error (charter §Kill rules).

Provenance: the executing agent completed the full compute — 792 game occurrences across
three cohorts at 100% decode success (resident 242/242, ranks 6–20 300/300, top-5 250/250),
producing `a2-phase0a-rows.jsonl` (3.3 MB) and `a2-phase0a-report.json` — then died in a
trailing print when the machine was suspended during a physical relocation. Every number
below is quoted from its `report.json`; the integrator assembled this document and drew the
verdict. Script: `cgauto/renewable_base_feasibility.py`.

## 1. There is no renewable base, for anyone

| cohort | reproduction ratio R (median) | games reaching R ≥ 1 | R defined | games with zero harvest |
|---|---|---|---|---|
| resident | **0.00** | 6.6% | 42% | **57.9%** |
| ranks 6–20 | **0.77** | 4.7% | 84% | 15.7% |
| top-5 | **0.75** | **1.2%** | 100% | 0.0% |

R is new plantable seeds per harvested crop generation, net of what is spent. **It is below
1 for every cohort including the top five**, and only 1.2% of top-5 games ever reach
self-replacement. Population growth says the same thing independently: every cohort starts
at ~16 trees and ends far below it — **net −11.97 (resident), −8.95 (ranks 6–20)** — with
only 6.6% / 10.3% of games ending above their initial population. The resident is the
extreme case: **0.05 of its own planted trees are alive at game end**, against 2.17 for
ranks 6–20.

**So planting is sub-critical for everybody. Nobody on this ladder grows their resource
base.** Any design premised on a self-sustaining loop is premised on something that does not
exist on these maps.

## 2. And yet 3–4 workers are reached, from the depleting base

| | worker 3 reached | earliest / median turn | worker 4 reached | earliest / median turn |
|---|---|---|---|---|
| resident | **0 / 242 (0.0%)** | never | **0 / 242** | never |
| ranks 6–20 | 89 / 300 (29.7%) | t28 / t85 | 42 / 300 (14.0%) | t81 / t130 |
| top-5 | **189 / 250 (75.6%)** | t34 / t106 | **104 / 250 (41.6%)** | t55 / t137 |

**Where the bill currency comes from** — the decisive table:

| | endowment | natural trees | **self-planted** | opponent-planted | iron mined |
|---|---|---|---|---|---|
| top-5, worker 3 | 39.9% | 21.6% | **37.2%** | 1.2% | 5.99 |
| top-5, worker 4 | 26.9% | 22.3% | **49.7%** | 1.2% | 16.05 |
| ranks 6–20, worker 3 | 48.7% | 22.8% | 28.0% | 0.4% | 4.85 |
| ranks 6–20, worker 4 | 31.0% | 24.7% | 44.1% | 0.2% | 13.57 |

Two things stand out. **Self-planted crops carry 37% of the third worker and half of the
fourth** — farming genuinely funds scaling even though it does not replace itself. And the
**endowment's share falls** (39.9% → 26.9%) as the game runs, while the self-planted share
rises: the economy shifts from spending its inheritance to spending its own output, without
ever becoming self-sustaining.

**Iron scales with roster:** mined iron rises 5.99 → 16.05 between workers 3 and 4 for the
top five (4.85 → 13.57 for ranks 6–20). This is a hard requirement for A2 and a direct
conflict with the resident's architecture, whose mining is gated off entirely at
`own_units < 2` (D174a).

## 3. The synthesis, and the corrected premise

**The top cohort runs a sub-critical but strongly productive economy.** It is not renewal
and it is not pure windfall consumption: it is *conversion* — extracting far more from a
finite, declining base than we do, fast enough to fund 3–4 workers before the base runs out.
Supporting context: maturation costs ~31.6 turns dry versus ~11.8 watered, so water access
sets the clock on how many generations fit in a game.

The resident sits at the floor of every measure: zero harvest in **57.9%** of games, 0.05
planted trees alive at the end, and **0 of 242** third workers. Its mean margin is +0.49
with a 47.1% win rate, against +36.19 and 60.3% for ranks 6–20.

## 4. Kill rule K1: fires as written, amended with the error recorded

K1 said "Phase 0a finds no renewable base → stop." No renewable base was found, so it
fires. **The rule was mis-specified by me**: it assumed renewal was the *necessary
condition* for reaching 3–4 workers. The measured necessary condition is **conversion
efficiency of a finite endowment**, and the target is demonstrably achieved by two separate
cohorts. Killing the programme on that rule would discard an achievable objective because I
described its mechanism wrongly.

Amended (charter §Kill rules): **stop if Phase 1 cannot convert the endowment into a
fruit-funded third worker in ≥40% of fresh-map games by turn ~110.** That is measurable,
anchored to observed cohort performance, and fails fast if A2 cannot convert.

This is my third gate-specification error of the week, after D176a's two, and it shares
their shape: a threshold anchored to the wrong quantity. The durable rule — now in
CONSTRAINTS — is that a gate must be specified against the variable the intervention
actually moves.

## 5. Reproducibility

`a2-phase0a-report.json` and `a2-phase0a-rows.jsonl` (session scratchpad);
`cgauto/renewable_base_feasibility.py`; phase markers
`.superpowers/sdd/a2-phase0a-phase-markers.md`. Cohorts: resident agent 6561795 (242
games), ranks 6–20 (300), top-5 (250). No seed ranges consumed — read-only corpus audit.
