# 20260821-corpus-prevalence — how often do the ruled defects happen in REAL games?

- Status: **CLOSED 2026-08-23 by owner ruling — superseded by fresh-game measurement, not
  abandoned.** Owner: *"we can remove 7 about defects in the whole archive. I would prefer to have
  quick iterations with new games and new analytics"*. The question this task asked — how often do
  the ruled defects actually happen — **was answered the same day on fresh games** rather than on the
  archive: 149 real ladder games, 38,869 turns, contention 0 %, dancing 11 %, idleness measured to
  the limit of the instrument (`local_claude_1/narrate/g1-first-grading-2026-08-23.json`). Its one
  remaining blocker was host reach to `data/processed/games.jsonl`; that blocker is now moot because
  the archive is no longer the route. **Deliverable (a), the replay→`Trace` adapter, was delivered
  and G-1 ACCEPTED, and is retained** — it is the instrument the fresh-game grading runs on, so this
  closure destroys nothing. Deliverables 2–4 are dropped.
- Superseded status: OPEN — OWNER-APPROVED 2026-08-21 ~11:15Z ("go").
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1**
  (instrument-first) · Integrator: local_claude_1
- Priority for claude_1: after `20260821-champion-subject-library`; may interleave with it
  (read-only, no build).
- Source: the recorded Arena corpus `data/processed/games.jsonl` (9,082 games as of
  2026-07-30; use the current file, pin its SHA-256 and count) — **our own command
  streams only**; opponents are not replayable and nothing here replays anything.
- Created UTC: 2026-08-21T11:16:00Z

## THE QUESTION (owner's)

Before Arena hours are spent on a cure, how often does its defect occur in real play —
for the resident lineage that played those games, by exact agent id, and in particular
for the most recent ones?

## Deliverables (read-only measurement)

1. Run the accepted detectors (D-1 dance, P4 stall) and the eligible-action oracle over
   our own trajectories in the corpus, per game: episodes found, their length, the unit,
   and the classifier's mechanism label where the classifier can be applied to a real
   trajectory (say where it cannot, and why).
2. **Prevalence table** per mechanism (the five owner-ruled + the benching class): games
   affected / total, episodes per 100 games, turns lost per affected game, split by agent
   id (old resident vs recent) and by map class where the corpus records it.
3. **Cost proxy**, honestly bounded: turns lost × a stated per-turn value proxy (e.g. the
   troll's realized banking rate in that game), with the caveat written next to the
   number. No causal claim about score; this ranks cures, it does not price them.
4. A one-page owner note: which mechanism is worth Arena time first, by real-game
   prevalence, and which are rare.

## Gates

- G-1 codex_1: detector/oracle versions pinned and unmodified; the trajectory adapter
  from corpus records to detector input reviewed; a negative control (a game with no
  episode) and a positive control (a corpus game known to carry one — the real-corpus
  cases in the old library qualify) both observed.
- G-2 the tables + the note.

## Out of scope

No replay, no candidate, no Arena action, no re-ruling; no "the corpus proves the Arena
delta" claims (duration and outcome are post-game variables — M5's rule stands).
