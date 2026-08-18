# 20260818-osc031-chop-clause-instrument — 4c: make the chop planner say its "no" out loud

- Status: **CLOSED 2026-08-18T15:36Z — OWNER RULED "A DEFECT."** All gates
  passed (G-4c.1 instrument r3; G-4c.2 controls+proofs r5; G-4c.3 evidence r2;
  brief r2 accepted-for-delivery and delivered). Measured attribution final:
  315/315 evaluations over the pinned 167 turns terminate at
  `PREDICT_TREE_NONE`. Ruling record:
  `local_claude_1/adjudications/OSC-031-ruling-2026-08-18.md`. Successor task:
  `coordination/tasks/20260818-osc031-forecast-defect-fix.md`. OSC-031 exits
  the 4b stamp list. Prior: OPEN — OWNER-CHARTERED 2026-08-18 in session ("put it in action" on the
  4c brief). Canonical brief:
  `local_claude_1/session-inputs/leftovers-4a-4b-4c-2026-08-18.md` §4c; residue
  named-unresolved at `claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md`.
- Record owner: local_claude_1 · Work owner: **claude_1** (instrument) ·
  Reviewer: **codex_1** (instrument-first) · Integrator: local_claude_1
- Area: oscillation verdict session residue, branch **4c** (iteration pool #6)
- Base: diagnostic COPY of the readable resident `98628e98…` (the resident file,
  the dev copy, and the live Arena are untouched; no candidate, no submission —
  the cure-C paired night runs in parallel and this task must not touch it)
- Created UTC: 2026-08-18T06:59:16Z

## THE QUESTION (owner's, plain words)

In recorded case OSC-031 a chop-capable troll, with trees on the board and no
fruit to pick, asked "should I chop?" every turn for 167 turns and answered no
to every tree every time. WHICH test inside the chop checklist says no? Nobody
knows; guessing was refused (unvalidated tree-math replicas lie; "a named open
item beats a fourth cause claim"). This task makes the bot answer out loud.

## THE GOAL

The rejecting clause NAMES ITSELF from the real bot's own execution: a
parity-disciplined instrument logs, for the OSC-031 fixture, EVERY clause
verdict the chop planner reaches, per tree, per turn, across the full 167-turn
window. Deliverable = the named clause (or clauses, with per-turn distribution)
+ an owner brief in plain words. **NO fix. NO judgment** — bug-vs-correct-caution
is the OWNER's ruling afterward, and nothing in the deliverable may pre-empt it
(smuggled-verdict discipline: attributions and measurements only, neutral
wording).

## What to build

1. Instrumented diagnostic build in the standing h-starve-1 style
   (`claude_1/hstarve1/make_instrumented*.py` + `audit.py` shared runner —
   REUSE the shared runner or prove parity with explicit controls; never
   re-implement the loop).
2. Taps log the chop planner's clause-by-clause evaluation for every candidate
   tree: **all clauses, unprivileged.** The standing suspicion — the
   tree-prediction math (`predict_tree`/`chop_outcome`) — stays recorded as an
   UNTESTED hypothesis and must not shape what gets logged; capacity/time
   clauses are logged even though "unlikely".
3. The log must reflect what the real bot EXECUTES (the pool-2 taps lesson:
   logged = executed, no tap sited where a later pass rewrites the decision).

## Gates (fail-first, in order)

1. **G-4c.1 instrument review:** codex_1 reviews the instrument BEFORE any
   result is treated as a finding (instrument-first; self-audit is not the
   gate). Verdict is not delivered until its message is published.
2. **G-4c.2 parity + both-ways controls:**
   - Parity: the instrumented build is row-identical to the uninstrumented
     resident copy on the OSC-031 fixture AND on at least one positive-control
     fixture, same discipline as `claude_1/hstarve1/parity-all34-2026-08-17.json`
     (all-34 parity welcome if cheap; the two named fixtures are the gate).
   - Observed firing both ways: on the positive control the log shows ACCEPT
     rows with clause outcomes (a fixture/window where the planner does choose a
     chop); on OSC-031 it shows REJECT rows with **exact turn coverage of the
     167-turn window** (turn coverage is the standing metric).
     **[AMENDED 2026-08-18T07:12:39Z, record owner — see Amendment 1 below: the
     coverage population is defined structurally, not by the 167 constant.]**
3. **G-4c.3 the finding:** clause-decision table (JSON + short md), the named
   rejecting clause(s) with per-turn/per-tree distribution, delivered as a
   message with the evidence attached; then the OWNER brief in plain words.

## Explicitly OUT of scope

- Any behavior change, however obvious the clause looks. Any harm/benefit
  judgment. Any class-wide claim ("this happens in other games") — that is a
  possible FOLLOW-UP the owner may charter after ruling; this task measures one
  game. Any Arena action (the M-1 night owns the Arena tonight; controller =
  local_claude_1 only). Any touch of the byte-sacred resident file or dev copy;
  no formatters over hash-locked sources.

## Amendment 1 — coverage population defined structurally (record owner, 2026-08-18T07:12:39Z)

claude_1's instrument handoff (`20260818T070706Z`) measured 190 in-window /
198 whole-game turns of chop evaluation across TWO units, and correctly refused
to reconcile that against this charter's "167-turn window" by adjusting
anything. The reconciliation is the record owner's, from the sources:

- **167** (pool 5, `claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md` §4) =
  the PARKED unit's CHOP-only `NO_GOAL_ASSIGNED` turns (167 of 189; the residue
  as priced in the 521-turn reconciliation: 325+28+1+167).
- **190/198** (instrument, subject-derived) = every turn on which
  `chop_candidates` executed for either unit (units 0 and 2), in-window/whole
  game.

Both are correct about different populations; the charter's constant borrowed
the residue LABEL for a coverage BOUND, which was wrong-scoped. The gate is
restated STRONGER, structurally:

- **G-4c.2 coverage (restated):** the log covers EVERY turn on which the chop
  planner executed for any audited unit in the fixture, with per-tree clause
  verdicts — no gaps, subject-derived, no constant to match.
- **G-4c.3 reconciliation (new mandatory deliverable):** the finding exhibits
  the historical 167 residue turns as a NAMED SUBSET of the logged turns with
  their own clause distribution, so the pool-5 record and this measurement
  join without either being rewritten.

The per-tap question claude_1 raised (five taps never observed firing) is
review scope as they requested: **codex_1 specifies or approves the controls**
(synthetic states allowed); for any clause left unfired, the review records
either an observed firing or a reviewer-verified structural argument why the
clause cannot fire in the audited class — defaulting fail-closed to demanding
the firing. "Every observed rejection was X" and "no other clause rejected"
remain distinct claims until then.

**MANIFEST PINNED (record owner, 2026-08-18T08:28:01Z):** the G-4c.3 named
subset is `claude_1/chop4c/osc031-167-manifest.json`, sha256
`b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5`, at artifact
commit `20e713aa5e9d9e1eb00a2a5180f1dc0a88de535c` — derived under the pinned
rule (`local_claude_1/chop4c/167-manifest-derivation-pin-2026-08-18.md`; count
167 exactly, STOP rule did not fire; decomposition 190 − 1 GOAL_SPLIT − 22
non-CHOP-only), independently reproduced byte-identically by codex_1
(`codex_1/reviews/osc031-167-manifest-reproduction-2026-08-18.md`). This file
and only this file satisfies the named-subset deliverable.

## After the gates

The owner looks at the named clause and rules: **bug → fix charter** (separate
task, full gates) or **correct caution → harmless stamp** (feeds 4b). The
ruling can join the 4a viewer sitting or stand alone, at the owner's leisure.

- Authority: owner charter in session with the integrator, 2026-08-18.
