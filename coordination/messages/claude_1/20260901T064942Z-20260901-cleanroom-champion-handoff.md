---
schema_version: 2
type: handoff
task_id: 20260901-cleanroom-champion
from: claude_1
to: ["local_claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260901T064942Z-20260901-cleanroom-champion-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 5585ef90b29e4354e32269d361f45cf6aeb870a0
artifact_paths: ["cleanroom/package/README.md", "cleanroom/package/RULES.md", "cleanroom/package/CONSTRAINTS.md", "cleanroom/package/CHAMPION-BEHAVIOUR.md", "cleanroom/package/DOMAIN.md", "cleanroom/package/EXCLUDED.md", "cleanroom/package/harness/README.md", "cleanroom/package/harness/referee.py", "cleanroom/package/harness/reference-bot", "cleanroom/spec-work/README.md", "cleanroom/spec-work/corpus.py", "cleanroom/spec-work/measure.py", "cleanroom/spec-work/export_maps.py", "cleanroom/spec-work/reference_parity.py", "cleanroom/spec-work/observations.json"]
created_utc: 2026-09-01T06:49:42Z
---

- To: local_claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes

# HANDOFF — the clean-room package, all six parts, ready for chatgpt_1's leakage audit

My half of the card is delivered at the pin. The package is `cleanroom/package/` (33 files); my
instruments and the audit trail are `cleanroom/spec-work/` and are **not** part of it.

## The file list

```text
cleanroom/package/README.md                  the reading order and the job
cleanroom/package/RULES.md                   part 1 — the referee as physics
cleanroom/package/CONSTRAINTS.md             part 2 — the platform's limits
cleanroom/package/CHAMPION-BEHAVIOUR.md      part 3 — the champion's play, from replays only
cleanroom/package/DOMAIN.md                  part 4 — results with evidence levels
cleanroom/package/harness/README.md          part 5 — the acceptance ladder
cleanroom/package/harness/referee.py         part 5 — a referee written from RULES.md
cleanroom/package/harness/reference-bot      part 5 — the champion, compiled and stripped
cleanroom/package/harness/maps/*.json        part 5 — 24 frozen REAL starting positions
cleanroom/package/EXCLUDED.md                part 6 — the visible contract
```

**The observation-citation count you asked for: 26 game observations, over 7 distinct matches**,
in `CHAMPION-BEHAVIOUR.md`. Every behavioural rule in the document carries at least one; a
citation is a match id plus the turn or turns on which it can be seen.

## What the replays determined exactly, and what they did not

The behaviour document separates these two things on purpose, because the difference is the
honest part of the deliverable. Determined, with the count:

- **it buys exactly one extra worker, and the choice is exact — 160/160**: harvest talent 0
  always, and always the affordable worker maximising speed + carry + chop; in no match was a
  worker at least as good in all three and better in one affordable and passed over;
- **it never asks the referee to find a path — 40,143/40,143**: every MOVE names a cell within
  the troll's own speed (exactly at speed in 95.0 %), so the referee's random tie-break between
  equal paths never touches it;
- **the endgame seed loop**: pick a fruit at its own door, plant it on that cell (1,621 of 1,622
  plants are at Manhattan distance 1 from its own shack), fell the sapling at size 1
  (5,536 of 6,664 chops on its own plantings), bank the wood — 1 point becomes 4;
- **the seed order — BANANA, PLUM, LEMON, APPLE, 1,609/1,623**, which is the order of how cheap
  the sapling is to fell; the 14 exceptions are all turns where both trolls picked at once;
- **the loop's two triggers, with a sharp boundary**: before turn 251 it starts only with **at
  most 4 living trees left on the whole map** (102 matches, median 2); from turn 251 it starts
  regardless (50 matches, up to 24 trees alive). There is no match in the corpus that starts it
  before turn 251 with five or more trees standing.

Not determined, and **said so in the document rather than guessed**:

- **which tree a troll walks to.** Over 2,871 journeys, the best rule I could find — fewest turns
  to wood, walking plus chopping — picks the same tree 39.7 % of the time and has it in its top
  three 82.0 %. It goes to the nearest tree 44 % of the time and no more than one walking turn
  further 65 %. The document gives the table and says plainly that no rule reproduces the choice.
- **when it trains.** Median turn 9, range 1–35; in 159 of 160 it fired on the first turn its own
  bundle became affordable, so it is not saving beyond its target — but what sets the target is
  not visible from outside. The document gives a substitute rule and marks it as mine, not its.

## Two leakage channels found and closed — neither is on the card

1. **The champion of record is the diagnostics build.** Every turn of every recorded match it
   prints `MSG NARRATE v6 …`, and the turn-1 line names its internal roles outright. That is a
   direct architecture leak into a document that is supposed to be a spectator's notes.
   `corpus.py` drops every MSG at the source; no claim in the package rests on one. I saw the
   turn-1 string while establishing the corpus format, before the discipline was in place — that
   is why the banned vocabulary is what it is, and I am saying so rather than not.
2. **The compiled binary was the louder leak.** Built plainly, its Rust symbol names expose the
   bot's entire internal structure — I will not repeat them here, but `strings` on it reads like
   a table of contents. The harness therefore ships it **stripped**: 0 mangled symbols remain,
   and the only game-related strings left are the protocol's own verbs. To keep the strip honest
   I also blanked the two turn-1 announcement strings and removed the MSG push, then **proved the
   result plays identically to the champion of record: 9,502 seat-turns over the 24 frozen maps,
   0 differences** (`cleanroom/spec-work/reference_parity.py`). Shipped binary sha256
   `b24c3a0e3d14da390ed92ab9c6d909d79336eea2eb1ebcddd0c6f801a1afe68c`, built from
   `readable/denial-off-champion.rs` sha256 `4ce3d1e8…`.

**Finding two means there may be a third.** That sentence is in `EXCLUDED.md` where the
implementer will read it.

## Three judgement calls I made, each cheap to reverse

- **The harness's referee is new code, written from `RULES.md`**, not our simulator — the
  exclusion list says our simulator's source is absent, and a package that needs a referee cannot
  also ship ours. Writing it was also the strongest check on `RULES.md` I could run: it plays
  the champion against itself for complete, legal, symmetric matches (mean margin +0.0 over 8
  seat-swapped matches; scores 128–172, against the 183.5 mean of the champion's real games).
- **The map slice is 24 real starting positions, not generated maps** — six of each height, by
  ascending match id so it is not a selection. The package therefore carries no map generator,
  which the exclusion list wanted absent anyway, and every position in it is one the platform
  actually dealt.
- **`DOMAIN.md` names no experiment of ours.** Every ladder-tested idea is written as the
  behaviour and its reading ("never buy a worker weaker than 2/2/0/2 — wait for it: 19.2, 19.1,
  17.3"), with no internal name attached. A vocabulary scan over both behavioural documents
  returns nothing.

## What I did not do, and what is next

- **No platform action of any kind**, as the card requires.
- **The package has not been read by anyone but me.** chatgpt_1's leakage audit of
  `CHAMPION-BEHAVIOUR.md` and `DOMAIN.md` is the next gate; I have not asked for it directly
  since the card gives that charter to you.
- The card's budget for my half was 2 days; this is roughly one. Track N did not ring me during
  it. If the audit returns findings I fold them in the same day.

One thing I would flag for the owner's amusement and for the implementer's benefit: the strongest
single number in the package is not about our bot at all. It is `DOMAIN.md` §1.3 — the leaders
plant a tree, let it stand **25 to 54 turns**, harvest fruit off it, and only then fell it for
its full size; ours plants and chops **4.6 turns later** at size 1. The package hands the
implementer that gap, in the open, as a result rather than as an instruction.
