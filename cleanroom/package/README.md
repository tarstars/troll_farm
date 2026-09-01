# Build a bot for this game

Everything you need is in this directory. Read it in this order.

| file | what it is |
|------|-----------|
| **`RULES.md`** | the game, completely — what the referee does, as physics |
| **`CONSTRAINTS.md`** | what the platform will and will not accept: one file, size, time, seats |
| **`CHAMPION-BEHAVIOUR.md`** | what an existing strong bot does and *why*: Part I is one page of principles, each marked essential / habit / not determined — build from that; Part II is the evidence, every count and match citation, measured over 160 real matches — check against that |
| **`DOMAIN.md`** | what has been learned about this game the expensive way, with the evidence level of each line |
| `champion-purchases.json` | data behind `CHAMPION-BEHAVIOUR.md` principle 2: for each of the 160 matches, the shack on every turn up to the moment the bot bought its second worker, and what it bought — for fitting your own rule where the document has none |
| `endgame-truth-table.json` | data behind principle 9: every turn before 251 with at most four trees alive, with the score relation, the workers' state and whether the conversion started — for choosing your own start rule |
| **`harness/`** | 24 frozen real starting positions, a referee with its boundary tests, and the acceptance ladder |
| **`EXCLUDED.md`** | what is deliberately not here, and why — including the existing bot's executable, which you receive only after your version 0 is frozen |

## The job

Write a bot that plays this game at least as well as the existing bot described in
`CHAMPION-BEHAVIOUR.md`, from this package alone. Do not read outside this directory; if you find
yourself needing something that is not here, **write down what you needed** — that is the most
valuable output of this experiment.

Climb the acceptance ladder in `harness/README.md` in order: legal complete matches against your
own bot first — then **freeze version 0** (its source hash is recorded) and only then receive the
existing bot as an executable for the 48-match scout, the locked 144-cell panel and, if close,
400 matches. No strength number counts until your bot plays 48 of 48 legal, complete matches.

## Two things worth knowing before you start

**`CHAMPION-BEHAVIOUR.md` describes a bot, not the best bot, and its habits are not your
specification.** Its Part I marks what carries score and what is merely habit; copy the first,
decide the second. A leaner bot of equal strength is the hope of this experiment, and equal
strength is measured on the harness, not by resemblance. `DOMAIN.md` §1.3 records the largest
known gap between it and the strongest players on the ladder, and it is a gap the described bot
does not close.

**Where a document does not know something, it says so.** Three of the described bot's choices
— when it buys its worker, which tree it walks to next, and the exact turn its endgame
conversion starts — are marked OPEN rather than guessed at, with the data to fit your own rule.
Those are the places where your own judgement has to do the work, and where a different answer
is not automatically wrong.
