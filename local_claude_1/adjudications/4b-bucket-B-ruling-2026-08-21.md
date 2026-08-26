# 4b bucket B — owner ruling 2026-08-21 (~08:20Z): OSC-005 / 010 / 027 / 030 are BUGS

Recorded by local_claude_1 from the owner's words in the sitting. The owner judged the
games first and stated the mechanism in their own terms; the facts below were pulled from
the FROZEN library (`claude_1/banana-restoration-r2/oscillation-library-98628e98/library/`,
the one the grader and the harness use, 34/34 aligned with `sweep34-door1-base.json`) and
from the champion grader, and checked against the owner's reading case by case.

## The ruling

**All four are BUG under R-2 (a troll with available work must be employed), known-open.**
The four "harmless" stamps proposed in the 4b package are **withdrawn** — they were wrong,
for two reasons that are the coordinator's, not the investigation's:

1. **Wrong unit.** The "not starved" label came from the H-starve-1 audit, whose anchor for a
   dance with a blocker is the BLOCKER (the teammate standing on the tree, which was indeed
   working). The DANCER — the troll the owner watched — was never the audited subject.
2. **Wrong proxy.** "Never waits" was read as "works". A pacing troll emits MOVE every turn.
   The champion grader had already said NOT_FIXED on all four; the package proposed stamping
   NOT-FIXED cases as harmless.

## Owner's mechanism taxonomy — three shapes, all self-inflicted

Rule fact that frames all of it: **enemy trolls never block ours** (they may share our cell);
**two of our own units cannot end on one cell, but may swap cells in one turn** ("circular
swaps allowed"). Every jam here is two of our trolls.

| shape | cases | what happens | owner's remedy |
|---|---|---|---|
| **1. Pass blocked in a one-wide corridor** | OSC-005, OSC-027 | the dancer needs to get past a teammate who is chopping mid-corridor; it paces the two cells in front of it until the tree falls | **swap** (legal in one turn); the chopper steps back and resumes — cost 2 chop turns. This is R-1's shape. |
| **2. Pass blocked in an open map** | OSC-010 | the dancer, full of wood, heads to bank; a teammate chops on the straight line; a detour one row over costs zero extra moves; it paces instead | **route around** — treat a stationary teammate as an obstacle |
| **3. Same tree wanted** | OSC-030 | the dancer wants the banana a teammate is chopping; a free lemon sits two cells further | **a tree being worked is taken**; pick another — the team-picker's job (bucket C family) |

## Per-case facts (frozen library; champion grader in the last column)

| case | window | dancer | what the dancer was doing | teammate | other work in reach | champion `547fa706` |
|---|---|---|---|---|---|---|
| OSC-005 | t7–18 (12) | #2, empty | heading west down a 1-wide corridor toward an apple (hp 17) and a banana | #0 chopping a lemon (hp 10) mid-corridor | none on the near side | NOT FIXED — detector fires |
| OSC-010 | t80–86 (7) | #0, **2 wood in hand** | going to bank; shack 5 cells east | #6 chopping a plum on the straight line | a zero-cost detour; 6 other trees | NOT FIXED — no progress in window |
| OSC-027 | t3–24 (22) | #2, **2 wood in hand, chop power 0** | going to bank down a 1-wide corridor | #0 chopping an apple (hp 20) mid-corridor | none (one tree on the map) | NOT FIXED — detector fires |
| OSC-030 | t24–31 (8) | #2, empty | wants the banana two cells away | #0 chopping that banana (hp 6) | a free lemon 2 cells further (detour open) | NOT FIXED — detector fires |

Cost per episode: a delay of 7–22 turns; in 010 and 027 eight points (2 wood) sit in a
troll's hands the whole time. Frequency across games: unmeasured.

## What is NOT decided

- **No cure is chartered.** The three shapes are three different small mechanisms (swap
  protocol · teammate-aware routing · tree reservation); whether to charter any of them, or
  shelve all four with the 18 benching cases, is the owner's call, not made in this sitting.
- Nothing here touches the two idle trolls (OSC-032/033, measurement in flight) or the
  remaining 4b items (OSC-026 single troll, OSC-012 no-power troll).

## Coordinator error log (so it is not repeated)

- A stale second library exists at `claude_1/banana-restoration-r2/oscillation-library/`
  (33 cases, numbering shifted — only 14/33 agree with the grader). The coordinator read
  OSC-005 from it in the first answer to the owner and described a different game; corrected
  the same sitting before the ruling. The tools use the frozen library and were never wrong.
  A card to claude_1 asks to retire or mark the stale directory.
