# 20260807-historical-artifact-curation: rethink old artifacts and place them into the evidence schema

- Status: queued — blocked on evidence schema v2 landing; owner-directed 2026-08-07
- Record owner / integrator: `local_claude_1`
- Work owner: unassigned (assign after schema v2 is merged and green)
- Reviewer: unassigned (must not be the work owner)
- Area: decision-evidence index / institutional memory
- Blocked by: the evidence schema v2 + hypothesis-tier feature
  (`docs/superpowers/specs/2026-08-07-evidence-index-hardening-design.md`)
- Base commit: to be set at claim time
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-07T17:00:00Z
- Last updated UTC: 2026-08-07T17:00:00Z

## Why this is a separate task

The schema/tooling work builds the container. This task fills it, and filling it is not
transcription — it requires deciding what each historical artifact actually established, whether
that conclusion still holds today, and what it is evidence *for*. That is judgement work with a
different skill profile and a different failure mode, so it gets its own record, its own owner,
and its own review.

**The motivating failure:** D89a `banana_seed_factory` (2026-07-21) is a *working* banana
mechanism — 256/256 activation, mean paired margin +79.441, rejected only on a safety gate — and
eight subsequent implementation attempts across roughly a week never cited it. Nothing was lost;
it simply was not where anyone looks. This task exists so that stops happening.

## Outcome

A prioritised, reviewed set of evidence records covering the historical artifacts that still carry
decision weight, plus an explicit list of artifacts deliberately **not** recorded and why.

## Scope of the corpus

Roughly 141 candidate decision points: ~124 D-series identifiers referenced in
`docs/CONSTRAINTS.md` and ~17 H-series, against 11 existing records (~8% coverage). Supporting
sources: `docs/BACKLOG.md` (56 KB), `docs/CONSTRAINTS.md` (94 KB), `docs/LEDGER-MAP.md` (978
lines), `docs/APPROACH-REGISTER-2026-07-30.md`, `docs/D-series-atlas.pdf`, `docs/archive/INDEX.md`.

**Do not attempt all 141.** Coverage is not the goal; retrievability of what matters is.

## Method — required

1. **Triage first, author second.** Produce the prioritised list and get it reviewed *before*
   authoring records. Rank by: does a current or plausible near-future decision depend on this?
2. **Rethink, do not transcribe.** For each artifact, state what it established, on what
   population, and whether that conclusion still holds. An artifact whose conclusion has been
   overtaken is worth recording precisely *because* it is stale — with the supersession explicit.
3. **Flag three categories loudly**, because these are the ones that cost us:
   - measured, working results nobody is currently citing (the D89a class);
   - artifacts that **contradict** a currently held belief;
   - conclusions whose premise has since failed (`void-premise` is a first-class status).
4. **Use git-pinned coordinates.** Every claim cites `commit` + `path` + `lines`, per schema v2.
   Pin to a commit reachable from `main`.
5. **Batch and review.** Author in batches of no more than five records; each batch is reviewed
   before the next begins. A wrong record is worse than a missing one — it is a false citation
   that future work will trust.

## Deliverables

- a triage document: the prioritised list, with explicit exclusions and reasons;
- evidence records for the accepted priorities, validator-green;
- a short report on the three flagged categories above, routed to the owner.

## Prohibitions

No edit to `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, or any other canonical document — this task
*cites* them, it does not rewrite them. No hand-editing of anything under
`docs/evidence/generated/`. No implementation, candidate, gate, detector, host, value,
TestSession, submission, or Arena action. No CI anywhere.

## Acceptance

- validator green on every authored record, with commit-pinned citations;
- every record reviewed by an agent other than its author;
- the exclusion list is explicit — "not recorded" must be a decision, not an omission.
