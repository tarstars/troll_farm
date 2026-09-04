# Task 20260904-champion-prefix-orchard — does a small orchard near the tent beat the champion's own continuation?

- **Born:** 2026-09-04 13:2xZ, on the owner's word **"run it"** after reading chatgpt_1's four-question judgement
  (`chatgpt_1/judgement/2026-09-04-what-next-after-optimizer-blocker.md`, pin `4c1cc683…`). Chartered 2026-09-04
  16:5xZ by the coordinator. **The authorisation is the owner's; the shape below is chatgpt_1's design, unchanged.**
- **Work owner:** **chatgpt_1** — end to end: the experiment, the machinery, the numbers, the report.
- **Independent reproducer:** **claude_1** — a *second, separately written* implementation of the same measurement,
  chartered when chatgpt_1's result lands (§7). Not a reviewer: a re-measurer.
- **Verifier:** the coordinator, by execution.
- **Kind:** **one offline simulation experiment. No ladder, no platform, no Arena, no panel, no holdout, no cluster.**
- **Budget:** one implementation round, one measurement, **three days, to 2026-09-07 17:00Z.**

---

## 1. The experiment in the owner's own words

Take the champion of record **unchanged**. Let it play its own opening until the moment it trains its own second
troll — about game turn 9. From there, try **one** different thing: **plant a small orchard near the tent, tend it,
and fell it for wood**. **Never train a third troll.** Then replay both that candidate and the champion — advanced
continuously, as itself — to turn 300 against the same opponents on the same maps, and compare the final score
margins.

In chatgpt_1's notation:

```text
A (baseline):  unchanged champion ────────────────────────────────────────► turn 300
B (candidate): unchanged champion through its own second TRAIN
               → searched near-orchard macros
               → continuously advanced shadow champion ────────────────────► turn 300
```

**The branch point is after the champion's own second troll is trained.** Everything before it is byte-identical to
the champion, on both arms. `NO_PLANT` is always legal — the search may decline to plant at all. The third troll is
disabled in this experiment, deliberately and without argument.

## 2. Why the shape is exactly this, and why it is not negotiable

Three consecutive builds died of **one architectural disease**, identified by chatgpt_2, verified by the coordinator
and confirmed independently by chatgpt_1 (`coordination/HANDOVER-2026-09-04-orchard-turn.md` §3):

> **An irreversible roster change was handed to a champion continuation that had never been validated for that
> roster, with no progress invariant.**

Stage 2A, chatgpt_2's three-troll start and chatgpt_1's own optimizer build all show it. chatgpt_2's five stalled maps
are a strict subset of its control's nine (5 of 5 checked), and on those maps both arms record the same second troll,
no third troll and the same final score — **the stalls were inherited from the shared prelude, not created by the
optimizer.**

**Keeping the prefix byte-identical through the champion's own second `TRAIN` is what makes this experiment immune to
that disease.** It is the whole reason for the design. Any deviation — an earlier second troll, a different talent, a
delayed train, a "small" prelude — reintroduces the exact failure mode that killed the last three builds and
invalidates the measurement. This is a **dead condition**, not a preference (§5.1, §5.2).

**The standing rule this card enforces, for every future build too:** *no irreversible action may replace the champion
unless the complete alternative continuation has already beaten it.* A progress deadline on macros is a secondary
safety belt and cannot undo a bad commitment.

## 3. Done means

An artifact under `chatgpt_1/champion-prefix-orchard/` containing, in plain words with the numbers beside them:

1. **The paired result.** Mean paired final-score **margin** difference (candidate minus champion) with its **95 %
   interval and n**, over the common map-seats; and **paired own score** with its interval, as a mandatory guard.
   Margin is the selector — Δwin was retired as a kill criterion on 2026-09-04 (§6).
2. **The policy the search actually chose**, stated as a rule a human can read: when planting starts, how many trees,
   which species, how far from the shack, when tending stops and felling begins — and **how often it chose
   `NO_PLANT`**, per map and overall.
3. **The published action vocabulary** — every action the search could take, listed. (Standing requirement since
   2026-09-04: both previous optimizers turned out to have no `PLANT` in their action space at all, which was the real
   explanation of two failures.)
4. **Mechanics before value, on both arms independently.** Neither arm's value number may be read until both run
   clean: candidate and baseline identical before the branch on every case, all 300 turns answered, telemetry clean,
   and any long-inactivity alarm explained. (The harness's `stalled` field is a **longest no-command streak** — not a
   crash, not a referee end condition and **not a loss label**. It is a valid fail-closed mechanics gate and nothing
   more.)
5. **The raid check.** The result recomputed under the high-raid scenario. Raids run **0.19 per 100 tree-turns before
   turn 100 and 0.6–1.0 after**; a late orchard is raidable and that is a real cost, not a rounding term.
6. **Wood calibration.** Exact replay must show no wood overstatement above the already-adopted **1.5×** bound.
7. **A straight recommendation:** does this mechanism deserve a further card, and does it deserve a ladder slot? By
   chatgpt_1's own warning, **a mean paired margin below about +15 does not deserve a ladder slot** even if real.
8. **A handoff** naming the pin, and the board row updated in the same commit.

## 4. What the experiment is given for free — do not re-derive these

All verified against `sim/engine.py` or on 400 map-seats. Sources: the orchard-kinetics read (claude_1, closed into
this card, §7), chatgpt_2's supplement, the coordinator's checks.

**Mechanics**

- **A mature size-4 tree is 16 points, not 4** (`WOOD_POINTS` 4; felling yields `plant.size`).
- **Health at maturity differs by species, all yielding the same 4 wood: banana 6, plum 12, lemon 12, apple 20**
  (`TREE_HEALTH_BASE` 2/4/4/8, `TREE_HEALTH_SLOPE` 1/2/2/3). So a chop-1 troll fells a **banana in 6 turns against an
  apple's 20 — 3.3× the wood per chop-turn** — and the referee prices bananas at **zero** for the training bill.
  **Banana is therefore the first ordering choice for a wood orchard**; plums, lemons and apples stay for the bill.
  No bot of ours has ever done this. The search may examine all species, but must price them separately.
- **First fruit:** plum and lemon ~12 turns beside water against 32 inland; apple 8 against 36; banana 16 against 24.
  A full tree regrows one fruit the instant it is harvested — that is what makes "tend" a real phase.
- The referee's chop loop is commented **"last wood can duplicate"**: with several choppers on one tree the final wood
  unit can be issued more than once. A multi-chopper schedule must respect it.

**Geometry** (claude_1, 400 map-seats, `claude_1/orchard-kinetics/results/curve.json`)

| within | free cells (median) | q1 / q3 | of which water-adjacent (median) |
|---|---|---|---|
| 2 steps | **11.5** | 9 / 14 | **2.0** |
| 4 steps | **27.0** | 21 / 34 | **5.0** |
| 8 steps | — | — | 13.0 |

Starting fruit draw: median **24**. **The fast orchard is small and the big orchard is slow** — that tension, not the
tree count, is the subject. A thirty-tree orchard is not reachable close to the tent.

**Economics already measured** (chatgpt_1's read, in its judgement)

- At turn 108 the median game still holds 24 wild wood, but the surviving trees sit at **median door-distance 13**;
  **no wild tree remains within four steps from turn 75 onward.**
- A chop-3 carry-4 worker earns about **0.5 points per worker-turn at distance 13**; a **near mature banana converts
  at 3.2**, and the full plant→grow→fell chain at about **1.73**.
- **Planting does not beat a nearby standing wild tree.** The orchard is a **near reserve for after the near forest is
  gone** — not a free value engine. That is the mechanism under test.
- The champion already plants 9.8 trees a game and fells 81 % of its banked plums and lemons; the top four plant ~29
  and their own trees overtake wild ones by turn 40–70.

**And one standing prohibition:** **never model the opponent as idle.** That assumption is what made stage 2A promise
turn 70 and deliver 74.5 into a stripped forest.

## 5. Dead means — chatgpt_1's own falsification list, adopted verbatim as the card's dead conditions

Any one of these ends the orchard-optimizer line. They were written by the work owner **before** the experiment ran,
and the coordinator holds them.

1. **The optimizer-off path differs from the champion**, before or after the branch.
2. **The champion's second troll changes** in talent or training turn on any case.
3. **The paired final-margin lower 95 % bound is not above zero.**
4. **The paired own-score lower bound is negative.**
5. **The no-plant champion is selected on most maps.**
6. **The gain disappears under the high-raid scenario.**
7. **Exact replay shows wood overstatement above the 1.5× bound.**

**And the soft stop:** a positive result whose mean paired margin is **below about +15** is recorded as a measured
component and **does not buy a ladder slot**. That is the work owner's own bar and the coordinator agrees with it.

## 6. What this card must NOT do

- **No ladder hour, no submission, no platform, no Arena, no cluster.** If the result earns a ladder slot, that is a
  separate decision with the owner's prediction asked in chat first.
- **No third troll.** The roster question is closed four independent ways (stage 2A at game turn 74.5 → 14.59;
  chatgpt_2's three-troll start at turn 25 → 14.07; the wood-charging gate declining all 4,593 evaluated turns; the
  cheap-third-troll read dead on paper). **It must not be re-litigated inside this card.**
- **No early or altered second troll**, for the reason in §2.
- **No new panel and no fresh sealed holdout yet.** The 24-map smoke and the pinned 200-map panel are **development
  data** — every build since August has been shaped against them. Generalisation is tested *after* a positive
  mechanism, on a sealed holdout, not now.
- **No Δwin.** Δwin is retired as a kill criterion everywhere. **Δmargin with its 95 % interval is the selector**, and
  the margin-to-rating relation is **flat then falling**, not linear — no rating number may be derived from a margin
  by a slope.
- **No rating claim from one ladder reading.** The ladder is not a 2.2-point wall; **2.2 is what one reading buys.**
  Paired half-width = 1.96 · sd · √(2/n) with sd 0.815: n = 1 gives ±2.26, n = 6 gives ±1.00, n = 21 gives ±0.50.

## 7. The two cards this one absorbs, and the reproduction

- **`20260904-orchard-kinetics.md` (claude_1's read) is CLOSED AS SUPERSEDED by this card**, not killed. It asked the
  right question and its delivered geometry is an input here (§4). Its remaining questions — the wood curve, the value
  of a planting turn against a chopping turn — are answered *by this experiment*, by exact paired replay rather than
  by a separate model. Running both would be two half-measurements of one thing.
- **`20260904-start-game-optimizer-build.md` is already CLOSED** (2026-09-04 13:1xZ) on its own pre-registered 24/24
  mechanics condition, at 19/24, reproduced to the digit. Its **design is preserved and is not falsified**; this card
  is its architectural successor.
- **claude_1 is reassigned to reproduce this experiment independently when chatgpt_1's result lands.** Two separately
  written implementations of one measurement is exactly what made the stage-2A field reading trustworthy — both
  agents agreed to the digit. claude_1 must **not** read chatgpt_1's implementation before writing its own; it gets
  the card, the referee and the pinned inputs. Its charter is a separate card at that moment.

## 8. The work owner's prior, recorded before the result

**About +2.5 rating, range 0 to +4, explicitly uncalibrated** — a planning prior, not a conversion from local score to
ladder rating. Expected local size: **roughly 10 to 25 points of final own-score or margin gain per game on maps where
the near reserve is used.** Recorded here so the result can be read against what was believed beforehand.

The coordinator's own position, on the record: this is the first orchard experiment with a **named mechanism** (worker
productivity from ~0.5 to ~1.7 points per turn after the near wild forest disappears) rather than a hope about
planting, and the first built so that the champion's opening cannot be damaged by it. That is why it is worth the
budget. It is also the case that the previous orchard bots were retired on readings that could not resolve them —
orchard 6 read 18.84 against the champion's 18.19 — so nothing in the record refutes an orchard; it only fails to
support the ones we built.

## 9. Cost, so the budget is honest

Four opponent archetypes × two seeds = eight continuations per candidate plan. The champion side is **cached per
branch state**, not rerun per plan. Re-ranking eight retained plans is therefore ~64 candidate continuations plus the
cached baselines per map. That is appropriate offline. **Online feasibility is unproved and must not be inferred**
from the Rust anytime planner's 378 ms benchmark — full paired continuations and scenario replay are different work,
and the release source already stands at 77,043 units against a 100,000-character limit.

## Log

- 2026-09-04 13:2xZ the owner: **"run it"** — the experiment authorised. — owner
- 2026-09-04 16:5xZ chartered to chatgpt_1 with its own falsification list as the dead conditions; the orchard-kinetics
  read closed into it as superseded with its geometry kept as an input; claude_1 named as the independent reproducer
  at delivery. — coordinator
