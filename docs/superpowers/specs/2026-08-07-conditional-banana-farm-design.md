# Conditional banana farm with banana-collection abort — design

- Date: 2026-08-07
- Owner-specified; designed by `local_claude_1`
- Task record (to be created): `coordination/tasks/20260807-conditional-banana-farm.md`
- D-series id: to be assigned when the frozen protocol is written; not used here
- Base: resident `rust/src/bin/yamo_orchard_live.rs`, SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`
- Farm mechanism source: `data/analysis/live-agent-6553250/d89a-banana-seed-factory-blueprint-2026-07-21.md`

## 1. Owner specification

A bot that:

1. collects resources for and trains a second troll;
2. denies one of lemon/plum;
3. starts a self-sustaining banana orchard after that denial;
4. falls back to chopping everything if the enemy harvests our bananas faster than we do.

Acceptance is **behavioural**: the bot passes when it demonstrably does these four things.

## 2. Why this shape, and what it is built against

D89a (`banana_seed_factory`, 2026-07-21) is the only banana mechanism this project has built
that worked at scale: activation 256/256, 1,344 bank bananas planted, a sustained harvest and
replant loop in 252/256, mean paired margin **+79.441** CI [+40.991, +117.892], catastrophes
26 → 11. It was rejected on four of fifteen value gates — worst opponent-family −6.938 (bar −5),
p10 margin −72 (bar −20), worst pair −235 (bar −60), and opponent-score delta +82.863 (bar +1).
The last of those is superseded by the owner's 2026-08-07 delta ruling: judge on margin, not on
absolute opponent gain.

The tail is the real defect, and its cause is documented: of the opponent's +82.863, only
**+12.453** came from crops of ours they took; **+76.508** came from their *own* created crops.
The farm did not leak by theft — it freed the opponent to complete their own reproductive loop
while our starter tended a private orchard. The worst cell (map 9,914,047, seat 0, Gold adaptive)
had our score rise 163 and theirs rise 398.

This design does not try to fix that leak. It bounds exposure to it instead: farm only in games
we are already losing, and stop as soon as the farm is observably feeding the opponent.

## 3. Architecture — a three-state machine with no reversible transition

One persistent state on the bot. Two transitions, both latched.

```
DENY ──(opponent_trolls > 2)──► FARM ──(banana-collection test fails)──► WOOD
```

There is no path back and no direct DENY → WOOD edge.

**DENY** — today's resident behaviour, unmodified. The denial bonus at
`yamo_orchard_live.rs:1101-1105` is live: `score = 1000*wood/turns`, plus
`900/(1 + manhattan(tree, opponent_shack))` for the focus species while `opponent_trolls <= 2`.

**FARM** — the D89a seed factory. The starter plants banked bananas, protects one bank-sourced
seed reserve from our own chopping, harvests ripe tracked own bananas, and replants each
harvested banana in a reachable empty conversion cell. The trained worker keeps the resident's
wood/logistics specification. Carrying wood, iron, or non-banana fruit continues to take
precedence and uses resident bank logistics.

**WOOD** — pure wood maximisation. No denial bonus, no planting. This is already what the
resident degenerates into once `opponent_trolls > 2`, so WOOD is not new behaviour; it is the
current fallback, reached by a different route.

### 3.0 The denial bonus follows the machine, not the live count

Today the denial bonus is gated inline on `opponent_trolls <= 2`, recomputed every turn from the
board. Once the machine leaves DENY the bonus must be **permanently off, independent of that live
count** — otherwise an opponent who loses a troll and drops back to two would silently re-enable
denial while we are in FARM or WOOD. That would break monotonicity at the behavioural level even
though the state machine itself never reverses, and reintroduce exactly the A → B → A pattern the
latching exists to prevent. The gate therefore becomes `state == DENY`, and `state == DENY`
requires `opponent_trolls <= 2` has always held.

### 3.1 Why the transitions are latched

Latching is the whole anti-oscillation argument, and it is structural rather than tuned: an
A → B → A loop is unrepresentable. This matters because oscillation is closed permanently in
`CONSTRAINTS.md` — D176a solved it almost perfectly (long-run task rate 8.50% → 2.88%, below
yamo's 2.9% reference, zero de-novo oscillation, all six value gates passing) and was still
worth only +0.045 margin. We get the property by construction and claim no value for it.

### 3.2 The blast radius is bounded by construction

If the opponent never reaches three trolls, the machine never leaves DENY and the bot is
**byte-identical** to the current resident. The change can only act in games where the opponent
has already out-scaled us — the population the B3.1 audit identified, where opponent scaling
precedes our collapse by 42–125 turns in 84% of catastrophes (83% of catastrophic mass). This
is a testable invariant, not an aspiration: see G5.

## 4. Sensors

Both are read directly from state the referee already sends. The bot receives **both** players'
inventories (`GameState::inventories: [Stock; 2]`, populated by `for inv in &mut inventories`),
so nothing here requires chop attribution or plant-lifecycle inference — the layer where Banana
R2 rounds 1–6 failed.

**DENY → FARM.** `view.units.iter().filter(|u| u.player == 1).count() > 2`, the same expression
already used at `:1066`. First observation latches; the count dropping back to 2 does not revert.

**FARM → WOOD.** On entering FARM, snapshot `(turn, inventories[0][BANANA], inventories[1][BANANA])`.
Thereafter let `d_us` and `d_them` be the increases in each side's banked banana since that
snapshot. Abort when `d_them > d_us` holds for `K` consecutive turns, and only after `W` turns
in FARM.

`BANANA` is index 3. It costs zero toward TRAIN (`docs/mechanics.md`: "BANANA and WOOD cost
zero"), so the opponent has no training incentive to farm bananas of their own; a rise in their
banked banana is therefore a sound proxy for harvesting from our orchard. This is the owner's
stated rule — "if the enemy harvests our bananas more than we do, fall back" — expressed in
directly observable quantities.

A farm that produces nothing also aborts, since `d_them > d_us` holds when `d_us` is zero and
the opponent collects anything at all. That is intended.

## 5. Frozen constants

Chosen by reasoning and frozen before any run. `CONSTRAINTS.md` records that N6's one permitted
denial-weight sweep failed both arms; we should not expect to sweep our way out of a bad
constant, so these are not tuning dials.

| Constant | Value | Justification |
|---|---:|---|
| `W` (warmup turns in FARM) | 30 | A banana planted at size 0 needs four growth steps at base cooldown 6 to reach size 4, then one further cooldown to fruit. 30 turns is one "time to first banana"; aborting sooner would kill the farm before it could pay. |
| `K` (consecutive turns) | 5 | Insurance against a single-turn spike. Cheap, and the transition is one-way, so a spurious abort is unrecoverable within the game. |
| `T` (deficit threshold) | 0 | Strict inequality. The warmup and persistence requirement carry the noise rejection; a third tunable would add surface without evidence. |

## 6. Acceptance gates — behavioural, per the owner

| Gate | Statement | Measurement |
|---|---|---|
| G1 | Trains a second troll | `TRAIN` issued and own unit count reaches 2 |
| G2 | Denies one of lemon/plum | A focus species is selected and frozen; chops of that species occur while `opponent_trolls <= 2`, preferentially near the opponent shack |
| G3 | Starts a self-sustaining banana orchard | FARM entered; bananas planted; a harvest→replant cycle completes at least once |
| G4 | Falls back on the banana test | The abort fires in games where `d_them > d_us` persists, and does **not** fire in games where it does not |
| G5 | Bounded blast radius | In games where the opponent never exceeds two trolls, emitted commands are byte-identical to the resident |
| G6 | Monotonicity | No state transition ever reverses, over the whole panel, and the denial bonus never re-enables after DENY is left (§3.0) |

G1 and G2 are satisfied by the current resident, so they are "do not break what works" gates and
are largely covered by G5. The new work is G3 and G4.

G4 requires both arms — firing and not firing. A rule that always fires is not conditional, and a
rule that never fires is not a rule. This is the project's mandated trigger-fidelity check, which
must run **before** any panel; it saved D174a and caught D173a.

### 6.1 Boundary: these gates deliver a bot, not a promotion

Behavioural gates establish that the bot is built correctly. They are not evidence of value, and
this project has been burned repeatedly by conflating the two — opportunistic mining delivered its
mechanism at 100% trigger fidelity and scored −10.76; B3.13 passed five compiled boundaries, exact
teacher-forced replay and eight smokes, then scored 11.96 at rank 111/113 live; D176a reached 100%
fidelity and failed at mechanism.

Arena submission therefore remains governed by the standing authorization in `docs/STATE.md` §3,
which requires a `QUALIFIED` verdict from a frozen protocol and expected gain above the ±0.5–1
noise band. Passing G1–G6 authorizes no Arena action. The value measurement is a separate,
later, frozen step.

### 6.2 The value question this design is built to answer, when we get there

D89a's mean was never the problem. If the abort works, **the tail improves**: p10 and worst-case
margin move materially toward their bars (−20 and −60) relative to D89a's −72 and −235 on
comparable maps, without giving back the whole +79.4 mean. If the mean improves and the tail does
not, the design has failed at the only thing it was built for.

## 7. Testing strategy

Built and tested in three independently verifiable stages.

**Stage 1 — the machine, with no farm.** DENY and WOOD only, with FARM as a pass-through to
WOOD. Unit tests for monotonicity (G6) and byte-identity on non-triggering games (G5). This
stage should produce a bot that is behaviourally indistinguishable from the resident everywhere,
which is a strong and cheap check that the plumbing is inert.

**Stage 2 — graft the farm.** D89a's blueprint into the FARM state. Trigger fidelity for G3.

**Stage 3 — the abort.** Snapshot, warmup, persistence, latch. Trigger fidelity for G4, both arms.

Development panel and confirmation maps follow the standing protocol; sealed ranges
(`9,844,200–215`, the official holdout, the 11 sealed D164 games, `9,852,000–063`,
`9,857,000–127`) stay closed.

## 8. Out of scope

No change to the denial bonus magnitude — N6 closed it ("keep 900; do not retry zero"). No
attempt to deny the opponent's training bills — H4 closed that (`NO_MATERIAL_DENIABLE_BILL`,
strict blockable rate 0.0 over 17 catastrophes; 43 of 73 mandatory batches are IRON, which
chopping cannot touch). No repair of D89a's opponent-production leak; this design bounds exposure
to it rather than fixing it, and the separate scoping task
`20260807-d89a-leak-repairability-scoping` remains the place that question is answered. No Arena
action. No formatter over `rust/src/bin/` or `cgauto/`. The resident source stays byte-exact.

## 9. Known risks

**The abort watches the minor term.** Theft was +12.453 of D89a's +82.863 leak; the dominant
+76.508 was the opponent's own production. A farm can therefore pass the banana-collection test
and still lose the way D89a lost. The owner specified this sensor after that decomposition was
presented. A margin-based abort (snapshot `view.scores`, abort when their score grows faster)
watches the dominant term at identical implementation cost and remains available as a variant if
G4 passes but the tail does not improve.

**Late farm start may not compound.** D89a began at worker-2 materialization; here FARM begins
when the opponent reaches three trolls, typically much later. There may be too few turns left for
the loop to establish. G3 will show this directly, and a failure to establish is a real result.

**The proxy is not exact.** An opponent who plants their own bananas inflates `d_them` and causes
an early abort. Rare, since banana buys no training, but real; it biases toward aborting, which is
the safe direction.

**Bank exhaustion.** The resident already spends banked bananas on its own shack-ring orchard
(`:1193`). Whether enough remain at FARM entry is unmeasured and is the first thing Stage 2
should report.
