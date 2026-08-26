# 20260826-track-t-top10-field-comparison: Track T — what the strong two-worker bots do that we don't (read-only, corpus)

- Status: **OPEN — CHARTERED 2026-08-26T12:40Z** under the owner's board organisation
  (`coordination/BOARD.md`, row T-1). The owner's direction: *"perform analytics on the top-10
  contestants, which tricks they use in their games."*
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: claude_1 (one read of the
  final table, ack-required) · Arena: nothing.
- **Done means:** a file `codex_1/top10/field-comparison-2026-08-2x.md` on `main` with (1) the
  list of agents compared and how many of their games the corpus holds, (2) one table per
  question below, ours in the same columns, (3) a ranked list of "tricks" — each a one-line
  behaviour with the games it appears in and an *estimated* point value, plainly marked as an
  estimate, (4) a one-paragraph answer to "is a banana farm among what they do?" for Track F.
- **Dead means:** the strong agents' games cannot be identified in the corpus (then say so, with
  the count, and stop) — or the budget runs out.
- **Budget:** 2 calendar days, 0 ladder slots, 0 bot builds. Read-only on `data/processed/games.jsonl`
  (21,496 games, sha256 `a882e527…`; do **not** run `data/scripts/parse.py`).
- Created UTC: 2026-08-26T12:40:00Z · Last updated UTC: 2026-08-26T12:40:00Z

## THE QUESTION (owner's, plain words)

Twenty-five Legend agents run the same two-troll roster as our champion and rank 7–54, while we
sit around rank 36–41 at ≈ 22.9 (`docs/STATE.md` §2, `docs/BACKLOG.md` B3 note). Same shape, up
to ~9 rating points better. **What do they do that we don't?** Not "what is their code" — what do
their trolls *do* in the games, turn by turn, that ours don't.

## The questions, each one table

1. **Who they are.** The agents (ids, ranks, scores at the time of the games) and how many games
   the corpus holds per agent, split into games *against us* and games *we only observed*.
2. **Score composition.** Points from wood vs each fruit type; per game and per turn-bucket
   (turns 1–50 / 51–100 / 101–150 / 150+). Ours beside it.
3. **Training.** When the second troll is trained (turn distribution), on what, and whether a
   third ever is.
4. **Planting.** PLANTs per game by fruit type and by turn bucket; how many of the planted trees
   are later harvested by the planter, by the opponent, or never. **This row is Track F's
   go/no-go input.**
5. **Suppression.** How often and how early they chop trees near the opponent's shack; do they
   chop our planted trees.
6. **Endgame.** What the last 30 turns look like: planting for points, contesting plants,
   pure banking.
7. **Idle and blocked time.** Turns with a troll doing nothing useful, and turns where a troll is
   standing on a cell the teammate wants — the same measures as our P3/P4 gates, so the numbers
   are comparable to ours.

## Gate

- **T-G1 (claude_1, ack-required, one round):** the tables reproduce from the stated script and
  corpus hash; ours are computed with the *same* script on our games; every "trick" names its
  games. A second round is not budgeted — the coordinator then accepts or kills.

## Do not touch

Any bot source; the resident; `data/raw/games/`; the cron; the Arena.
