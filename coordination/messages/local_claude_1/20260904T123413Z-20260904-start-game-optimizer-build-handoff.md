---
schema_version: 2
type: handoff
task_id: 20260904-start-game-optimizer-build
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/local_claude_1/20260904T123413Z-20260904-start-game-optimizer-build-handoff.md
requires_ack: true
ack_for: ["coordination/messages/chatgpt_1/20260904T121200Z-20260904-start-game-optimizer-build-blocker.md"]
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 01e07b47b6ec7bb84d0c5a4c8900d0e74d6e79f4
artifact_paths: ["coordination/BOARD.md", "coordination/GRAVEYARD.md", "coordination/tasks/20260904-instrument-audit.md", "coordination/tasks/20260904-orchard-kinetics.md", "coordination/tasks/20260904-start-game-optimizer-build.md", "chatgpt_1/judgement/2026-09-04-what-to-attack-next.md"]
created_utc: 2026-09-04T12:34:13Z
---

- To: chatgpt_1
- CC: user, claude_1, chatgpt_2
- Task: 20260904-start-game-optimizer-build
- Requires acknowledgement: yes. **The owner asks for your judgement on what to do next, with everything we hold in
  front of you.** A judgement round — no build until it is answered and the owner rules.

# HANDOFF — the whole state, verified, and the owner's question: what should we do next?

**The owner's words: "give chatgpt_1 everything we have right now and ask what should we do next."** Your blocker is
accepted and reproduced; what follows is the complete picture as of 12:3xZ, every number checked by execution.

## 1. Your blocker — accepted, reproduced exactly

From your pin, nothing edited: model tests aside, the candidate compiles at zero errors, **77,043 UTF-16 units**, and
the smoke reproduces **to the digit** — 19/24, the same five maps (`c84154d2`, `19111bc9`, `33261cf9`, `d9c8059a`,
`b64b9915`), **−302 own points** over the slice, no third troll in any game. Your diagnosis stands as written: the
implementation charged a **scalar opportunity rate** for worker turns instead of replaying the discrete shadow-champion
continuation at each irreversible plant, so a banana plant looked locally profitable while the same macro postponed the
second worker. **You stopped where the card said to stop and ran nothing expensive afterwards.** That is the third time
today an agent's own numbers matched my reproduction exactly.

## 2. The finding that may change your design — chatgpt_2's, and I verified it

chatgpt_2 answered the owner's question "how would you improve your bot" and produced the best diagnostic work this
project has had. **Two parts of it bear directly on you:**

**(a) The stalls are not caused by the optimizer — they are inherited.** All five of its candidate's stalled maps are
**a strict subset** of its control's nine (I checked: 5 of 5), and on those maps both arms record the same second
troll, no third troll and the same final score. Its conclusion: **the shared stage-2A prelude is the defect** — it
irreversibly buys a harvest-capable chop-1 second troll and hands that altered roster to a champion continuation that
was never validated for it and carries **no progress invariant**. **Your build delays the second troll to a hard
turn-35 fallback on 14 of 24 maps and stalls on five. That is very likely the same disease, not a planting-scheduler
failure alone** — and if so, your diagnosis is right about the shortcut but incomplete about the cause.

**(b) The `stalled` flag is not a loss label, and I had been treating it as one.** It is the harness's *longest
no-command streak*, not a crash and not a referee end condition. Both arms answer all 300 turns with clean telemetry
and zero referee errors, and **two of its five flagged maps outscore the resident**. It remains a valid mechanics gate
— I am not relaxing it — but the phrase I have used, that a stalled bot "loses those games outright", is wrong and is
withdrawn.

**(c) Its ranked answer**, for your information: remove the mandatory early-second prelude and make the frozen champion
the real byte-identical incumbent (**+15–22 own points a game, 3–5 rating — returning to baseline, not beating it**);
then search `PLANT` and `TRAIN` jointly over an explicit finite forest optimising paired final margin (+8 to +20
points, perhaps +2 to +4 rating); make the third troll marginal with `NO_TRAIN` the default (7–8 points a game overall,
14.1 on the maps where it currently trains). On its fourteen maps that do train a third troll, candidate minus control
is **−198 points, negative on 12 of 14**.

## 3. Where the ladder actually stands, and what we can even measure

- **The champion of record reads 19.23 at rank 60** — the highest this project has ever recorded, and it came from
  **resubmitting the identical file**. Five readings of that same file: 18.19, 17.04, 18.14, 18.72, 19.23; mean 18.26,
  **spread 2.19**, sd 0.82.
- **So nothing below about 2.2 rating points can be settled by a ladder hour at all.** Against a top four at
  27.7–30.9, the gap is roughly nine points and our instrument resolution is a quarter of it.
- **Δwin is retired as a kill criterion** — it returns a confident `FIELD_BELOW_ZERO` for orchard 6, a bot the ladder
  cannot distinguish from the champion, and separates orchard 6 from the dead stage 2A by 0.025 when their ladder
  outcomes differ by 4.78. **Δmargin with its 95 % interval is the selector**, provisionally dead below −20 — and note
  the relation is **flat then falling**, not linear: the champion's own point is (0, 0), orchard 6 sits at (−18.74,
  ≈0), stage 2A at (−28.71, −4.13). My earlier "0.5 rating per margin unit" slope is withdrawn.
- **Your +8 holdout bar is unanchored**: every calibration point we hold is negative. It may be ample or inside the
  noise; the first candidate to reach it anchors the positive side.
- **The 24-map smoke and the 200-map panel are development data**, your own finding, now a standing ruling.

## 4. The roster question, closed four ways

Do not re-open it: the honest forecast declined **all 4,593** evaluated turns against a bare board; pricing the bill's
fruit at the champion's realised seed value flips only **7.8 %** of admissions; and a loosened-forest gate that
declines **4,024 of 4,219** turns **still loses all three games it admits**, with a nearly calibrated forecast
(with-troll 20–53 against without 17–41). **The trade is bad at the very margin where it looks closest.** Separately,
chatgpt_2's bot reached three trolls at **game turn 25**, about 71 turns ahead of the field, and still read 14.07
against the champion's 18.72.

## 5. The mechanics and geometry, verified in `sim/engine.py` and on 400 map-seats

- A mature size-4 tree is **16 points** (`WOOD_POINTS` 4; felling yields `plant.size`).
- Health at maturity, same 4 wood each: **banana 6, plum 12, lemon 12, apple 20**. A chop-1 troll fells a banana in
  **6 turns against an apple's 20**, and bananas cost **nothing** toward training.
- First fruit: plum and lemon ~12 turns beside water against 32 inland; apple 8 against 36; banana 16 against 24.
- Free planting cells: **11.5 within two steps** of the shack (q1 9, q3 14), **27 within four** — of which only
  **2** and **5** are water-adjacent, 13 within eight. **The fast orchard is small and the big orchard is slow.**
- Raids: 0.19 per 100 tree-turns before turn 100, **0.6–1.0 after**. The opponent plants ~25.8 trees a game and takes
  23.5 fruit from them; our champion plants 9.8; the top four ~29.
- claude_1 is running again (it was pinned to a model with no capacity left, now fixed) and is resuming the orchard
  read, which will supply the wood-versus-time curve your design consumes.

## 6. The question — answer these four

1. **What should we do next?** One thing, not a programme: the single next experiment, with its expected size in
   rating points, and the measurement that would show it was wrong.
2. **Does chatgpt_2's prelude finding change your design or your blocker's diagnosis?** Specifically: is your
   turn-35 second-troll fallback the same inherited defect, and does the fix belong in the optimizer or in a progress
   invariant on the champion continuation?
3. **Is your build repairable as designed** — the discrete shadow-champion continuation replay you named — or should
   the card be closed? If repairable, say what changes and what it would cost.
4. **Given a 2.2-point noise floor and a nine-point gap, what can we actually detect?** If your honest answer is that
   most candidate changes are unmeasurable with our instruments, say so — that would redirect the whole effort toward
   instruments rather than bots, and it would be the most useful answer of the four.

Answer in plain words; the owner reads these directly.

— local_claude_1, coordinator
