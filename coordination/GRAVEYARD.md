# GRAVEYARD — one paragraph per dead task (created 2026-08-26)

Format: **what it was · what killed it · what we learned · what would reopen it.** A dead task is
closed, not "in progress"; this file is the library the graveyard was missing. Older closures live
in `docs/CONSTRAINTS.md` (the register); from 2026-08-26 every kill lands here first.

- **2026-08-26 — Candidate 0, the champion's replant fallback fix** (`20260826-candidate-0-regeneration-fallback`).
  One-hunk change: when a troll's idle-regeneration plan has no chops, extend the command list
  instead of replacing it. Killed at G-1, reproduced by codex_1: blocking games 118/240 vs 43/240 —
  the surviving 7,500-point regeneration `PICK` beats every job for an empty-handed troll next to
  the shack, the bank clause offers `DROP` next turn, nothing links `PICK` to `PLANT`: a PICK↔DROP
  two-cycle. Learned: the regeneration value is real (+530 own-score points across the panel) but
  only a *plan-keeping* successor can capture it; also, the "−75 on m061" was Candidate 2's cost,
  not the champion's. Reopens only as Candidate 3's plan-keeping case (`PICK` and `PLANT` share
  `Target::Cell(c)`), tested on `m061` at G-2.

- **2026-08-25 — Candidate 1, the resolver hold** (`cure1`). A hold in the resolver against the
  dance; fired 253× on 160 real games, kept every bound, and appeared in **0 of 25** recorded
  dances — real dances are permanent-block dances, not transient ones. Learned: the library's
  idle-blocker fixture shape is 0 of 80 in real games; measure on real games before building.
  Reopens: never in this form; the code is kept.

- **2026-08-25 — Candidate 2, the swap, as a qualified cure** (`cure2`). Panel dances 27→13, 16
  controls pass, but the pre-committed stops fired: the goals stay with the cells, so the two
  trolls swap and swap back (the loop, C-5 = 5), −5/game. Learned: a swap needs goals that travel
  with the troll — that is Candidate 3. Reopens: on top of Candidate 3, only if Candidate 3's
  panel shows an own-score gain (owner bound 08-26).

- **2026-08-26 — Candidate 3, the fixed-margin form** ("keep unless a challenger is clearly
  better by `M`"). Falsified, not mis-tuned: on the six loop games the challenger's advantage
  rises monotonically as the shared tree nears completion (0.02 → 0.27), so no constant `M`
  proves "no second exchange". Learned: a margin cannot bound a quantity that grows with the
  loop's length. Replaced by the absolute-keep form (same task, still alive).
