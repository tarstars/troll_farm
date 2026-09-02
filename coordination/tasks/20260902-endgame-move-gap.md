# Track E — the endgame gap: what our trolls do in the last fifty turns that the top bots' trolls do not

Born 2026-09-02 08:0xZ under the owner's decision of the same morning ("I like this approach. Write
it down and let's do it."). A **read**, not a build. One day.

## The question

Row T-1 (`codex_1/top10/field-comparison-2026-08-26.md`) left one gap unexplained: **our bot issues
about 8 MOVE commands in the endgame where the strong bots issue 32–38.** Our oldest known weakness
is the late game — we lead early and are out-produced late (Legend finding D159; the
"late-throughput ceiling"). If our trolls stand, wait or repeat a low-value action in the last
fifty turns while theirs keep working, that is production left on the table and the cheapest kind
of fix. If instead the gap is an artefact (their trolls carry more and walk more for the same
yield), the read says so and the line closes.

## Roles

- **claude_1** reads and writes the report.
- **codex_1** is not involved (it builds Track P).
- The coordinator reviews (one round) and puts the one-paragraph answer on the board.

## The evidence to use (nothing new is played)

- The per-turn command corpus `data/processed/turns.jsonl.gz` (174 MB; every command of every
  seat in the 24,973-game corpus, built by row T-2) — the top four's games are the seats of
  agents `6479768` (delineate), `6480540` (norxondor_gorgonax), `6479460` (MSz) and Bubaptik's
  (see `local_claude_1/reconstructions/profiles/`).
- The champion of record's own collected ladder games with telemetry:
  `local_claude_1/denial-ablation/games-41202036/` (160 games) and the later collections under
  `local_claude_1/ladder-queue/games-*/` for the orchard bots if a contrast helps.
- The exact per-turn board reconstruction of row R-1 (`local_claude_1/reconstructions/fits/`) for
  positions, carried loads and scores per turn.

## The deliverable — `claude_1/endgame-gap/READ-2026-09-02.md`, one page plus tables

1. **The command mix by phase** (turns 1–100, 101–200, 201–250, 251–300) for our champion and for
   each of the four top bots: MOVE / HARVEST / CHOP / PLANT / TRAIN / WAIT (or no-op) per troll per
   turn, and the number of trolls alive. State whether the 8-vs-32 gap is per game, per troll, or
   per turn, and whether it is a late-game gap or an all-game gap.
2. **What our trolls are doing instead** in turns 251–300: standing still harvesting one cell,
   waiting, walking between two cells, or idle because nothing reachable is left — with three
   example games (id, turn, cell) the owner can open.
3. **The points at stake**: our score gained in turns 251–300 against the opponent's, over the 160
   collected games, split by whether we led at turn 250 — and the same for the top four in their
   games (their own score gain in the last fifty turns).
4. **One candidate rule, or "no rule"**: if production is left on the table, the smallest change
   to the champion that would recover it (in plain words, judged from game state down, never from
   the code up), with the expected size of the effect and how the local panel would read it. If
   the gap is an artefact of carry or map geometry, say so and close the line.

## Done / dead / budget

- **Done when** the report is on `main`, the coordinator's one review round is answered, and the
  board carries the one-paragraph answer (gap real or artefact; the candidate rule or none).
- **Dead when** the per-turn data cannot separate the phases or the command types for the top four
  (the corpus rows lack the fields) — then the report says which field is missing and stops.
- **Budget:** one day of claude_1 (the read), one review round; no build, no ladder, no platform
  action.

## Log

- 2026-09-02 08:0xZ: card born; handoff to claude_1 to follow, ack-required. — coordinator
