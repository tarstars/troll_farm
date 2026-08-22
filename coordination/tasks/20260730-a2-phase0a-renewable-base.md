# 20260730-a2-phase0a-renewable-base: does a renewable resource base exist on these maps?

- Status: closed — verdict EXISTS (qualified); K1 does NOT fire; base is sub-critical and LABOR-limited; integrated
- Record owner: claude_1
- Work owner: claude_1
- Reviewer: chatgpt_1 (optional)
- Integrator: claude_1
- Area: A2 Phase 0a (= backlog N3); charter `docs/A2-programme-charter-2026-07-30.md`
- Base commit: ccc56454c89c246b597b7ceaf507e04b1af435fb
- Branch: session-2026-07-01 (integrator; executed by claude_1 subagent)
- Progress lease: 15 minutes; phase markers renew it
- Created UTC: 2026-07-30T05:13:21Z
- Last updated UTC: 2026-07-30T05:13:21Z

## Outcome
A verdict on whether a genuinely self-sustaining resource loop exists on these maps, with
the per-map ceiling on sustainable crop throughput and the earliest turn a fruit-funded
third worker is reachable. **This is kill rule K1: if no renewable base exists, the A2
design target is physically impossible and the programme stops.**

## Frozen protocol
None (read-only corpus audit). Charter §Phase 0 governs; CONSTRAINTS binding.

## Exclusive write set
- `cgauto/renewable_base_feasibility.py` (new); scratchpad report

## Do not touch
- `rust/src/bin/yamo_orchard_live.rs`; sealed ranges; `data/raw/games/`; the cron.

## Acceptance checks
- Distinguishes a self-sustaining loop from a larger/faster windfall, with the tree
  population's finiteness modelled explicitly (H1: worker 4 affordable 0/220).
- Reports the sustainable throughput ceiling per map class and the earliest fruit-funded
  worker-3 turn, with uncertainty.
- Verdict states EXISTS / DOES-NOT-EXIST / UNDETERMINED and what would settle the latter.
