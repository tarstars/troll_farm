# Review 2 (R3, final round) of `docs/reports/2026-08-28-top-four-algorithms.tex` — 2026-08-28, 03:55–04:05Z

Reviewer: R3 (second and final review round). Only the `.tex` was edited; structure, preamble, packages and macros untouched. Review 1 (R2, 37 corrections) was read first and none of its fixes was undone. R1's report on the four source documents (`local_claude_1/reconstructions/REVIEW-2026-08-28.md`) arrived while I was working; every number it corrects was re-checked in the report (details below).

## What was checked

- **Plain English, sentence by sentence.** Every technical word at first use (troll, shack, talents, train, referee, rating, gist, neural network, median, search, pseudo-code, hybrid, denial, tie-breaks — all already explained by R2); the remaining jargon found and replaced: "roster cap", "fine-tuned", "was gamed", "bank" (verb), "fitted rules", "training ladder" / "fixed ladder" (which the owner could confuse with the public ladder), the two-number talent shorthand `2/2`.
- **Consistency inside the report**: troll counts, turn numbers, the plant-cell rule share (78–90 % in §5 and §11), the training-trigger share, the games counts (848 profiled, 784 replayed in full), the number of workers and reviewers (the preamble says eight workers and three reviewers; the body said two reviewers — now three).
- **Consistency with `local_claude_1/reconstructions/README.md`** — the disagreements are listed below; in each case the per-player `ALGORITHM.md`, the profiles and the fits were trusted and the report fixed; README was not edited.
- **Spot fact check, 15 numbers** against `profiles/<player>.md`, `fits/{delineate,norxondor,Bubaptik,MSz}.md`, `fits/README.md`, `sources/SUMMARY.md`, `prior-art.md` and the four `ALGORITHM.md`:
  1. delineate 223 games, 78 % wins, 415 vs 253, wood 93 % — holds (profile §9).
  2. delineate 98 wood per game = 75 own + 12.5 opponent + 11 wild — holds (fits §0).
  3. delineate third troll in 56 % at median 111, fourth in 27 % at median **144** — report said 145; fixed to the profile's 144 (fits say 146; README 144).
  4. delineate plant-cell rule 89.9 %, harvest rule 70.5 %, chop rule 41.8 % raw / 20.5 % tie-adjusted — hold (fits §1, §2, §4).
  5. norxondor 0.13 ms over 63,945 turns; P→D median 153, middle half 124–173, one turn after the last TRAIN in 62 % — hold (ALGORITHM §1, §2.3).
  6. norxondor ladder minimums and caps, 441/443 specs, delay 0 in 439/444, 76/184 turn-1 trains, 1,036/1,036 mining trips in deficit — hold (ALGORITHM §3.1, §3.7; fits §3).
  7. norxondor plant-and-cut: 1,116 own bananas cut at size 1, 2,407 of 5,161 own-tree cuts within 4 turns — hold (fits §0).
  8. Bubaptik second troll on turn 2: report said "89 % of games" — that is the profile's 25-turn histogram bin (`'1': 170`), the same artefact R1 found for MSz; the per-turn verb table gives TRAIN 0.83 at turn 2 and the ALGORITHM says 154 of 186 first purchases — fixed to "154 of the 186 first purchases we could trace (83 %)".
  9. Bubaptik 147/154 exact turn-2 rule, 139/147 third trolls on the first affordable turn, 14 affordable fifth trolls not bought, 890/18 banana picks, CHOP 0.03→0.69 — hold (ALGORITHM §3.1, §3.2).
  10. Bubaptik wood 69 per game (MSz 80, norxondor 80, delineate 98) — holds (profiles); added to §8 with the chop-command distinction R1 asked for.
  11. MSz trains on turn 1 in "214 of 215 games" — the profile's 25-turn bin; ALGORITHM/R1: 196 of 203 full-length games, rule exact 196/196, verb table TRAIN 0.97 at turn 1 — fixed.
  12. MSz turn-1 talent rule (speed 2 iff plums ≥ 5, carry 2 iff lemons ≥ 5, harvest 2 iff apples ≥ 5 and lemons ≥ 5, chop 1) — the report already had "(and carry 2)"; made explicit.
  13. MSz third troll 441/444 delay 0, median 97, 200/444 bigger spec not taken, 34 two-troll games with 12 % wins, fourth troll 38 % at 128–129 — hold (ALGORITHM §2, fits §0); the "waits for the 12th iron, 18 of 21" fact added.
  14. Training trigger "within one turn" per player: delineate 361/412 = 88 %, Bubaptik 404/425 = 95 %, norxondor 444/444, MSz 444/444 — the range is 88–100 %, not 88–99 %; same-turn only 61 % / 60 % for delineate / Bubaptik (R1) — fixed.
  15. Our champion's chop rule across the four: raw 29.9–41.8 %, tie-adjusted 15.8–30.1 % (fits) — the report's "20–42 %" (from README) was neither; fixed to "30–42 %, and 16–30 % with random tie-breaks".
- **Profile "size-1 share of felled trees"** (R1's item 6): searched the report — the only size-1 figures are norxondor's 1,116 plant-and-cut bananas (from the exact fits) and MSz's "71 % size 4" (fits); no profile size-1 share is used. Nothing to fix.
- **LaTeX**: `%`, `&`, `_`, `#` escaped in every edited sentence; `\path{}` / `\url{}` untouched; braces balanced; no package added.

## Compile result

`cd docs/reports && xelatex -interaction=nonstopmode -halt-on-error 2026-08-28-top-four-algorithms.tex` twice: **exit 0** both passes. `Overfull` lines in the `.log`: **0**. `Underfull`: 1 (the pre-existing one in the glossary table, unchanged from R2's run). PDF: **8 pages**.

## Edits made (one line each)

Fact corrections
1. §1: "about one hour" → "about an hour and a half" (README says 03:00–03:45Z, but the writers' documents are stamped 03:55Z, 04:10Z and 04:30Z).
2. §1: "and two reviewers" → "and three reviewers (one re-read the four documents against their sources, two read this report)" — matches the preamble's `pdfauthor` and the actual R1/R2/R3 setup.
3. §5: training trigger "88–99 %" within one turn → "88–100 %", with "on that very turn in about 60 % of cases for delineate and Bubaptik and in 99 % for norxondor and MSz" (replaces the vaguer "most often on that very turn").
4. §5: our chop rule "20–42 %" → "30–42 % … and just 16–30 % when the rule rates several trees equally and must pick one at random" (fits: raw 29.9–41.8, tie-adjusted 15.8–30.1).
5. §5: "measured on 182–223 games each" → "191–223 games each (182–215 of them replayed in full)" — the two sample sizes were being mixed.
6. §6: delineate's fourth troll "at 145" → "at 144" (profile median; README 144; fits 146).
7. §8: Bubaptik second troll "on turn 2 in 89 % of games" → "in 154 of the 186 first purchases we could trace (83 %)"; "exact in 147 of 154 cases" → "of those 154".
8. §8: added "the third troll has chop 2 in 114 of 154 cases" to the `4/3/h/c` sentence (R1 item 3).
9. §8: added "it brings home the least wood of the four (69 pieces per game; MSz and norxondor 80, delineate 98), although MSz gives fewer chop commands" (R1 item 5).
10. §9: MSz "trains on turn 1 in 214 of 215 games" → "in 196 of the 203 games we replayed in full (97 % of all its games), by an exact rule that held in all 196"; harvest clause → "if at least 5 apples and at least 5 lemons (that is, only together with carry 2)" (R1 item 1).
11. §9: fourth troll: added "the program waits for the twelfth iron that chop 3 costs rather than settle for chop 2 (in 18 of the 21 cases where iron was the last thing missing)" (R1 item 4).
12. §9: "118 chops per game, the fewest of the four" → "118 chop commands per game, the fewest of the four (though Bubaptik brings home less wood)".
13. §9: fruit points of "the others 27–33" → "27–34" (R1 harmonised the MSz document to 34 for norxondor).
14. §3: MSz "buys two heavy lumberjacks" → "one or two" (the fourth comes in 38 % of games).
15. §3: our bot "plants almost nothing" → "plants little" (it plants 10 a game, as §5 says).
16. §5: "(MSz never raids)" → "(MSz does not raid)" (3.6 % of its early chop targets are near the enemy shack).

Plain-language / clarity
17. §2: "a small banana falls to one or two chops" → "a freshly planted banana falls to a single blow from a strong chopper; a full-grown apple takes many" (true for every chop power; R2 had flagged the old wording).
18. §5: "bananas later (they are the cheapest wood)" → "(the fastest-growing and softest tree, so the quickest wood)".
19. §5: "bank a little wood" → "bring home a little wood".
20. §6: "was gamed: it built many cheap trolls" → "it cheated: it built many cheap trolls to collect the rewards".
21. §6: "everything fine-tuned together on the score" → "everything trained together once more on the score alone".
22. §6 and §9: "training ladder" / "fixed ladder" → "fixed sequence of trolls to buy" (the word "ladder" is used for the public ranking elsewhere).
23. §8: "a `2/2` hybrid" → "a small hybrid (speed 2, carry 2; it can both harvest and chop)".
24. §8: speed-4 trolls chop 69–77 % "of their turns" → "of their action turns" (moves excluded, as in §6).
25. §10: "Bubaptik's roster cap and slow-troll fallback trigger" → "the limit on how many trolls Bubaptik buys, and what makes it fall back to a slow troll".
26. §10: "fitted rules of norxondor" → "rules fitted to norxondor's games".
27. Glossary: "MSz probably does" (search) → "MSz perhaps does (a guess)" — the documents mark it GUESS.

## Discrepancies with `local_claude_1/reconstructions/README.md` (README not edited; the report follows the documents)

1. README: training "delay 0 in 88–99 % of trainings" — delay 0 is 61 % (delineate) and 60 % (Bubaptik); "within one turn" is 88–100 %. Report now says the latter with both figures.
2. README: "MSz trains on turn 1 in 214 of 215 games" — 25-turn bin; the exact count is 196 of 203 full-length games (R1). Report fixed.
3. README: MSz's harvest rule "harvest 2 iff apples ≥ 5" — needs "and lemons ≥ 5 (carry 2)". Report has it.
4. README: "The late trolls are carry-3/4, chop-3, harvest-0 lumberjacks" — Bubaptik's third troll is chop 2 in 114 of 154, delineate keeps harvest 1. Report says "chop 2 or 3, little or no harvest power" (R2) and now gives Bubaptik's 114/154.
5. README: plant-cell rule "84–90 % of all plants" (twice) — MSz is 77.6 %; report says 78–90 % (R2).
6. README: "30–40 trees a game" — norxondor 29.1, Bubaptik 28.8, MSz 29.5; report says 29–40 (R2).
7. README: our chop rule "predicts 20–42 % of their targets" — the fits give 29.9–41.8 % raw and 15.8–30.1 % tie-adjusted; report now says 30–42 % / 16–30 %.
8. README: "2,407 such cuts" described as plant-and-cut bananas felled at size 1 the next turn — the fits count 1,116 own bananas cut at size 1 and 2,407 own-tree cuts within four turns of planting; report says both (R2).
9. README: delineate's fourth troll "at 144" agrees with the profile; the fits say 146 — report uses 144.
10. README: "eight parallel workers between 03:00Z and 03:45Z" — the writers' documents are stamped up to 04:30Z; report says "about an hour and a half".
11. README: Bubaptik "second troll on turn 2" (no share given) — the exact share is 83 % of traced first purchases, not the profile summary's 89 % (25-turn bin).
12. README and §12 of the report: `sources/` has 26 files — agrees with the directory listing (26 including `SUMMARY.md`); `prior-art.md` §5 says 27 — not followed.

## Not verifiable from the listed sources (left as is, flagged)

- §1 "Our own bot stood at about 19–21" — project state (board readings 19.8 and 21.2), not in the reconstruction documents.
- §1 the exact working time — the documents give only start and finish stamps.
- §8 Bubaptik's "154 of 186 first purchases" vs the profile's 191 games with a second troll — five seats unaccounted for (R1 notes it; probably games without a raw replay). The report says "we could trace".
- §8 Bubaptik's fifth troll at turn 164 — W5 and the profile; `fits/Bubaptik.md` prints 178 on 12 games (unreconciled, R1). Report keeps 164.
- §6 "days or weeks" for a re-training project and §7 "our reading of the two letters" — writers' judgements, marked as such (R2).
- §11 item 1's recommended "carry-3, chop-3, no-harvest lumberjack" is the README's proposal for our bot, not a measurement; the measured late trolls are chop 2–3, harvest 0–1 (§5). Left as a recommendation.
