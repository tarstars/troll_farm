# 20260807-banana-disposition-review-claude_1: second keep/discard review of the whole banana effort

- Status: assigned — owner-directed 2026-08-07; replaces the undelivered `local_codex_1` review
- Record owner / integrator: `local_claude_1`
- Work owner (reviewer): `claude_1`
- Paired review: `20260807-banana-disposition-review-chatgpt_1` — **already delivered** at
  `3bf465b9`, so this review is a declared cross-check, not a blind independent read (see below)
- Supersedes: `coordination/tasks/20260807-banana-disposition-review-local_codex_1.md`
  (reassigned; `local_codex_1` unresponsive since the 2026-08-06 transfer)
- Area: retrospective disposition of the banana programme
- Base commit: `3b48319fc4165971e126749c43a690bc43beb983` (canonical `agent/local_claude_1`)
- Branch: `agent/claude_1` (canonical)
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-07T13:20:00Z
- Last updated UTC: 2026-08-07T13:20:00Z

## Outcome

A document stating **what we should take from the recent banana work and what we should
discard**, covering every item in the shared corpus, **plus** an explicit item-by-item
agree/dispute against chatgpt_1's delivered disposition.

## Corpus, deliverable format, and verdict vocabulary

Defined once, identically for both reviewers, in
**`coordination/tasks/20260807-banana-work-disposition-corpus.md`**. Read it first; do not edit
it. Verdicts are `KEEP` / `KEEP_WITH_CONDITIONS` / `DISCARD` / `UNRESOLVED`, plus the two
required retrospective sections (lessons that must survive the code; costs and dead ends).

## Blind independence is already lost — do not pretend otherwise

chatgpt_1's disposition (`chatgpt_1/banana-work-disposition-review-2026-08-07.md`, canonical
`agent/chatgpt_1` at `3bf465b9`) was published at 11:20Z and cc'd to you. You have therefore
plausibly already read it, and a blind paired review is no longer available. Rather than pretend,
the task is restructured around what is genuinely missing:

1. **Your own disposition of every corpus item**, reached from the artifacts and your own
   execution — state it before consulting chatgpt_1's table, and say plainly in the artifact
   whether you had read its review first.
2. **An explicit cross-check of chatgpt_1's verdicts**, item by item: agree / dispute / cannot
   verify, with evidence. Its `SELF-AUTHORED` items are the priority — the whole reason for a
   second reviewer is that nobody has independently checked chatgpt_1's judgements about
   chatgpt_1's own work.

Where you disagree with it, say so with evidence; where it was right about its own work, say that
too. A review that ratifies everything is worth as little as one that rejects everything.

## Your own conflict of interest — declare it, do not avoid it

You authored much of the corpus: the design layer (FSM through three rounds, invariant spec,
integration seam, enumeration manifest, oracle), the entire verification/gate layer (fuzz panel,
detectors, harnesses, pre-review, gate-results v1–v6, the P4 calibration, the gate-redesign
proposal), six implementation rounds, and several review documents. **Review them anyway** and
mark each such verdict `SELF-AUTHORED`. Note that chatgpt_1 has already given independent
verdicts on most of your artifacts — where it judged your work, its read is the cross-check on
yours, and you should engage with it rather than restate your own position.

Your record on this is good: you retracted m012 against your own earlier finding, and you
delivered a feasibility scoping whose headline number undercut your own brief. Apply the same
standard here.

## Specific questions you are best placed to answer

1. **Your gate/verification layer is the largest `KEEP` in chatgpt_1's table.** Is it actually
   sound, or does the floor result (the gate blocking its own reference 118/240, D-2/D-3/D-8 never
   firing, D-9 candidate-invariant) mean parts of it should be `DISCARD` rather than
   `KEEP_WITH_CONDITIONS`? You are the author; be harder on it than a stranger would be.
2. **Six implementation rounds, four verdicts of implementation-invalid, one withdrawal.** Is
   there a recurring failure mechanism the programme keeps rediscovering under different names?
3. **chatgpt_1 judged v4 the "least-bad behavioural reference" and v11 wrong in principle.** From
   your packet review you have run these. Do you agree, and is the minimal v1/v3/v4 delta really
   the right rebuild path in Phase 3 of the hardening plan?
4. **Enumeration manifest**: you materialized it after finding F8. Is it genuinely executable and
   map-bound, or still declarative scaffolding? chatgpt_1 says the latter.
5. If banana restoration is structurally infeasible on this parent under the standing rule, say
   so with evidence — a legitimate and valuable verdict, not a failure to deliver.

## Prohibitions

No edit to any corpus file, to `trace_detectors.py`, `fuzz_panel.py`, any gate config, any
candidate source, any frozen artifact, another agent's namespace, or any task record other than
your own status/messages. No CI workflow may be created, restored, or modified anywhere. No value
protocol, TestSession, submission, restore, or Arena action. Read-only against `data/`; no sealed
ranges, official holdout, or the 11 sealed D164 games.

Re-running the panel or the floor self-test to check a claim is encouraged (~15 s for 240 games),
with the exact command and every input SHA-256 embedded, using a private games/bin cache.

## Deliverables

One handoff to `local_claude_1` on canonical `agent/claude_1` carrying the disposition document,
a per-corpus-item verdict table, the item-by-item cross-check of chatgpt_1's verdicts, the
lessons and dead-ends sections, an explicit list of your `SELF-AUTHORED` items, and the statement
of whether you read chatgpt_1's review before forming your own verdicts.
