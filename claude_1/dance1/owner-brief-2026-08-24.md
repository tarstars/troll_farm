# Owner brief — why do the dances that survive in real games happen?

- Task: `20260824-real-game-dance-attribution`, step 3. claude_1, 2026-08-24.
- Evidence: `claude_1/dance1/g2-execution-2026-08-24.md` and the published fact table
  (`claude_1/dance1/results/`). Every number below has one source and one meaning.
- Awaiting codex_1's G-2 execution review. Nothing here is a ruling.

**The one caveat on every number: dancing measured off replays is an upper bound.** The adapter
rebuilds plant clocks it cannot observe, and that error direction invents dances rather than
hiding them. "22 episodes" means "at most 22".

---

## The hole this was meant to close

On 2026-08-23 the record said trolls danced in about 11 % of real games and blocked each other 0
times in 469 — and it said nothing about *what any of those trolls wanted or what was in its way*.
That is now closed. **462 dance episodes have a complete fact row**: who danced, between which two
cells, for how long, which teammate was where, what the troll said it was aiming at on every turn
of the window, whether two units traded places, whether an opponent was standing there, and how the
dance ended. 80 of those episodes are the instrument's own games (469 of them, telemetry on) and
382 are the champion's (306 games, no telemetry).

## The answer, in plain words

**In four dance episodes out of ten, a teammate is parked on top of a plant, working it, and will
not move.** Not idle — *working*. It chops, picks, drops and plants, on one cell, orthogonally
adjacent to the two cells the dancer is bouncing between. On the instrument's games this is 34 of
80 episodes; on the champion's, 146 of 382. In 24 of those 34, the teammate is standing on a live
plant. In 10 of 34 it never leaves that cell again for the whole game.

**In the rest, there is no teammate in the way at all, and the troll's stated want is unstable.**
46 of 80 instrument episodes have a teammate alive but none that qualifies as a blocker. Of those,
22 wanted one fixed thing the whole time and still bounced; 21 changed their stated target *inside*
the seven-to-forty-turn window — 31 of the 36 changing windows name two or more distinct real
targets; and 3 traded places with the teammate.

**No troll ever wanted nothing.** The class for "the dancer had no target at all" is **empty**, 0 of
80. The v2 blind spot — a real want that lost to `WAIT` and reads as `NONE` — is, per the v3
instrument, nearly empty too: across all 34 v3 episodes there are exactly **2 turns** where the
troll chose nothing while a real candidate was available.

**The dances mostly end by themselves.** 52 of 80 end with the dancer simply making progress; 16
end when the parked teammate finally moves; 9 run to the last turn of the game.

## The thing I did not expect, and which I think matters most

**The mechanism the whole frozen oscillation library was built around does not occur in real
games.** The library's dominant shape is `M2` — an *idle* teammate standing on a plant, 14 of its
38 episodes. In 469 real instrument games that class is **empty: 0 of 80**. On the champion's 382
it is 16, about 4 %.

The geometry is the same. The idleness is not. The library's criterion asks for a peer that waits
on ≥ 95 % of turns; the real-game blocker waits on **0 %** of them in 33 of 34 episodes. So a
criterion inherited from panel games sorts real games into a different bin — and the bin it empties
is the one every earlier design conversation was about.

I am not calling that a bug and I have not proposed a cure. It is a statement about where the
episodes fall, and it is the thing I would want ruled on first.

## The two corpora agree

Same measurement, same code, no telemetry on either side: a working blocker in 42.5 % of the
instrument's episodes and 38.2 % of the champion's; no qualifying blocker in 57.5 % and 56.0 %. I am
**not** reporting the gaps between those pairs as differences — different lineages, different ladder
days, different opponents, no randomisation.

## Not established — the section that matters

- **Why the dance happens.** Nothing here is causal. A teammate being adjacent and stationary is a
  correlation with the window, not a demonstration that it caused it.
- **That the dance is swap-induced.** Withdrawn, twice over. The coordinator's refutation stands
  (the champion has no swap rule and dances at the very-old bot's rate), and my own swap-tick
  control failed its negative side: the predicate fires **3,256 times** in 132 of 141 pre-cure
  game × seat pairs that were supposed to be silent. Class 3 is therefore named
  `POSITIONAL_EXCHANGE`, not `SWAP_FLAP`, and the causal reading is gone. Whether that means the
  predicate is too broad or the ledger's premise about the old resident was wrong, **I do not
  know**; 49 % of those ticks have both units commanding a move into each other, which is
  consistent with either.
- **That batch 3 dances more.** It reads 18.8 % of games against 11.4 % and 11.3 %. Different
  submissions, different days, different opponents, no randomisation. One number beside another.
- **That the instrument and the champion differ.** See above; the gaps are not tested and are not
  claimed.
- **Whether the short windows are real.** 34 of 80 episodes are the minimum seven-turn window, and
  in every one of the 11 blocked short-window episodes the "blocker" later moves around the map
  freely (7 to 40 distinct cells). At the long windows, 10 of 23 blockers never move again all
  game. Those look like two different objects to me, and the criterion does not distinguish them.
  I did not adjust a single count for this; the table is published so you can rule on it.
- **Prevalence beyond these four corpora.** Nothing is claimed about any other lineage, opponent or
  day.

## What I am asking for

Nothing to approve. If you want a next step, the one the evidence points at is a ruling on whether
"a teammate working a plant it is standing on, indefinitely, next to the dance" is acceptable play
or a defect — because that is where four episodes in ten actually are, and the inherited criterion
was not written to see it.
