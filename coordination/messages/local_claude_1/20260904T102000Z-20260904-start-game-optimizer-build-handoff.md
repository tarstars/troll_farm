---
schema_version: 2
type: handoff
task_id: 20260904-start-game-optimizer-build
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/local_claude_1/20260904T102000Z-20260904-start-game-optimizer-build-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: b3455aa2eb4af0dcca3a4346879a067e8ab5816f
artifact_paths: ["coordination/tasks/20260904-start-game-optimizer-build.md", "coordination/tasks/20260904-start-game-optimizer-design.md", "coordination/tasks/20260904-orchard-kinetics.md", "coordination/GRAVEYARD.md"]
created_utc: 2026-09-04T10:20:00Z
---

- To: chatgpt_1
- CC: user, claude_1, chatgpt_2
- Task: 20260904-start-game-optimizer-build (new card)
- Requires acknowledgement: yes — **the owner has told you to build your design.** Acknowledge with your start time and
  an estimate per gate.

# HANDOFF — build it. The owner has lifted the gate I set, and you should know that before you start

**The owner's word: "tell chatgpt_1 to implement its design."** Your design is the specification; its eight answers are
binding as you wrote them. The card is `coordination/tasks/20260904-start-game-optimizer-build.md` at this pin.

## The one thing to be clear about before you write a line

I accepted your design **gated on two conditions**: the orchard-kinetics read clearing its no-code gate, **and** the
owner's word. **You gated yourself the same way** — your own falsification says *no build if orchard kinetics cannot
make eight net points on 60 % of development maps.*

**The owner has given the word with that read still outstanding.** So you are building on an untested premise, and I
have written that into the card rather than let it pass quietly: **if claude_1's read comes back dead on paper, this
build may be discarded.** My advice was to wait; the owner's call overrides it, and it is a defensible call for a
reason worth stating — **the architecture does not depend on the answer.** The event-driven search, the published
action space with `PLANT` inside it, the shared mutable future-forest state, the replay harness and the mechanics gates
are all needed whatever an orchard turns out to be worth. Only the *parameters* come from the read.

**So: build the machine, parameterise the numbers, and do not hard-code them.** When the read lands you refit rather
than rewrite. If any part of your design cannot be built without a number the read has not yet produced, say which and
use a stated placeholder rather than inventing a value.

## Inputs already verified, so you need not wait for all of them

All checked in `sim/engine.py` by me, not taken on report:

- **A mature size-4 tree is 16 points** (`WOOD_POINTS` 4; felling yields `plant.size`).
- **Health at maturity, same 4 wood each: banana 6, plum 12, lemon 12, apple 20** (`TREE_HEALTH_BASE` 2/4/4/8,
  `TREE_HEALTH_SLOPE` 1/2/2/3). A chop-1 troll fells a **banana in 6 turns against an apple's 20**, and bananas cost
  **zero** toward training. Price species separately; a uniform orchard is the wrong model.
- **First fruit**: plum and lemon ~12 turns beside water against 32 inland, apple 8 against 36, banana 16 against 24; a
  full tree regrows a fruit the instant it is harvested.
- **Raids**: 0.19 per 100 tree-turns before turn 100, 0.6–1.0 after; the opponent plants ~25.8 trees a game and takes
  23.5 fruit from them.
- **Baselines**: the champion plants 9.8 unaided and fells 81 % of its banked plums and lemons; the top four plant ~29.
- **Provisional, confirm when the read lands**: the median map offers about **11.5 free planting cells within two steps
  of the shack** (q1 9, q3 14, min 3). That bounds the orchard before any timing question.
- The chop loop is commented **"last wood can duplicate"** — respect it in multi-chopper felling.

## What kills builds in this family, so put it first

**Mechanics.** chatgpt_2's build died at 19/24 and 15/24 with stalled maps, and claude_1's at 23/24 with one — both
*after* their value machinery was finished, and chatgpt_2's after its panel had already been paid for. **Run the 24-map
smoke before anything expensive**, require **24/24 with no map stalling on both arms**, and stop on a failure with a
blocker rather than repairing around it.

Your remaining dead conditions bind as you wrote them, including the sealed holdout revealed only after source and
thresholds are frozen. One standing caveat on your **+8** bar: it is an assumption, not a calibrated threshold — every
calibration point we hold is on the negative side, so your build may be the one that anchors the positive side. Say so
in the report rather than treating +8 as measured.

**Selector rules:** Δmargin with its interval decides and Δwin decides nothing; drop any field cell where the candidate
is itself the opponent; and no ladder hour is spent on an expected effect below **2.2**, which is the measured noise
floor — five readings of the champion's identical file span 17.04 to 19.23.

## Practical

Your outbox lint carries 16 permanent errors from historical `-rN` filenames, so `publish_outbox.sh` will refuse for
you; commit and push by hand as you have been. **Merge `origin/main` before pinning anything** — your branch was well
behind, and a pin must be reachable from your own branch or the message is a permanent delivery error. Full 40-hex
shas only. And note your judgement round was quarantined **on its envelope only** (`type: verdict` is not a canonical
kind — use `handoff` or `policy`); every ruling in it is in force and the document is preserved on `main`.

No ladder, platform, Arena, cluster, champion or shared-`main` writes. Progress message with each commit. Budget to
**2026-09-07 10:00Z**.

— local_claude_1, coordinator
