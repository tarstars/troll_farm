# The banana farm as the next item — coordinator's assessment for the owner (2026-08-26)

Written at the owner's request ("next item is to try banana farm — what do you think about it?"),
from the repo's own record, gathered this session. Plain words; every code explained at first use.

## What the record says, in six lines

1. **Bananas are the game's cheapest crop.** Cooldown 6 ticks (2 near water) against 8–9 for the
   others; training a troll on bananas costs nothing; a banana tree has health 5–6 against 8+3·size
   for an apple — so it is cheap to grow and **cheap for the enemy to chop**. Each fruit banked = 1
   point; a planted tree scores nothing by itself; a banana planted at size 0 needs ≈ 30 turns
   before its first fruit (`docs/mechanics.md`, the CBF spec §5).
2. **The only mechanism in this project that ever produced a large local signal is the banana
   seed-factory D89a (July 21):** mean paired margin **+79 points** (confidence interval +41 to
   +118), own score +162, on 256 local games. Nothing else in the register is within a factor of
   ten of that (`docs/CONSTRAINTS.md:99-103`).
3. **It also failed hardest on the real ladder.** The live "banana factory b100" trial (Aug 2):
   **12.99, rank 127/131**, against the parent's 23.3 / rank 32 — 49 wins, 49 losses, 22 % of games
   catastrophic (`coordination/tasks/20260802-owner-banana-factory-b100-arena.md`). The local
   panel was wrong about this idea by ~10 ladder points.
4. **Why it failed is not measured.** The panel showed the *opponent's* score rising by +83 too.
   Whether they stole our bananas or just farmed beside us was never split out — the repo marks it
   UNRESOLVED (CBF spec §2). The b100 tail cause is "not established".
5. **The implementation history is the worst in the project:** Banana R2 went six rounds without
   reaching a value panel (replant-before-bank, growth-blind oracle, 225 no-progress turns, 141/240
   games blocked …); its state machine has 10 persisted states and 6 coupling channels; the
   disposition is "no further implementation until the gate can reach ACCEPT"
   (`docs/CONSTRAINTS.md:114-145`, `claude_1/banana-restoration-r2/`).
6. **The reference #3-Legend bot does not farm.** yann-moisan plants only in the endgame for extra
   points and had a "sweet spot" planting rule that was implemented and **disabled**
   (`docs/reference/2026-07-11-yannbot-design.md:50-54`). Specs A (unconditional) and B
   (conditional on the opponent's third troll) were owner-approved 2026-08-17 v12, implementation
   gated on an explicit owner go. Standing owner rule since 08-10: **no banana action before the
   second troll is trained** (detector D-9a).

## My opinion

**It is the right kind of bet and the wrong kind of history.** Against the score goal (≥ 25.40,
+2.5–3.6 points away), the farm is the only lever on the register whose measured effect is on the
scale of the gap — the dance/stall line, by contrast, has a ceiling of ≈ 1.4 points and an
unestablished cost. So *if* one more score attempt is to be made, this is the one worth making.

But three things must be different from last time, or it will end the same way:

1. **Ask the ladder's question before writing bot code.** The +79 was measured against the local
   opponent pool; real Legend opponents took the farm apart (12.99). Two cheap reads settle whether
   the idea can work at all:
   - **Do the top Legend bots farm?** The corpus has 21,496 games; the 25 agents that reach ranks
     7–54 on our exact two-worker roster are in it. Count mid-game banana PLANTs per game for them.
     If none of them farms, the farm is not the road to 25.4 and we should know that for the price
     of a script.
   - **Who ate the b100 farm?** The b100 games are in the corpus. Split the opponent's banked
     bananas into "from our trees" and "from their own" per game. That is the UNRESOLVED number
     from CBF §2, and it decides whether a farm is defensible against real opponents or only
     feeds them.
2. **Build the smallest farm, not the FSM.** Spec B (conditional) with the CBF's three latched
   states (deny → farm → wood, one abort sensor) — not the 10-state machine — on the readable
   source, delivered as a diff file like Candidate 3. This is also the only version consistent with
   the owner's second goal, control over the code and its cleanliness: a farm the owner cannot read
   is a farm the owner does not control. Implementation-validity gates first (the six-round
   lesson): byte-identity before the first transition, no-progress and blocking counts, the D-9a
   rule, before any value number is looked at.
3. **Measure on the ladder, not the panel.** The panel lied by ten points on this exact idea. Use
   the self-replacement block (8 reads, standard error ≈ 0.5) against the champion's own reads; a
   panel result is a go/no-go for the submission, never the verdict.

**What I would not do:** start from Spec A (unconditional) — the b100 trial *was* effectively an
unconditional farm; or restart Banana R2's FSM branch; or let a +79-style panel number authorize
anything but one ladder block.

## Cost and order

The two corpus reads (item 1) are a day of one bot (claude_1 or codex_1), no coordinator rulings
needed beyond the charter. They can start now, in parallel with Candidate 3's bounded finish, and
their answers decide whether the farm charter is written at all. If both reads say "yes" (top bots
farm; the b100 farm fed the opponent mainly through theft, which a conditional abort can watch),
the build is a bounded charter of the Candidate 3 shape: G-0 once, one review, one build, one
validity panel, one ladder block, the diff on `main`, then stop.

Nothing is chartered by this page. The owner's word starts it.
