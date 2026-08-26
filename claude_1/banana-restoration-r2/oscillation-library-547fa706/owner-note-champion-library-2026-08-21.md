# The champion has its own fixtures now — one page for the owner

**2026-08-21 · claude_1 · card `20260821-champion-subject-library` (your "go") · measurement only,
nothing about any bot changed.**

## What you asked for, and what came back

You said fixtures should follow the champion, because we were measuring with stale baskets. The
champion of record — the Door-1 bot `547fa706…` you kept yesterday morning — was run against
itself over **the same 240-game panel** the old library used, and every oscillation and stall
episode it produced was frozen the same way. Result: **21 situations from 28 episodes**, against
the old subject's 34 from 46.

Nothing was re-ruled. Your rulings are about **mechanisms**, and mechanisms do not belong to a
bot; only the *exhibits* do.

## The one number to keep

**21.** That is how many recorded positions the champion actually owns. The old 34 belong to
`readable__no_orchard`, a different program, and the champion re-runs only 11 of them as the same
game. From today the sentence "case OSC-xx is fixed/not fixed on the champion" is only meaningful
about **this** library.

The case NUMBERS ARE NOT THE SAME between the two libraries. Old OSC-013 is new OSC-011, old
OSC-017 is new OSC-010, old OSC-012 is new OSC-009. Every page says which game it is; the table
in `carry-over-2026-08-21.md` gives the mapping in full. Please read a number as a page link, not
as a name.

## What the champion's own fixtures show

| shape you ruled on | exhibits on the champion |
|---|---|
| corridor / open-map pass — a stationary troll on the route | 8 cases (new OSC-001…008) |
| idle troll parked on a plant | 9 cases (new OSC-009…017) |
| single-troll goal flip | 1 case (new OSC-018) |
| same tree wanted → reservation | **no exhibit** |
| benching — work was there and the troll waited | **15 of 21 cases**, 1,751 benched unit-turns |

"**No exhibit**" means this library contains no case of that shape. It does **not** mean fixed.
The floor is 240 games; a shape can be absent because it did not come up. I have not written the
word "fixed" about any mechanism anywhere in this delivery.

The benching row is the one worth your attention: it is your rule R-2, it is still the most
common thing in the champion's own record, and the worst single case (new **OSC-021**, map m059)
carries **380** unit-turns where a troll waited with work available.

## Pages to look at

`claude_1/banana-restoration-r2/oscillation-library-547fa706/viewer/index.html` — open it in a
browser, no server needed. Suggested three, all of them the champion's own games:

- **OSC-021** — the worst benching case in the library (m059, seat 0).
- **OSC-010** — an idle troll parked on a plant for 194 turns (m014; this is the game you knew
  as old OSC-017).
- **OSC-001** — the corridor pass, the shape rule R-1 came from (m110; same game as old OSC-001,
  and one of the 11 that carried over).

The pages show recorded facts as solid marks and the one inferred thing — where a troll would
land if its order completed — as a dashed hollow circle. They record nothing and rule nothing.

## What I did NOT do

No cure, no candidate, no Arena action, no deployment. The auto-refresh hook that would
regenerate this library the next time you rule KEEP is **designed only**
(`refresh-hook-design-2026-08-21.md`); it goes to review and then through the normal deploy card,
because a thing that writes to the record unattended should not arrive as a side effect of a
measurement task.

## One thing that turned up on the way, worth thirty seconds of your time

The old library's panel config was **edited on 2026-08-12, after the library was frozen** (the
source-portability repair). Nothing measured changed — I rebuilt all 34 old situations and every
window, board, command line and classification came back byte-identical — but the config file no
longer matches the digest the library recorded, and it took a control to prove that the
difference was harmless rather than real. The record caught it because the library had pinned the
config's digest at freeze time. That pin is the reason the answer is a paragraph instead of a
week.
