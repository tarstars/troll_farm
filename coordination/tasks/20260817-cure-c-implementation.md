# 20260817-cure-c-implementation: implement cure C, pass every gate, submit to the platform

- Status: OPEN — OWNER-CHARTERED 2026-08-17 in session ("I would propose implement C
  and post it on platform"; task written at owner direction as a single end-to-end
  goal for claude_1). This charter IS the owner's verdict on the no-goal branch of
  the oscillation session; the session's other branches (the 24 pairing-bench cases,
  the harmless-rulings, the OSC-031 chop residue) remain OPEN and unprejudiced.
- Code owner: `claude_1` (end-to-end driver: implementation → tests → panel →
  submission) · Reviewer: `codex_1` (implementation review + panel reproduction —
  both gate the submission) · Integrator/Arena bookkeeping: `local_claude_1`
- Base: the readable resident `98628e98…` (candidate build; the resident FILE stays
  byte-sacred until the owner's post-night KEEP ruling; the candidate is submitted
  as a NEW agent).

## THE GOAL (owner-set): the candidate is SUBMITTED on the platform after every gate
below is green. Not "ready to submit" — SUBMITTED, same working session as the last
green gate.

## 1. What to build — cure C, exactly per the corrected brief

`local_claude_1/session-inputs/cure-candidate-C-brief-2026-08-17.md` (corrected
2026-08-17). In one sentence: at the `:1189` fall-through, when NOT in true endgame,
a chopless troll gets the explicit mid-game chain — `idle_harvest_candidates` →
`bank_candidates` if carrying → **explicit WAIT tail** — and never enters the
endgame planner. Constraints, all binding:

- True-endgame routing (`endgame(view)`) untouched. The `:1185` full-capacity exit
  untouched. NOTHING else changes — no pairing-bench touch, no chop-side touch, no
  banana code, no opportunistic fixes however tempting.
- The chain is written out in full in the diff with its tail explicit — an
  undefined tail is how the next wall gets built (`docs/DISCOVERY-two-correct-
  doors-make-a-wall-2026-08-17.md`).

## 2. Pre-registration — BEFORE the first line of code

Freeze the accepted cross-tab (message `20260817T202500Z`) as the prediction
registry of this task:

- CURED completely: OSC-008 (7/7), OSC-028 (51/51), OSC-032 (110/110),
  OSC-033 (143/143) — 311 turns, plus 14 bonus turns on OSC-031/001 → 325 of 521.
- PREDICTED UNCURED: OSC-009 (endgame-branch), OSC-005 (:1185 door), OSC-031's
  167 fruitless-board turns (correct WAIT tail), OSC-001's endgame/occupancy turns.
- Ladder expectation, written in advance: **+0.2 to +0.7 points. Under the M-1
  materiality floor (1.0) an IMMATERIAL verdict is a possible HONEST outcome** and
  is not a failure of the task; nobody re-frames it afterwards.

## 3. Gates — every one fail-first, in this order

1. **G1 fixtures:** the four cure fixtures observed FAILING on the unmodified
   resident, then green under the candidate at exactly 311/311 turns; the predicted-
   uncured set observed behaving as predicted; **all 34 situations re-run: zero
   de-novo D-1, zero de-novo P4, no regressions anywhere.**
2. **G2 panel:** the 240-game panel vs the matched floor — **ZERO de-novo D-1 AND
   ZERO de-novo P4** (both arms), command errors 0, with the per-game decomposition
   published. Stall-game count reported against the floor's 27 (no causal claim).
3. **G3 performance:** warm p95 < 50 ms (per-turn probe, T-1 pattern); thread
   parity (1-proc == N-proc, row-identical).
4. **G4 review:** codex_1 reviews the implementation AND independently reproduces
   G1–G3 before any submission. REVISION_REQUIRED loops stay inside this task.
5. **G5 submission:** on G4 green — submit the candidate to the platform via the
   standing serialized path: hand the green handoff to `local_claude_1`, whose
   countersign-and-submit is COMMITTED same-session with no further approvals (the
   owner's go is THIS charter). Owner-directed exception: if the controller is
   unreachable for more than 6 hours after the green handoff, claude_1 submits
   directly under this charter and says so.

## 4. After submission (not claude_1's gate, recorded for completeness)

The paired candidate-vs-resident night runs under the M-1 rule (1.96·SE winner,
1.0 materiality floor, max two extensions); `local_claude_1` does the Arena
bookkeeping; **KEEP vs REVERT is the OWNER's ruling on the night's numbers.** The
resident file mutates only on an owner KEEP.

## 5. Boundaries

One change per night — the candidate carries C and nothing else. No spec/banana
implementation (separately gated). Causal claims about ladder effect only after the
night, only with the measurement attached. All standing transport rules apply
(WIP limit, evidence gate, verdict-equals-message, fail-first).

- Created: 2026-08-17 · Authority: owner charter in session with the integrator.
