# Three-troll optimized start: executed result

**Verdict: `DEAD_AS_BOT`**

## Provenance

The result was produced during an identity collision under the path
`chatgpt_1/three-troll-optimized-start/`. The owner identified the producing session as
`chatgpt_2`. The complete historical artifact is pinned at rescue commit
`8da821a28db9658062bfb772e2e63b6f47f4868d` and is republished under
`chatgpt_2/three-troll-optimized-start/`. Generated sources, sidecars, logs and raw JSON are retained
byte for byte; only this explanatory result page and the README add the corrected namespace and
later interpretation.

## What was compared

The candidate and control share the same turn-2-second-troll opening. Only the candidate enables the
wood-aware third-troll optimizer. The historical paired comparison was intended to measure that
optimizer rather than the shared early-second-troll change.

The control subsequently proved mechanics-invalid on the same smoke bar: 15/24, versus the
candidate's 19/24 and the required 24/24. Therefore the comparison is useful diagnostic evidence,
not a clean deployable-control experiment.

## Validity and runtime

- candidate fixture bed: PASS; control: PASS
- candidate smoke mechanics: 19/24; control: 15/24
- candidate stalled maps: 5; control stalled maps: 9
- source size: candidate 90,070 UTF-16 units; control 90,071; limit 100,000
- timing: first-turn max 2.397 ms; warm p99 1.045 ms
- panel execution faults zero: True

## Third troll

- trained in 14/24 candidate smoke games
- trained by turn 110 in all 14 of those games
- p25 / median / p75 turn: 10 / 30 / 56
- selected tuples: `1 1 0 1` ten times; `1 2 0 1` four times
- fallback or no admitted/completed third-troll plan: 10 games

## Candidate minus control on identical maps and opponents

- paired margin difference: +2.39 [0.6575, 4.175]
- historical paired win difference: +0.0500 [+0.0050, +0.0950]
- direct duel: 51 candidate wins, 57 ties and 92 losses in 200 games
- direct-duel score-margin difference: -0.97 [-1.81, -0.24]
- external-panel win-difference by opponent: -0.015 versus champion; +0.115 versus orchard 6

## Later selector ruling

A later instrument audit retired paired win-rate difference as a kill criterion. Draw rates varied
from 0.8% to 43.5% across matchups, so a win-only indicator discarded too much information and could
confidently mis-rank bots. The current selector is paired score-margin difference with its 95%
interval. Consequently, the historical `+0.0500` win-difference result carries no independent
promotion weight.

Neither metric overrides the pre-registered mechanics death: both candidate and control missed the
24/24 smoke requirement. Any revival must first remove the funding stalls and establish a
mechanics-valid control, then rerun a margin-based paired panel.

## Boundary

The optimizer is a deterministic contested-resource assignment model and live policy gate. Its
value estimate is not a proof of turn-300 game value. No ladder or platform action was taken.
