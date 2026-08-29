# Review 1 (R2) of `docs/reports/2026-08-28-top-four-algorithms.tex` — 2026-08-28

Reviewer: local_claude_1 (first review round). Only the `.tex` was edited; structure, preamble and macros untouched.

## What was checked

- Every number and claim in the `.tex` against: `local_claude_1/reconstructions/README.md`, the four `<player>/ALGORITHM.md`, `sources/SUMMARY.md`, `profiles/COMPARISON.md`, `profiles/<player>.md`, `fits/{delineate,norxondor,Bubaptik,MSz}.md`, `fits/README.md` (for the 784-game validation), `prior-art.md`.
- Every URL in section 12 against the URL header of the archived source files in `reconstructions/sources/` — all eight match verbatim (gist, feedback thread 208241, stats page, referee repo, Astrobytes README, marekesz/contests, side threads 208196 and 208252). The yannmoisan.com link is the one in the existing archive reference.
- Jargon at first use, sentence length, repetition; coverage of every README finding (four kinds of program, common facts, per-player plans, training rules, planting rule, phase switches, what was not recovered, the warning, the ranked ideas, sources with links) — all present; nothing had to be added except explanations.
- LaTeX: `%`, `&`, `_` escaped in text; `\path{}`/`\url{}` kept; braces balanced.

## Compile result

`xelatex -interaction=nonstopmode -halt-on-error` twice: exit 0 both times. `Overfull` lines in the `.log`: **0** (also 0 before my edits). `Underfull`: 1 (pre-existing, unchanged). PDF: 8 pages.

## Edits made (one line each)

Fact corrections
1. §4: "Twelve other top-league players" → "Eleven other" (SUMMARY: 12 Legend players wrote in the thread, delineate among them; the 11 others are the ones listed in §12).
2. §4: "Since June … roughly 220 games of each" → "191 to 223 games of each" ("since June" unsupported by the sources; per-player counts are 223/218/191/216).
3. §4: "checked against the referee's final tallies (848 of 848 games agree)" → "positions and outcomes are read from the referee's own log, so they are exact in all 848 games" (no source states an 848/848 tally check; the profiles state exact positions from the referee log for all games).
4. §4: replays "no disagreement in any of them" → added "except where the referee itself picks one of two equal paths at random" (`fits/README.md`).
5. §5: later trolls "carry 3 or 4 and chop 3, and usually cannot harvest at all" → "carry 3 or 4, chop 2 or 3, and little or no harvest power" (delineate/MSz/norxondor third trolls have harvest 1; norxondor's third and 74 % of Bubaptik's third trolls have chop 2).
6. §5: trained "on the very turn its price became affordable" in 88–99 % → "within one turn … most often on that very turn" (delineate: same turn 61 %, within one turn 88 %).
7. §5 and §11: planting rule "84–90 %" → "78–90 %" (MSz's fit is 77.6 %); "30–40 trees" → "29–40" (norxondor 29.1, Bubaptik 28.8, MSz 29.5).
8. §5: "Lemons and plums come first" qualified to three of the four (MSz's early plants are banana-heavy: 778 bananas vs 496 lemons in turns 0–49).
9. §5: "The first wood reaches the shack around turn 100–120" → only for norxondor and MSz; delineate and Bubaptik bank first wood at median turn 24–26 from their raids; the chop rate climbs after turn 100–150 for all.
10. §5: "the early game has a raid" → "for three of the four … (MSz never raids)" (MSz: 3.6 % of early chop targets near the enemy shack).
11. §6: "playing millions of games against itself" → "a great many practice games (the author gives no count; playing against itself is implied)" (the gist gives no count and never states the opponent pool).
12. §6: third troll "(carry 4, chop 3) … at turn 111 on average" → "(usually carry 4, chop 3) … typically at turn 111 (the median …)"; fourth "(3/4/1/3)" → "usually"; "half to three quarters of its turns" → "of its action turns (moves not counted)".
13. §7: source note "the game author's statistics agree" → they show the same plan but a 56 % contest win rate (not 67 %).
14. §7: "first wood at turn 97 on average" → "median turn 97"; "switches at turn 153 on average (between 124 and 173)" → "median turn 153 (the middle half of games between 124 and 173)" — 124–173 is the 25th–75th percentile, not the range (18–186).
15. §7: "highest chop rate on the ladder" → "of the four" (that is what the profile measured); "stops harvesting by turn 222" → "around turn 222" (median).
16. §7: second troll "otherwise around turn 9–14" → "over all games the second troll comes at median turn 9–14" (the 9–14 medians include the turn-1 purchases).
17. §7: plants "one cell from the shack on average" → "median one cell" (mean is 1.7).
18. §7 and §11: "plant-and-cut … happened 2,407 times" → "1,116 own bananas cut at size 1; 2,407 of all own-tree cuts within four turns of planting" (that is what `fits/norxondor.md` counts).
19. §3 and §8: Bubaptik "joined/entered after the contest" → "was not in the contest's top league (probably a later entrant)" (SUMMARY: "probably a post-contest entrant … or a different name").
20. §8: later trolls "always on the first affordable turn (139 of 147)" → "nearly always … (139 of 147 third trolls)".
21. §9: third troll "at turn 97 on average" → "median turn 97"; chop rule "no rule predicts more than 35 %" → "more than about a third" (best raw fit is 36.1 %).
22. §10: "copied 77 % of norxondor's moves" → "its rules matched 77 % of norxondor's recorded decisions" (the 76.9 % is the intent-tree accuracy, not move accuracy).

Plain-language / clarity
23. §3 table: "trained by self-play" → "trained by practice games"; MSz row explains "search" at first use.
24. §4: "gist" explained ("a public note on GitHub, called a gist").
25. §3, §12: "post-mortem" → "write-up" (three places).
26. §6: "a project of weeks" → "days or weeks" (the gist speaks of days of training).
27. §7: "pseudo-code" explained at first use.
28. §8: "hybrid" and "denial" explained at first use; "caps its roster" → "stops buying trolls".
29. §10: "tie-breaks" explained.
30. §12: "13.3 million command rows" → "turn records" (rows are seat-turns).
31. Glossary: "lumberjack" now "little or no harvest power"; added rows for "median" and "search".

## Not verifiable from the listed sources (left as is, flagged)

- §1 "Our own bot stood at about 19–21" — from the project state, not from the reconstruction documents (consistent with the board: 19.8 and 21.2).
- §1 "in about one hour … and two reviewers" — the README says 03:00–03:45Z; the reviewer count is the coordinator's.
- Preamble `pdfauthor` says "with four workers and two reviewers" while the text says eight workers — preamble left untouched per the rules; the author may want to align it.
- §2 "a small banana falls to one or two chops" — true for chop 2–3 trolls (size-1 banana has 3 health); a chop-1 troll needs three.
- §6 "a project of days or weeks" and §7 "our reading of the two letters" are the writers' judgments, now marked as such.
