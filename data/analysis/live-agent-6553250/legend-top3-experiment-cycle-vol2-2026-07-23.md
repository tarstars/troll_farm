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

Operational, same day: the data-footprint cleanup executed per
`docs/superpowers/plans/2026-07-24-data-footprint-cleanup.md` with per-task review — 22
clean worktrees removed (branches intact), `rust/target/debug` cleared + AGENTS.md cap
rule, tranche-2 migration of 683 files / 1,042,056,986 bytes verified (count+bytes+SHA-256
+ zero-diff dry run) then symlinked, YT dead D144 first-attempt directory removed under
guards, and a 424,896,968-byte md5-verified mirror of the whole `legacy-data-analysis`
tree uploaded to `//home/delivery_ml/research/tarstars/troll_farm/mirrors/`. Local repo
23.5 → 2.76 GB; Python suite unchanged at its documented baseline (1,163 passed / 3 known
pre-existing failures).
