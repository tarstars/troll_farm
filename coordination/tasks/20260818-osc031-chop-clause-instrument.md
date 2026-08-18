# 20260818-osc031-chop-clause-instrument — 4c: make the chop planner say its "no" out loud

- Status: OPEN — OWNER-CHARTERED 2026-08-18 in session ("put it in action" on the
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

## After the gates

The owner looks at the named clause and rules: **bug → fix charter** (separate
task, full gates) or **correct caution → harmless stamp** (feeds 4b). The
ruling can join the 4a viewer sitting or stand alone, at the owner's leisure.

- Authority: owner charter in session with the integrator, 2026-08-18.
