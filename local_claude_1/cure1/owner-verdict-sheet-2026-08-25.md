# Candidate 1 — verdict sheet for the owner (2026-08-25)

Task `20260825-dance-cure-candidate-1-hold` ("a blocked troll holds instead of stepping
backwards"). Chartered by you this morning ("do it"), built, reviewed and measured on real games
the same day. Plain words; every code explained at first use. Numbers verified against the
published artifacts; `codex_1`'s independent re-run of the final grade is noted at the end.

## The verdict in one paragraph

**The cure is safe and it works as designed — and it is aimed at the wrong dances.** In 160 real
ladder games the hold fired 253 times in 102 games, kept every safety bound (no troll ever waited
more than 2 turns on it, no two trolls ever collided, no parked trolls, idle-with-work 0.44 %
against the 1.5 % line), and cut backward steps by 44 %. But **it fired inside none of the 25
dances the detector recorded**: every one of those was a troll stepping back and forth beside a
teammate that was *not going to move* — the permanent block the rule deliberately leaves alone.
The pre-committed acceptance bars were missed (dances ending in progress 44 % vs 65 %; backward
steps −44 % vs −50 %), so **G-2 fails, the score block (G-3) does not start, and the second
Arena action you authorized is unspent.** The size is in Candidate 2 — what to do about the
teammate that never moves — which is the ruling still on your desk.

## What happened, step by step

| step | outcome |
|---|---|
| G-0 design review (`codex_1`) | REVISION_REQUIRED once: eight definitions fixed; `claude_1` found a real hazard in my pseudo-code (a holding troll's square could be handed to an earlier-processed teammate) and proposed the two-phase fixed-point reservation I then ruled in. |
| G-1 first build | Parity perfect (rule off = champion byte-for-byte on 34 fixtures and 240 panel games); panel dances 27 → 1 — but it broke your absolute unchanged-orchard rule on one map and pushed idle-with-work to 2.28 %. **Rejected.** |
| Gate defect found | The panel's stall gate (P4) is game-level: a poison arm that parked a troll for 194 turns beside a working teammate passed it. Declared blind; the per-troll idle share is now the safety net. Needs its own charter. |
| G-1 revision | Hold only when the block is *transient* (teammate moving, or not on that square last turn); inert on orchard-eligible maps. Every clause green; `codex_1` accepted from a fresh archive. Panel cure small (dances 27 → 25): **98 % of the first build's holds had been against permanent blockers.** |
| G-2 real-game read | 160 games, identity clean (42,070 turns of telemetry decoded, 0 failures, 0 leak). **Fail on both acceptance clauses, no kill rule fired.** |

## The numbers that decide it (real games, 160 each)

| measure | v3 instrument (baseline) | Candidate 1 instrument | bar | result |
|---|---:|---:|---|---|
| backward steps per 1,000 troll-turns | 7.68 | **4.31** | ≤ 3.84 (half) | fail (−43.8 %) |
| dances ending in the dancer's own progress | 52 of 80 (65 %) | **11 of 25 (44 %)** | ≥ 65 % | fail (underpowered: 95 % interval 24–65 %, p = 0.10) |
| dance episodes per 1,000 game turns | 0.79 (34 episodes) | **0.59 (25)** | — | down, not attributed (different days and opponents) |
| holds that fired | — | 253 in 102 games; longest run 2 | b ≤ 2 | held |
| holds inside a recorded dance | — | **0 of 25** | — | the finding |
| idle-with-work per troll | 0.72 % | **0.44 %** | ≤ 1.5 % | pass |
| trolls blocking each other | 0 | **0** | 0 | pass |
| long-stall share of games | champion 1.3 % | **0.0 %** | ≤ champion | pass |
| telemetry | v3 | **v4: 82,789 rows, 0 decode failures; `r=` and positions agree on 95 % of rows, every disagreement explained** | — | instrument proven |

Caveats that travel with every row: dance counts off replays are an upper bound (reconstructed
plant clocks invent dances, equally for both arms); the two reads are different days and opponent
fields with no randomisation; clause (a) rests on 25 episodes.

## What we learned that we did not know this morning

1. **The real-game dance is the permanent-block dance.** Not once in 25 did a dancer face a
   transient block. The transient rule is a correct fix for a case that is common in the code's
   *behaviour* (253 holds) but not in the *dances* — the hold replaces backward steps that never
   reached the 7-turn detector threshold.
2. **The safety machinery is real**: the two-phase reservation, the bounded hold, the idle line,
   the poison arm, v4 telemetry, the pre-committed baseline. All of it is reusable for Candidate 2.
3. **Two gate defects** surfaced and are recorded: the panel's stall gate cannot see one parked
   troll (needs a per-troll predicate), and "P3 clean" on an orchard-eligible map means the whole
   game, so any cure must be scoped off those maps or change orchard play deliberately.

## Your decisions

1. **Candidate 1:** park it (my recommendation — safe, proven, small; keep the code and the
   telemetry for Candidate 2's build), revise it, or retire it.
2. **Candidate 2 — the teammate that never moves:** *swap* it out of the way once (with a no-swap-back
   lock), or *route around* it by pricing a road through a stationary teammate as the way around.
   This is where every measured dance now points. Either needs its own charter and, for its read,
   a new Arena authorization (the unspent second action was the score block for Candidate 1).
3. **The P4 gate defect:** charter the per-troll stall predicate now, or leave it recorded.

## Where everything lives

`claude_1/cure1/` (`agent/claude_1@22d6b2bb`): `g2-grade-2026-08-25.md`, `results/g2-grade.json`,
`g1-revision-report-2026-08-25.md`, `g1-report-2026-08-25.md`, the three arms and their manifest;
`codex_1/reviews/dance-cure-candidate-1-hold-*.md`; `local_claude_1/cure1/g2-read-2026-08-25.md`
(the read ledger) and `g2-games/` (the 160-game package, `050d1ceb…`); the task record
`coordination/tasks/20260825-dance-cure-candidate-1-hold.md`; my rulings `20260825T085500Z`,
`T094200Z`, `T103500Z`.

`codex_1`'s independent execution check of the G-2 grade: **pending at the time of writing**; if it
changes a number above, this sheet is amended and the change named.
