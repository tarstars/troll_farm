# Owner brief — why those two trolls were never given a job

You asked, in the 4b sitting: in OSC-032 and OSC-033 a troll stood still for 110 and 143
turns while work was available on every one of those turns, and nobody assigned it a job.
Why? Here is the answer in plain words. It is a measurement. **It names no bug and asks you
for no decision about the code** — whether this behaviour is wrong is your ruling, not mine.

## The short answer

Somebody did give it a job. The job was **"wait"**.

Every single turn of both windows, the bot's candidate generator ran to the end of its
options, found none of them applied, and returned a list with exactly one thing in it: wait.
The selector then did the only thing it could — it picked the only candidate it was handed.
So this is not a case of the selector ignoring available work. It is a case of the generator
telling the selector — on every turn of both windows, 110 and 143 of them — that there was nothing to do.

The exact line it came back through is the last resort in the main generator, the branch that
fires when regeneration is on and there are no chops available. It fired on **110 of 110**
turns in OSC-032 and **143 of 143** in OSC-033 — not most turns, every turn — and the four
things the generator was looking at were identical on all of them: the troll was carrying
nothing, it had room for two more, regeneration was safe, and there were no trees worth
chopping.

## Why it never got out of that state

Nothing changed. That is the whole of it. The four conditions above never moved, on any turn,
in either game. There was no oscillation between two options and no near miss — the generator
formed no real candidate at all, so there was nothing for it to pick between. In OSC-032 you
can see the moment it happens: the troll works normally for 90 turns, gathers, chops, banks a
full load on turn 90 — and from turn 91 on it never finds another chop, so it waits out the
rest of the game.

## The thing I expected to find, and did not

The last investigation (Phase 3, a different case) found this same fallback **throwing away
real work**: it had built two genuine pick-up candidates and then discarded them and replaced
them with a bare wait. That is a much more alarming shape, and the charter warned me not to
assume it repeated here.

It does not repeat here. In these two games the fallback discarded exactly one thing per
turn — the wait it had just created itself, which it then recreated. **Nothing real was
formed, so nothing real was thrown away.** Same line of code, different event. Whatever
Phase 3's case is, these two are not more of it.

## One thing worth your eye

OSC-032's recorded window matches what the current champion does exactly: it stops on turn 91,
the window starts on turn 91.

OSC-033 does not. The recorded window starts at turn 58, but on the current champion that
troll actually stops at **turn 21** — 37 turns earlier — and its first 14 idle turns come
back through a different branch of the code before joining the same one. So on today's
champion that troll's idle run is 180 turns, not 143. I am reporting that as measured and
drawing no conclusion from it; the recorded window came from an older bot, and the difference
may simply be that.

## What I did not answer

You flagged that `turn >= 100` sits suspiciously close to both windows. I checked the block
it guards: **it pushed nothing on any turn**, including the turns after 100 in both games. So
the turn number alone does not explain these windows — something else in that same condition
is false too, all the way through. I did **not** measure which part, and I am not going to
guess: the probe does not tap the parts individually, and the one hint I have is a proxy that
I have been burned by before. codex_1 ruled a probe for it not required. If you want that
answer it is a small, separate, chartered job.

Also not answered, deliberately: whether any of this is a defect, whether it happens in other
games, and anything at all about the shelved anti-benching cure or your open
extend-versus-replace question. Two cases were measured; two cases are reported.

## Where the evidence is

- The finding and the full per-turn table: `claude_1/nogoal/route-table-2026-08-21.md`
  and `claude_1/nogoal/route-table-2026-08-21.json`
- The instrument and its six gates, reviewed and accepted before any of the above was
  treated as a finding: `claude_1/nogoal/instrument-note-2026-08-21.md`
- codex_1's acceptance:
  `codex_1/reviews/osc032-033-no-goal-instrument-g1-revision-review-2026-08-21.md`

Measured on the champion you kept this morning (`547fa706…`), as a diagnostic copy only. The
resident file, the dev copy and the live Arena were not touched.
