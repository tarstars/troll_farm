# Reconstructions of the four top players — the night of 2026-08-27/28

**Owner's goal (19:5xZ, before nine hours of sleep):** *"recover algorithms of 4 top players in
troll_farm competition. algorithm — description of actions which is enough for writing a program.
all means are good: internet search, analytics over our databases, whatever."*

**The four (Legend ladder, 19:50Z):** #1 **delineate** 30.89 · #2 **norxondor_gorgonax** 29.66 ·
#3 **Bubaptik** 27.90 · #4 **MSz** 27.72. Our corpus (`/home/tarstars/prj/troll_farm/data/processed/`)
holds every command of delineate (agent `6479768`, 223 games), norxondor_gorgonax (`6480540`, 218) and
MSz (`6479460`, 216); Bubaptik is looked up by name.

## Deliverable (by ~04:30Z, before the owner wakes)

`local_claude_1/reconstructions/<player>/ALGORITHM.md` for each of the four — in plain words, then
pseudo-code: the phases of a game, the state the bot keeps, the per-turn decision procedure for each
troll (what it considers, how it scores, what it picks), the training plan (which troll, when, paid
how), planting and harvesting rules, chopping rules, denial or contest behaviour, the endgame; every
number that can be measured is measured (with n), every guess is marked as a guess, every gap is
named. Sources cited: the player's own write-up if one exists (archived verbatim under
`local_claude_1/reconstructions/sources/`), our corpus analytics (`profiles/`), decision-rule fits from
replays (`fits/`). Plus `README.md`: the four in one page for the owner, what is solid and what is not,
and which of their ideas are the nearest to test on our champion.

## Workers (subagents, in parallel; none runs git, none touches the Arena; each writes only under its own directory)

- **W1 — internet.** Postmortems, forum posts, blogs, repositories, videos of the four (and, second,
  of any Spring Challenge 2026 Troll Farm top-20 player). Archive the raw text with URL and date under
  `sources/<player>-<source>.md`; summarize each into an algorithm sketch.
- **W2 — prior art in the repo.** Everything already reconstructed or measured about the four:
  Phase 9 imitation, Phase 14 Norxondor reconstruction, Norxondor's four-stage workforce ladder
  (8,738 triggers), L1 delineate readiness, D-series records, CONSTRAINTS, the archive, T-1's field
  comparison, rank-hypotheses' postmortem pointers. Output `prior-art.md` with per-player sections.
- **W3 — behaviour profiles from the corpus.** One tool (`profiles/profile_bot.py`) over
  `turns.jsonl.gz` + `games.jsonl` + `maps.jsonl`; per player (and our champion for contrast):
  training ladder (talents and turn for troll 2, 3, 4), verb timelines by 10-turn bucket, planting
  (type, timing, cell relative to shack and water), harvesting (own-planted vs wild), chopping (type,
  timing, near whose shack), mining, unit roles, endgame, score composition, wins by opponent class.
  Output `profiles/<player>.md` + `.json`.
- **W4 — decision-rule fits from replays.** Reconstruct per-turn states (map, trees, units) for a
  sample of each player's games with the existing replay/trace tooling or our referee mirror
  `sim/engine.py`, then fit the rules that matter: chop-target choice, plant-cell choice, training
  trigger, harvest choice, endgame trigger. Report each fitted rule with its accuracy over the
  decisions it explains. Output `fits/<player>.md` + code.

The coordinator integrates: `<player>/ALGORITHM.md` ×4, `README.md`, the board (Track R), the
morning brief.
