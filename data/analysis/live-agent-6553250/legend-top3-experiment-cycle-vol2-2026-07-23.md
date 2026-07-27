# Legend top-3 experiment cycle — volume 2 (opened 2026-07-23)

Objective, persistent cycle, and completion rule: see volume 1
(`legend-top3-experiment-cycle-2026-07-18.md`, frozen at D166). Live state:
`docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` — check before proposing.

Per-experiment obligations: one entry here (same style as volume 1); a CONSTRAINTS bullet
for anything closed; a STATE.md §4 update. The first session ending with this file over
100 KB freezes it with one appended note and opens volume 3.

<!-- entries below -->

## 2026-07-27: authorized passive refresh + operational cleanup (no experiments)

Passive read (read-only, D61p collector): resident `6561795` rank 43/110 @ 21.97 with 203
listed battles. The score is bit-identical to the 2026-07-23 read and the leaderboard's own
updateTime shows no recomputation since 2026-07-23T02:45:38Z — fresh-agent scores freeze
between rare ladder recomputes, so passive maturity recovery is materially slower than the
fresh-vs-mature analysis assumed. League 107→110. Bar: delineate 31.00 /
norxondor_gorgonax 29.52 / MSz 28.22. 198 new public replays collected (195 cached
skipped; 220/220 requests clean), QA 393/393 parsed with zero failures; snapshot
`data/raw/snapshots/20260727T130712Z-d61p/` (gitignored raw). No arena write.

## 2026-07-27: B3.1 catastrophe-tail endgame coverage audit (read-only; no candidate)

On the fresh snapshot's 192 open resident games (11 sealed-confirmation games excluded per
the D61p holdout protocol), the D159 signature replicates independently: 19/192 = 9.9%
catastrophes (margin ≤ −100) carrying 57.9% of negative-margin mass across 14 opponents;
ahead-at-t100 reversals match D159a's own `catastrophic_reversals` computation 16/16. The
resident's score-aware endgame switch (`endgame = turn>250 || (plants≤4 &&
my_score<opp_score)`) fired in 10/19 catastrophes but always at or after the score
crossover (median +46.5 turns late, minimum gap 0) — an AND-of-behind design structurally
cannot fire earlier, and the four worst catastrophes never triggered it before the trivial
turn-250 clock (never-fired games hold 57.6% of catastrophic mass). Verdict: **no coverage
bug; switch retuning is closed.** The bounded surviving signal: opponent workforce scaling
past the resident's two-worker ceiling precedes the crossover by 42–125 turns in 84% of
catastrophes (79% jointly with ahead-at-t100), covering 83% of catastrophic mass — an
observable trigger the resident never conditions on. This independently confirms D159's
top-ranked attack angle and feeds the B2.1 option-interface design (activation
conditioning), not a retuned switch. Report:
`scratchpad/b31-endgame-audit-report.md` (session scratch; numbers preserved here).

Operational, same day: the data-footprint cleanup executed per
`docs/superpowers/plans/2026-07-24-data-footprint-cleanup.md` with per-task review — 22
clean worktrees removed (branches intact), `rust/target/debug` cleared + AGENTS.md cap
rule, tranche-2 migration of 683 files / 1,042,056,986 bytes verified (count+bytes+SHA-256
+ zero-diff dry run) then symlinked, YT dead D144 first-attempt directory removed under
guards, and a 424,896,968-byte md5-verified mirror of the whole `legacy-data-analysis`
tree uploaded to `//home/delivery_ml/research/tarstars/troll_farm/mirrors/`. Local repo
23.5 → 2.76 GB; Python suite unchanged at its documented baseline (1,163 passed / 3 known
pre-existing failures).
