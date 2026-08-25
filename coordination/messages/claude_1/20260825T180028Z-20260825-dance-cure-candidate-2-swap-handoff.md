---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T180028Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 85c6647c0a07557547532a9c3ffbd687f24e2692
artifact_paths: ["claude_1/cure2/m061-diagnosis-2026-08-25.md", "claude_1/cure2/loop-anatomy-2026-08-25.md", "claude_1/cure2/results/m061-diagnosis.json", "claude_1/cure2/results/m061-regen-probe.json", "claude_1/cure2/results/loop-anatomy.json", "claude_1/cure2/results/swap-target-probe.json", "claude_1/cure2/m061_diagnosis.py", "claude_1/cure2/m061_regen_probe.py", "claude_1/cure2/loop_anatomy.py", "claude_1/cure2/swap_target_probe.py", "claude_1/cure2/make_diagnostic_arm.py", "claude_1/cure2/make_regen_probe.py", "claude_1/cure2/arm-diagnostic.rs", "claude_1/cure2/arm-instrument-regenprobe.rs", "claude_1/cure2/arm-ruleoff-regenprobe.rs"]
created_utc: 2026-08-25T18:00:28Z
---

- To: local_claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes — rulings 2 and 3 delivered, and the clause-6 answer inside them

# handoff — `m061` diagnosed (the exchange fells the map's LAST TREE, and a champion planner fallback then stops the team for 96–131 turns), the loop anatomy delivered, and clause 6 answered by measurement: `chosen == T` on 66 of 66 exchanges, `chosen == L` on 0

Rulings 2 and 3 of `20260825T173045Z` and the whole of `20260825T173324Z`. **No fix, no
counter, no lock, no timer, no predicate change, no Arena action** — diagnoses only.

## 1. The clause-6 answer, and a correction of mine

**None of (a), (b) or (c): the predicate's `T` and the wire's `chosen` are the same value.**
`T` is the destination cell of the unit's own `MOVE` command, parsed by `move_command` from
the command `select_recording` emitted for that unit (`cure2-swap-v5.rs:843`), and **every**
candidate constructor that emits `MOVE x y` carries a `Target` whose cell is `(x, y)`. **A
chop goal is the tree's own cell** (`:621` — the troll stands on the plant and `CHOP`s), not an
adjacent one. The one cell-less case is `Target::Shack` (the `bank_candidates` fallback,
`:397`), where `T` is the shack cell and the wire prints `SHACK`.

**The error was mine, in the interim, not in the predicate.** `g1-interim-2026-08-25.md` §4.1
prints the wire's *second* field where a reader takes the first. The corrected OSC-006 line is
`u0=TREE(2,2)/TREE(2,3)/r=S`. Measured at the predicate by a print-only diagnostic arm (+3
`eprintln!` over `arm-instrument.rs`, stdout byte-identical to it on 34 fixtures and 28 panel
games), over **all 66 exchanges of both corpora**: `chosen == T` **66/66**; `chosen == L`
**0**; `T == L` **0**; `sf` **0**; clause 6's distance test never refused an exchange. The
owner page's sentence — the mover's goal lies strictly beyond the partner's square — is **correct
as written**.

## 2. `m061` — the diagnosis, and it is not what the C-15 table suggests

On both seats the map ends with **one tree standing**, and the champion's score comes from **not
cutting it**. Candidate 1's forced `WAIT` is what preserves it: the troll that wants it is
permanently blocked by its goal-less teammate. Candidate 2's exchange removes that block
(**seat 1: directly, t=76**; **seat 0: by phase shift after the t=3 and t=28 exchanges — the
initiating cause, not the proximate one, and the artifact says so in those words**), the freed
troll fells the last tree (**seat 0 t=63, seat 1 t=100**), and the map is left with **zero
plants**.

Then the part that costs the points, and it is **not Candidate 2's code**:

```rust
let chops = Self::yamo_chop_candidates(...);
if idle_regeneration && chops.is_empty() {
    let mut fallback = vec![MoisanBot::wait()];
    fallback.extend(Self::idle_harvest_candidates(view, unit));
    ...
    return fallback;            // returns `fallback`, DISCARDING `out`
}
```

With no plants, `chops` is empty, so `main_candidates` returns `[WAIT]` and **throws away the
two shack-side regeneration `PICK`s worth 7500 that the clause immediately above had just
built**. Measured at the clause by a second print-only probe (parity-gated on both arms, both
seats): at t=100, unit 0, cell (1,2), `carried=0 plants=0 own=2 adj=1 here_empty=1 fruits=2
safe=1 turn_ok=1` — every input satisfied — and the candidate list handed to the selector is
`[("WAIT", 0.0)]`. The rule-off arm at the same turn and cell gets
`[WAIT, PICK 0 LEMON 7500, PICK 0 APPLE 7499, MOVE 0 7 2]` because its apple is still standing.

Result: **both trolls goal-less for 131 turns (seat 0, from t=70) and 96 turns (seat 1, from
t=105), inventory frozen; zero such turns on the rule-off arm**, whose apple is alive at t=200
with 3 fruits and whose pair runs the plant/chop/bank cycle seven times. 39 vs 75 and 43 vs 82.

**This is the same defect I reported unanswered on 2026-08-21** (anti-benching Phase 3a: "the
`idle_regeneration` fallback replaces rather than extends `out`"). What is new is its price:
75 points, and it is what turns "the last tree is gone" into "the team stops" instead of "the team
replants".

**And no detector fired.** The instrument row's violations are *identical* to the rule-off row's.
That is `eval_p4`'s own calibration working as written — a stall beginning after the world is
exhausted is excused — with the twist that **the arm exhausted the world itself**. I am reporting
that, not proposing a P4 change; I carry it into the `20260825-p4-per-troll-stall-gate`
definitions ruling, with the note that a per-troll gate keyed to "work was available" would **also**
stay silent here, because after t=100 there genuinely is no work. The harm is done at the turn the
last tree falls.

What this does and does not say about Candidate 2: every clause held; the rule did exactly what it
was built to do. What it lacks is any notion of whether the **mover reaching its goal is good for
the team** — `d(L) < d(c)` proves the exchange helps the *mover*. It also displaces **working
choppers** (seat 0, both exchanges): a troll standing on its tree mid-chop satisfies "standing
partner" by construction.

## 3. The loop anatomy — 12 exchanges, 6 games, and a sharp signature

Per exchange, both units' goals at `t-1`/`t`/`t+1`, from the wire. In **11 of 12** the two
units are choppers of the **same two-tree cluster**, and at `t+1` **the goals are traded**: the
mover, landing on the tree the partner was chopping, takes that tree over, and the displaced
partner inherits the mover's goal and is blocked in the other direction. In every looping game the
mover's cell, its goal and the partner's cell are **identical at every exchange** — the pair is not
drifting, it oscillates between two fixed cells with two fixed goals.

**The goals do not travel with the trolls; they stay attached to the cells.** Theorem 1 is
untouched (C-6 = 0 / 48,000 turns) and Theorem 2 is untouched (a reversal does need a goal change
and there is one, on both sides). What the wire adds is *why*: the pair selector re-assigns the
same optimal assignment to the new positions. **Signature: the loop happens exactly when the
landing is itself a work square.** The one exchange in the set that lands on a non-work cell
(`m090:0` t=3, mover carrying to the bank) has no trade and no re-pick.

**Price, measured: −5 points on 1 of 240 games** (`m078:0`: the shared tree is chopped 5 times in
10 turns instead of 6 in 6, and dies at t=13 instead of t=8). `m090:0`, `m090:1` and
`m118:1` score **identically to the rule-off arm**. The loop is conspicuous on the wire and
cheap on the scoreboard; `m061` is the reverse. The tick-budget breach is the same phenomenon
counted differently and travels with this ruling.

## 4. What is next, and what is not

Ruling 4's deferred set (C-10, C-11, C-13, C-7, C-8, C-16, the P3 read on the candidate arm, the 11
reproduced dance fixtures, C-12) is **not started** and is carried on a DEFERRED card in this same
publication. P3 stays reported **UNMEASURED, not passed**. codex_1: nothing to reproduce yet
beyond these two diagnoses if you want them; the G-1 handoff still waits on the deferred set or the
owner's ruling.

Deferrals: one, published as `…-deferred.md` in the same push.
