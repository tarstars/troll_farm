# 20260820-pair-selector-anti-benching — employ the benched troll (rule R-2)

- Status: OPEN — OWNER-CHARTERED 2026-08-20 at the 4a sitting ("We should fix
  it"), consequence of rule R-2 (`docs/RULES-LEDGER.md`). The 24-case
  GOAL_SPLIT class is the target: the team-picker's joint pairing discards a
  troll's oracle-verified available work, up to 194 turns per game.
- Record owner: local_claude_1 · Work owner: **claude_1** ·
  Reviewer: **codex_1** (instrument-first, then gates) ·
  Integrator: local_claude_1
- Base: **Phase 1 subject = cure-C `ad3bfefe…`, pinned NOW** (valid for both
  possible verdicts — the selection code is byte-identical in both night arms;
  step 0 verifies). **Phase 2 subject = whatever resident tonight's ruling
  settles**, rebased then; subjects are pinned per phase, never drift
  mid-phase.
- Priority: **UNBLOCKED BY OWNER 2026-08-20 ("This task shouldn't be
  blocked") — Phase 1 starts NOW.** The original subject-contingency was
  over-cautious: the Door-1 candidate's entire diff is one forecast hunk
  (record: r1 handoff + codex's "one pure-deletion hunk" verification); the
  pair-selector code is byte-identical in both bots of the running platform
  session, so the Phase-1 mechanism probe is valid regardless of tonight's
  verdict. Probe step 0 verifies that byte-identity explicitly. Only Phase 2
  (the fix build) waits for the settled resident. Sentinel build yields
  priority (it is an optimization since the launcher went live).
- Created UTC: 2026-08-20T08:35:54Z

## Phase 1 — WHY (evidence first; this touches the most sensitive code)

Parity-disciplined probe on the accepted toolkit: for a representative subset
of the 24 (at minimum OSC-017, OSC-013, OSC-034, OSC-004 — the four
owner-ruled), log per turn WHAT the joint pairing scored and WHY the
benched troll's candidates lost — which term of the pair score dominates,
whether the discard is a hard filter or a score preference, and whether the
winning pair's value is even positive. Unprivileged logging of the actual
selection arithmetic; no reimplemented scoring (one-scoring-path rule).
Deliverable: mechanism note + fix design PROPOSAL to the OWNER (design gate —
the picker is planner core; two-doors-wall applies).

## Phase 2 — the fix (after the owner's design go)

Per the approved design. Gate class per owner law: this is a
behavior-CHANGING candidate → **named-costs gate** (full decomposition both
directions, every de-novo game diagnosed and named, aggregate improvement,
codex package verdict) → **decided by its own M-1 platform session**, owner
rules KEEP/REVERT. Fixtures: the four ruled cases observed failing on the
unmodified subject, then employed under the candidate (turn-coverage metric).

## Boundaries

No Arena action within this task (sessions are the integrator's, serialized).
Resident byte-sacred. No relitigating R-2's scope — the rule is absolute by
owner ruling; only the MECHANISM of compliance is designable. All standing
transport rules (cards, deferrals, evidence gate, WIP) apply.

- Authority: owner rulings at the 4a sitting, 2026-08-20.
