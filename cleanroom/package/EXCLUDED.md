# EXCLUDED — what is deliberately not in this package, and why

This is a clean-room experiment. You are being asked to build a bot for this game from a written
description of the game, of the platform, of one existing bot's observable play, and of what has
been learned about the domain — and from nothing else.

The point is not secrecy. The point is that a description good enough to build from is a thing
this project has never had, and the only way to find out whether it has one now is to have
somebody build from it who cannot fall back on the original.

## Deliberately absent

- **Every line of the reference bot's source code.** It is in this package only as a compiled,
  stripped executable (`harness/reference-bot`). There is no source, no pseudocode, no module
  list, no function names, no data structures, no parameter table, no scoring formula.
- **The readable rewrites and the diffs between bot versions.** This project keeps a
  human-readable copy of each bot and a line diff for every change. None of it is here.
- **The simulator used for development.** `harness/referee.py` was written for this package from
  `RULES.md`; the production simulator, the feature extractors and the state representations
  built on top of it are not here.
- **The map generator.** The maps in `harness/maps/` are frozen real starting positions, so the
  package needs no generator and carries none.
- **Every opinion this project holds about how a bot for this game should be structured** — the
  phases, the roles, the way work is assigned to workers, the way candidate actions are scored
  and compared, the way plans persist across turns. All of it is architecture, all of it is
  deliberately absent, and `CHAMPION-BEHAVIOUR.md` was written so as not to imply any of it.
- **The reference bot's own debug output.** The build that played the recorded matches printed a
  line every turn describing its internal state. That channel was stripped from the evidence
  before the behaviour document was written, and it is stripped from the binary you have.

## Present, and why each is fair game

- **`RULES.md`** — the referee's behaviour. Facts about the world, not about any bot.
- **`CONSTRAINTS.md`** — the platform's limits. Same.
- **`CHAMPION-BEHAVIOUR.md`** — what a spectator can see the reference bot do, with a game
  observation behind every rule. A spectator is exactly what you would have if you played it on
  the platform yourself.
- **`DOMAIN.md`** — results that were paid for with real ladder time, stated as results rather
  than as designs, each with the strength of its evidence attached. Withholding these would not
  make the experiment cleaner, it would just make it slower and more expensive.
- **`harness/`** — a way to run your bot and see it play.

## Honesty about how clean this room is

Three things are true and are stated here rather than hidden:

1. **Whoever wrote this package had seen the reference bot's source.** Everyone on this project
   has. A perfectly unseen author does not exist, so the guards that do the work are procedural:
   every behavioural claim carries a game observation, the two behavioural documents use no
   internal vocabulary, and a second agent audited them for code leakage before you saw them.
   Judge the result by whether the documents read like a bot's design or like a spectator's
   notes.
2. **Two leakage channels were found and closed, and finding them means others may remain.**
   The recorded matches carry the reference bot's own per-turn debug line, which names its
   internal roles — it was stripped from the evidence. And the compiled binary, unstripped,
   exposed the bot's entire internal structure through its symbol names — it is shipped stripped,
   and a check confirms zero remaining internal symbols. The stripped binary was proved to play
   identically to the original over 9,502 seat-turns on the 24 frozen maps, so nothing about its
   play was changed to hide anything.
3. **Containment is by instruction, not by a wall.** Nothing stops a program from reading outside
   this directory. You are asked not to, and the package is built to make it unnecessary. If you
   find yourself needing something that is not here, **say what you needed** — that is the most
   valuable single output of this experiment, more valuable than the bot.
