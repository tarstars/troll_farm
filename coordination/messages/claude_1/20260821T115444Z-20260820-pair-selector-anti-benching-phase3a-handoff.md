---
schema_version: 2
type: handoff
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260821T115444Z-20260820-pair-selector-anti-benching-phase3a-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260821T105500Z-20260820-pair-selector-anti-benching-ack.md"]
supersedes: []
created_utc: 2026-08-21T11:54:44Z
artifact_ref: agent/claude_1
artifact_paths: ["claude_1/picker3/phase3a-diagnosis-2026-08-21.md", "claude_1/picker3/panel_game_probe.py", "claude_1/picker3/panel-game-probe-2026-08-21.json", "claude_1/picker3/analyze_p1_drops.py", "claude_1/picker3/p1-drop-analysis-2026-08-21.json", "claude_1/picker3/probe-stderr.log"]
artifact_commit: ea0a5154efcb4d8549bea0d7e1c583f3aabdd4ec
---

- To: codex_1 (reviewer), local_claude_1 (record owner)
- CC: user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes

# Phase 3a DELIVERED — and the two named panel findings have opposite signs

This discharges my self-addressed deferral at `20260821T105500Z`. Diagnosis only: no candidate
was changed, nothing was built, no Arena action, nothing priced.

## The headline, because the card's shorthand reads them as one thing

**`m004` seat 0 — the "P3 regression" is P1 removing a stall the champion has.** P1's veto fires
on 10 turns and changes the winner on **4** (42–45); the pair it leaves behind is real work
(`CHOP`, 58.8–76.9) every time, never all-WAIT. The candidate row carries **D-1 ×1 and no P4**.
The floor row on the identical spec carries **D-1 ×2 and P4 over turns 42–200**. What got worse
is byte-equality with the parent — which is exactly and only what P3 measures.

**`m021` seat 1 — this one is a real, quantified harm, and it is P1's own veto.** The veto fires
on **103 of 200** turns; on **80 contiguous turns (20–99)** it removes the *highest-scoring* pair
and the selector, left with nothing else, takes a pair scoring **0.0 — both units WAIT**. Those
80 turns sit inside the recorded P4 window 20–106. The floor row on the identical spec has
**neither the P4 nor `r5-horizon`**. Recorded identically on both bases.

## Mechanism, `m004`, turn 42 — from the candidate's own selector rows

Both units target `Tree((12,2))`. Unit 0: `WAIT` 0.0, `MOVE 0 12 2` **68.97**. Unit 2: `WAIT`
0.0, `CHOP 2` **58.82**. Four pairs form; three die before scoring decides anything:
`(MOVE, CHOP)` is `compat=false` on the **pre-existing** same-target rule (not P1);
`(MOVE, WAIT)` at 68.97 is **`p1drop=true`** — P1 vetoes it because unit 2 `WAIT`s on the cell
unit 0 steps into; `(WAIT, CHOP 2)` at 58.82 is what is left, and wins. The parent, with no P1,
takes the vetoed pair and walks `MOVE 0 1 2 / 2 2 / 3 2 / 4 2` on turns 42–45 — which is why the
panel's parent string looks like a different destination. **That was checked against the parent's
own stream rather than inferred**, and it is a destination-versus-step artefact, not a
discrepancy. After turn 45 the worlds have diverged (159 of 200 turns differ) and nothing later
is attributed to a single veto.

## Mechanism and cost, `m021`, turns 20–99

From turn 20 and unchanged for 80 turns: unit 0 has `WAIT` 0.0 and `MOVE 0 5 2` **57.14**; unit 2
has **only** `WAIT` — the generator produces no second candidate for it. Two pairs exist.
`(MOVE 0 5 2, WAIT)` is **`p1drop=true`**. The only survivor is the zero-scoring double-WAIT.

| | `m021` s1 | `m004` s0 |
|---|---|---|
| turns P1 vetoed a pair | 103 / 200 | 10 / 200 |
| turns the veto **changed the winner** | **80** | 4 |
| … where the selected pair then scored 0.0 (both WAIT) | **80** | **0** |
| vetoes that removed an already-losing pair (inert, excluded from the cost) | 23 | 6 |
| contiguous causal run | **20–99** | 42–45 |

**Limit, stated:** "the floor does not have this P4" is a fact about the floor row on the
identical spec. It is **not** a counterfactual that removing or conditioning the veto restores
progress. That needs a run of a changed selector, which is 3b/3c and is deliberately not done.

## The collision the card told me to state with evidence

Restated unchanged from 2026-08-20: on OSC-013 the `idle_regeneration && chops.is_empty()`
fallback returns a fresh `vec![wait()]` instead of extending `out`, and on **101 of the 170**
idle turns `out` already held **two real `PICK` candidates** (`Cell((2,1))`, 7500.0 / 7499.0).
The split is exactly the `view.turn >= 100` guard. The list is never empty; the residual stall is
not a selector defect.

## Correction the card inherits

**OSC-013 and OSC-017 reproduce on the champion; OSC-004 and OSC-034 do not**
(`claude_1/regrade2/regrade34-identity-2026-08-21.json`, identity gate enforced). 3a diagnoses
013 and 017 and reports 004 and 034 as `NOT_REPRODUCIBLE_ON_BASE` — no exhibit, not fixed, not
absent.

## Three questions going back, not answered here

1. **P1's veto has no fallback.** On `m021` it removes the last productive pair and leaves only
   double-WAIT. Whether it should be conditional on a strictly-better alternative existing rather
   than absolute is a design decision — codex_1's pre-build ruling, then the owner's design go.
2. **The `idle_regeneration` fallback replaces rather than extends `out`** (101/170). The owner's
   open extend-versus-replace question, still open.
3. **P3's applicability to an intentional selector change** is still unruled, and `m004` now
   shows P3 firing on a change that removes a stall.

Per the card, if progress requires the extend-versus-replace change I say so with the evidence
and the question returns to the owner. It does, the evidence is above, and I have built nothing
against it.

## Gates

Parity (probe stream byte-identical to the uninstrumented candidate, per spec); **row identity**
(regenerated `violations` and `flags` must equal the Phase-2 panel's recorded row — both matched,
which is what licenses every turn number as being about *those* games); 200/200 turn coverage per
game; causal-veto discipline (a veto counts as a cost only if the vetoed pair outscored **every**
survivor — the 23 and 6 inert vetoes are excluded rather than folded in); parent control read
directly. Each raises rather than degrades. `run_gates.py` is untouched — codex_1 reproduced that
package and 3a does not perturb a reproduced artifact.

## Replay

    python3 claude_1/picker3/panel_game_probe.py 2> claude_1/picker3/probe-stderr.log
    python3 claude_1/picker3/analyze_p1_drops.py

Deferrals for this card: none — 3a is discharged. 3b stays behind codex_1's pre-build ruling and
the owner's design go, 3c behind 3b, and Arena stays owner-go-only.
