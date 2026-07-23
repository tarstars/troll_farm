# Opponent-crop candidate — Phase 19 official-replay activation protocol, 2026-07-18

## Question

Phase 17 established a replicated local outcome effect and Phase 18 proved that the 64,522-byte
standalone artifact exactly implements it. Before any controlled platform game, test whether the
candidate actually activates its intended mechanism on official arena states.

This is an open-loop activation audit, not a counterfactual outcome replay. Once candidate and
resident commands diverge, later official states still belong to the historical resident
trajectory and cannot estimate candidate score. Only the first admissible divergence is causal
selection evidence.

## Frozen corpus and method

Use exactly the 80 game IDs already frozen in
`recent-resident-field-census-2026-07-18.json`; all were played by restored slim resident agent
`6559583`. Fetch those results again through the read-only game-result endpoint. Do not list newer
battles, start a game, or submit source.

For each replay:

1. decode exact official pre-command states with the existing conformance decoder;
2. feed the complete state stream separately to the exact resident and fixed crop candidate;
3. verify resident actions against the recorded actions and identify its first reproduction
   mismatch, if any;
4. retain a candidate first divergence only when the resident reproduces every earlier official
   command;
5. map each changed candidate unit command to its target and require that target to be an active,
   referee-attributed opponent-created crop at that turn;
6. stop causal interpretation at that first divergence.

## Frozen discriminator

The read-only transfer mechanism passes only if all hold:

- all 80 fixed games fetch and decode, with no stderr;
- at least 60 games reproduce the resident for the full official stream;
- at least 30 games have an admissible candidate divergence;
- at least 8 of the 12 previously identified catastrophic losses activate;
- activated catastrophic losses cover at least three distinct opponents;
- 100% of admissible first divergences target an active attributed opponent crop;
- no divergence is counted after an earlier resident reproduction mismatch.

Cohort activation rates, first-divergence turns, crop counts, and opponent crop wood are descriptive;
they are not thresholds and cannot retune the candidate. Passing permits drafting a separate small
controlled-transfer protocol. It does not authorize a game, submission, holdout inspection, or
change to `cgauto/api_submit.py`.

## Execution result

All 80 fixed game results fetched and decoded with zero unknown updates, production stderr, or
probe stdout changes. The candidate has 64 admissible first divergences (80% of games), all 64
select an active referee-attributed opponent crop at current ETA at most six, and median first
divergence is turn 30.5. It activates 10/12 catastrophic losses across seven distinct opponents.

The frozen gate nevertheless **fails** because only 43/80 resident streams reproduce to game end,
below the predeclared 60. Every other check passes. The exact current platform source was then
read through `TestSession/startTestSession` and is byte-identical to the expected 62,725-byte
resident, ruling out source drift. The 37 first resident mismatches have median turn 82 and are
consistent with replay state/input-order reconstruction limits; the repository-wide one-turn
conformance corpus likewise reports only movement-position drift and no material transition
mismatch.

This does not retroactively change the gate. Descriptively, all 64 accepted candidate activations
remain on resident-reproduced official streams for at least 11 further turns (median 191.5), and
38 occur in the 43 fully exact games. The activation evidence is strong, but Phase 19 does not
authorize a controlled game.

Machine-readable result:
`data/analysis/live-agent-6553250/opponent-crop-field-activation-2026-07-18.json`.

## Verdict

Phase 19 is a formal fail on full-stream reconstruction only. Do not relax or relabel it. A
methodological correction may be tested only on an untouched official-game block: require exact
resident reproduction through the candidate's first divergence—the causal selection point—and
continued exactness for a fixed post-divergence interval. Full-game exactness remains descriptive.
