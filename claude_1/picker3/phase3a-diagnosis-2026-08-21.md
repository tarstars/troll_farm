# Phase 3a — the anti-benching diagnosis: what P1's veto actually did

- Task `20260820-pair-selector-anti-benching`, Phase 3a (owner ruled D3 = **revise**).
- Author: claude_1 · Reviewer: codex_1 · Card:
  `coordination/messages/local_claude_1/20260821T103829Z-...-policy.md`
- **Diagnosis only.** Nothing here proposes, designs or builds a change. Where progress requires
  a design decision, the decision is named and handed back, not taken.

## Headline

The two named panel findings are **not the same kind of thing**, and the card's shorthand
("the `m004` P3 regression") reads them as if they were.

- **`m004` seat 0** — P1's veto fires on 4 turns (42–45) and each time the pair it leaves behind
  is still real work (`CHOP`, score 58.8–76.9). The candidate row carries **D-1 ×1 and no P4**;
  the floor row on the identical spec carries **D-1 ×2 and P4 over turns 42–200**. So on this
  game P1+P2 **removed a 159-turn stall the champion has** and halved its D-1 count. The only
  thing that got worse is byte-equality with the parent — which is exactly and only what P3
  measures. **Calling it a regression overstates it.**
- **`m021` seat 1** — P1's veto fires on 103 of 200 turns, and on **80 contiguous turns (20–99)**
  it removes the *highest-scoring* pair and the selector then picks a pair scoring **0.0: both
  units WAIT**. That is 80 turns of forced double-idle sitting inside the recorded P4 window
  20–106. The floor row on the identical spec has **neither the P4 nor the `r5-horizon` flag**.
  **This one is a real, quantified harm, and it is P1's own veto that produces it.**

Same clause, opposite signs, on two games in the same panel.

## Correction the card inherits, measured not assumed

Of the four named fixtures, **OSC-013 and OSC-017 reproduce on the champion; OSC-004 and OSC-034
do not.** Confirmed through the shared harness with the episode-identity gate enforced
(`claude_1/regrade2/regrade34-identity-2026-08-21.json`); OSC-034 was one of the eight rows once
graded FIXED and differs from its frozen window on 4 of 94 command lines. 3a therefore diagnoses
**013 and 017**, and reports 004 and 034 as `NOT_REPRODUCIBLE_ON_BASE` — no exhibit, not fixed,
not absent.

## Deliverable 1 — what the un-benched troll does instead of progressing

Delivered 2026-08-20 and unchanged; restated here so 3b has it in one place
(`claude_1/picker2/phase3-generator-route-2026-08-20.md`, `route-census-2026-08-20.json`).

On every idle turn of all four ruled fixtures, on both bases, the anchor's candidate list is
exactly **one** entry — the `WAIT` that `main_candidates` seeds it with — and it arrives there by
one route on **100%** of those turns: the `idle_regeneration && chops.is_empty()` fallback, which
returns a **fresh** `vec![MoisanBot::wait()]` rather than extending the `out` it has already
built. **The list is never empty. The residual stall is not a selector defect.**

**The collision, stated with its evidence, as the card required.** On OSC-013 that discard is not
harmless: on **101 of the 170** idle turns `out` already held **two real `PICK` candidates**
(target `Cell((2,1))`, scores 7500.0 / 7499.0) and the fallback threw them away. The 170 turns
are two spans, not one — turns 31–99 (69 turns) where the generator genuinely had nothing, and
turns 100–200 (101 turns) where it had those two `PICK`s. The split is exactly the
`view.turn >= 100` guard on the safe-regeneration replant block. Identical on both bases.

**Whether that fallback should extend `out` instead of replacing it is the owner's open
extend-versus-replace question, and 3a does not answer it.** It is not established that keeping
the two `PICK`s would restore progress: they would still have to be selected, be legal, and move
the unit out of the cycle, and the last of those is the grader's bar, not the generator's.

## Deliverable 2 — the `m004` P3: mechanism and turn

**Turn 42.** Panel record: `parent: MOVE 0 1 2;WAIT` vs `candidate: WAIT;CHOP 2`.

The probe rows for that turn, from the candidate's own selector:

| | unit 0 | unit 2 |
|---|---|---|
| idx 0 | `WAIT` — 0.0 | `WAIT` — 0.0 |
| idx 1 | `MOVE 0 12 2` → `Tree((12,2))` — **68.97** | `CHOP 2` → `Tree((12,2))` — **58.82** |

Four pairs are formed, and three are eliminated before scoring decides anything:

| pair | sum | outcome |
|---|---|---|
| (WAIT, WAIT) | 0.0 | survives, loses |
| (WAIT, `CHOP 2`) | 58.82 | survives — **and wins** |
| (`MOVE 0 12 2`, WAIT) | **68.97** | **`p1drop=true`** — vetoed by P1's `self_blocked` |
| (`MOVE 0 12 2`, `CHOP 2`) | 127.79 | `compat=false` — both claim `Tree((12,2))`, the **pre-existing** target rule, not P1 |

So the mechanism is exact: both units target the same tree; the target-compatibility rule (which
predates this work) kills the pair where they both act on it; P1 then kills the higher-scoring of
the two survivors because unit 2 is `WAIT`ing on the cell unit 0's `MOVE` steps into; and the
selector takes the only thing left, `WAIT;CHOP 2`. The parent, with no P1, takes the vetoed pair
— emitted as the single step `MOVE 0 1 2` on its way to (12,2), which is why the panel's parent
string looks like a different destination. Verified directly: the parent walks `MOVE 0 1 2`,
`MOVE 0 2 2`, `MOVE 0 3 2`, `MOVE 0 4 2` on turns 42–45 while the candidate chops.

**The veto fires on 10 turns and changes the winner on 4 (42–45). On none of them is the
replacement all-WAIT.** After turn 45 the two streams have diverged into different worlds — 159
of 200 turns differ — so no later turn is attributable to a single veto and none is claimed.

**What P3 is measuring here.** P3 asserts the candidate's command stream is byte-equal to the
parent's on orchard-eligible seat views. P1+P2 is by design a command change, so P3 is
structurally reachable by any real selector edit that touches such a view; the cure-C arm's 12 of
12 is luck, not principle. **Whether P3 is applicable to an intentional selector change remains a
ruling, and it is not mine.** What 3a adds is that on this game the byte change accompanies the
removal of the champion's own 159-turn P4 stall — so a rule that blocks on P3 here blocks an
improvement.

## Deliverable 3 — the `m021` P4 / `r5-horizon`: mechanism and cost

Panel record, **identical on both bases** (`panel-door1-cand.json` and `panel-cureC-cand.json`):
new property **P4**, window **20–106** — *"no own-inventory/own-cargo progress over turns 20–106
while work remains through turn 106"* — plus flag **`r5-horizon`** on unit 2: *"full wood carrier
since turn 12 never DROPs at a door within the bounded banking horizon of 30 turns"*. The floor
row on the identical spec has **neither**; both arms block anyway on a shared D-4 (turns 15–17).

The mechanism, from turn 20 onward and unchanged for 80 turns:

| | unit 0 | unit 2 |
|---|---|---|
| idx 0 | `WAIT` — 0.0 | `WAIT` — 0.0 |
| idx 1 | `MOVE 0 5 2` → `Tree((5,2))` — **57.14** | *(nothing — the generator produces no second candidate)* |

Two pairs exist. `(WAIT, WAIT)` scores 0.0. `(MOVE 0 5 2, WAIT)` scores 57.14 and is
**`p1drop=true`** — vetoed, because unit 2 is `WAIT`ing on unit 0's next step. **The selector is
then left with nothing but the zero-scoring double-WAIT, and takes it.**

**The cost, counted:**

| | `m021` s1 | `m004` s0 |
|---|---|---|
| turns P1 vetoed a pair | 103 / 200 | 10 / 200 |
| turns the veto **changed the winner** | **80** | 4 |
| … inside the recorded window | 80 (window 20–106) | 4 (window 42–200) |
| … where the selected pair then scored **0.0 — both units WAIT** | **80** | **0** |
| turns the veto removed an already-losing pair (inert) | 23 | 6 |
| contiguous causal run | **20–99** | 42–45 |

80 forced double-WAIT turns, contiguous, opening one turn after the P4 window opens and running
to within 7 turns of its close. Unit 2's own emptiness is the generator's doing, not P1's — but
the pair that would have had unit 0 walking to a tree existed on all 80 turns and P1 removed it
every time.

**Stated as a limit:** "the floor does not have this P4" is a fact about the floor row on the
identical spec. It is not a counterfactual claim that removing the veto would restore progress —
that needs a run of a changed selector, which is 3b/3c's business and is deliberately not done
here.

## What this hands to 3b, as questions

1. **P1's veto has no fallback.** On `m021` it removes the last productive pair and the selector
   has nowhere to go but double-WAIT. Whether the veto should be conditional on a
   strictly-better alternative existing — rather than absolute — is a **design decision for the
   owner and codex_1's pre-build ruling**, and I am not answering it by building something.
2. **The `idle_regeneration` fallback replaces rather than extends `out`** (the OSC-013
   collision, 101/170). Same status: the owner's open question, still open.
3. **P3's applicability to an intentional selector change** is still an unruled question, and
   `m004` now shows it can fire on a change that removes a stall.

## Gates — each fails the run rather than degrading it

1. **Parity.** The instrumented binary's command stream is byte-identical to the uninstrumented
   candidate's on each spec. The probe only prints. Enforced in `panel_game_probe.py`; a
   mismatch raises rather than reports.
2. **Row identity.** The regenerated spec's `violations` and `flags` must equal the Phase-2
   panel's recorded row for that (map, seat). Both matched — `m004` s0 and `m021` s1 — which is
   what licenses every turn number above as being about *those* games and not a lookalike.
3. **Turn coverage.** 200 `PS2TURN` rows per game, turns 1–200, no gaps.
4. **Causal-veto discipline.** A veto is counted as a cost only when the vetoed pair outscored
   **every** surviving compatible / stock-compatible pair. Vetoes that removed an already-losing
   pair are counted separately (23 and 6) and excluded from the cost, because counting them
   would inflate it.
5. **Parent control.** The parent's own turn-42–45 stream was read directly rather than inferred
   from the panel's summary string, which is how the `MOVE 0 12 2` / `MOVE 0 1 2` apparent
   mismatch was resolved as a destination-versus-step artefact instead of being written up as a
   discrepancy.

## Instruments — reused, not rebuilt

`claude_1/picker2/make_probe.py`'s selector probe (`PS2PAIR … p1drop=<b> waits=<n>`) is the
accepted instrument and is unmodified; `probe-door1-p1p2.rs` is its already-built output. The
Phase-2 battery `run_gates.py` is untouched — codex_1 reproduced that package and 3a does not
perturb a reproduced artifact. `route_census.py`'s fixture harness cannot reach panel games, so
`panel_game_probe.py` reuses the panel's **own** `fuzz_panel.build_jobs` / `make_referee` /
`run_pair` to regenerate exactly the two specs, rather than writing a second panel.

## Replay

    python3 claude_1/picker3/panel_game_probe.py 2> claude_1/picker3/probe-stderr.log
    python3 claude_1/picker3/analyze_p1_drops.py

## Artifacts

- `claude_1/picker3/panel_game_probe.py`, `panel-game-probe-2026-08-21.json` — the two specs,
  parity and row-identity gates
- `claude_1/picker3/analyze_p1_drops.py`, `p1-drop-analysis-2026-08-21.json` — the veto counts
- `claude_1/picker3/probe-stderr.log` — the raw selector rows both of the above read
- Carried forward unchanged: `claude_1/picker2/phase3-generator-route-2026-08-20.md`,
  `route-census-2026-08-20.json`, `idle-shape-2026-08-20.json`

## Out of scope, and not claimed

No candidate was changed, built or run against a candidate selector. No Arena action. No claim
that removing or conditioning P1's veto restores progress anywhere. No claim about the 235
non-deadlock benched turns, about fixtures outside the four ruled ones, or about any panel game
other than the two named. Nothing priced.
