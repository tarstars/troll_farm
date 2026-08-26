# 20260826-m061-stale-goal-read: Track D-3 — why did a troll on `m061` keep one goal for 171 turns, and what did it cost? (read-only on the Candidate 3 panel archives)

- Status: **OPEN — CHARTERED 2026-08-26T14:30Z by owner ruling ("go")**, board row D-3.
- Record owner: local_claude_1 · Work owner: **claude_1** (it holds the Candidate 3 arms, the
  v6 instrument archives and `narrate6`) · Reviewer: **codex_1** (one round, ack-required) ·
  Arena: nothing.
- **Done means:** a file `claude_1/cure3/m061-stale-goal-read-2026-08-2x.md` on `main` with:
  1. **The turn-by-turn account** of the 171-turn kept goal on `m061`, both seats (`m061:0`,
     `m061:1`): for every turn of that goal's life — what the goal was (`Tree`/`Cell`/`Bank`/
     `Shack` and its cell), whether it was live (`k=`), what the troll actually emitted, where it
     stood, what it carried, and which release predicates were tested and why none fired. Plain
     words beside the wire.
  2. **The mechanism in one sentence** — e.g. "a fruit picked to plant was kept because the
     planter never offered `PLANT` again", or "a tree goal survived because the carry never
     filled" — stated as what the data shows, not what the design expected.
  3. **The cost, attributed:** of the −47 / −43 own-score points on this map, how much is the
     stale goal (turns lost × what the champion's troll banked in the same turns) and how much is
     anything else.
  4. **For each plausible release fix** — (a) a turn cap on a kept goal, (b) release when a
     strictly better goal of the same kind is adjacent / cheaper, (c) release a picked-to-plant
     fruit when planting is no longer offered or possible, (d) any other the data suggests —
     **which turn it would have fired on `m061`**, the points it would plausibly recover there,
     and **its estimated cost on the other 119 maps** (the +25 outside `m061` must survive; count
     how many kept goals elsewhere the fix would have cut and what those goals went on to bank).
  5. **The `ka` distribution** over all 240 games (the packet reported only the maximum): every
     game with a kept goal older than 30 turns, named.
- **Dead means:** the v6 archives do not hold enough per-turn detail to attribute the 171
  turns (then say what *is* attributable and stop). The task does not build, tune or re-run
  anything.
- **Budget:** 1 calendar day, 0 builds, 0 panels, 0 ladder. Read-only on
  `claude_1/cure3/` panel outputs already on the VM.
- Created UTC: 2026-08-26T14:30:00Z · Last updated UTC: 2026-08-26T14:30:00Z

## THE QUESTION (owner's, plain words)

Candidate 3 ("a troll keeps its goal") cures the dance loop and is +25 fruit on 119 of the 120
maps, but on `m061` one troll kept a goal for 171 turns — a third of the game — and that map
alone costs −90, more than the cure saves everywhere else. **Why does this happen, exactly, and
which release rule would have stopped it without undoing the +25?** A fix, if one exists, becomes
a *new* candidate (Candidate 3b, its own card and bound); this task only finds the cause.

## Inputs

Candidate 3 G-1 packet `claude_1/cure3/g1-packet-2026-08-26.md` (on `main`); the instrument
arm's v6 archives (both seats of `m061`, and all 240 games for item 5); the champion's own
`m061` run for the turn-by-turn comparison (same seed, same seats); Candidate 0's post-mortem
(`coordination/tasks/20260826-candidate-0-regeneration-fallback.md` — the PICK↔DROP two-cycle on
this same map) and r4/r6 §7 (plan-keeping: a regeneration `PICK` carries `Target::Cell(own
cell)`).

## Gate

- **D3-G1 (codex_1, ack-required, one round):** the turn table reproduces from the named
  archives; the cost attribution's arithmetic checks; each fix's "would have fired on turn N"
  is verified against the wire, not argued. No second round — the coordinator accepts or kills.

## Do not touch

Any bot source; the arms; the resolver; the Arena; `data/raw/games/`.
