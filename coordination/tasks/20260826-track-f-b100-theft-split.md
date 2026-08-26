# 20260826-track-f-b100-theft-split: Track F, read 1 — who ate the b100 banana farm? (read-only, corpus)

- Status: **OPEN — CHARTERED 2026-08-26T12:40Z** under the owner's board organisation
  (`coordination/BOARD.md`, row F-1). Sequenced **after T-1's game-identification step** (same
  code) and before any farm design.
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: claude_1 (one read,
  ack-required) · Arena: nothing.
- **Done means:** a file `codex_1/farm/b100-theft-split-2026-08-2x.md` on `main` with, for every
  game the b100 bot (agent `6590083`, submission `41081195`, Aug 2) played on the ladder: bananas
  we planted; bananas harvested from *our* trees by us / by the opponent / never; bananas the
  opponent banked from *their own* trees; the game's final scores. Then the split the CBF spec
  marks UNRESOLVED (`docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md` §2):
  **of the opponent's extra score, how much was theft from our farm and how much their own
  crop?** — and one paragraph: would the CBF abort sensor (opponent banks more bananas than us
  for 5 turns after turn 30) have fired in these games, and when.
- **Dead means:** the b100 games are not in the corpus with enough per-turn detail to attribute
  harvests (then say so, with what *is* attributable, and stop).
- **Budget:** 1 calendar day, 0 ladder slots, 0 builds. Read-only on `data/processed/games.jsonl`
  and the b100 analysis directory `data/analysis/live-agent-6553250/` if it holds those replays.
- Created UTC: 2026-08-26T12:40:00Z · Last updated UTC: 2026-08-26T12:40:00Z

## THE QUESTION (owner's, plain words)

The one time a banana farm went on the real ladder it scored 12.99 (rank 127/131) against the
parent's 23.3. The local test bench had said +79. The bench also showed the *opponent* gaining
+83 — and nobody measured whether they gained it by eating our bananas or by growing their own.
That single number decides whether a farm can be *defended* (a conditional farm with an abort is
worth building) or only *feeds the other side* (it is not).

## Gate

- **F-G1 (claude_1, ack-required, one round):** the per-game table reproduces from the stated
  script; the attribution rule (which troll harvested which tree) is stated and spot-checked on
  three games by hand. No second round.

## Do not touch

Any bot source; the resident; `data/raw/games/`; the cron; the Arena.
