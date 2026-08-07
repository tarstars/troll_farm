# 20260807-banana-disposition-review-chatgpt_1: keep/discard review of the whole banana effort

- Status: assigned — owner-directed 2026-08-07; runs **after** `20260807-gate-architecture-review`
- Record owner / integrator: `local_claude_1`
- Work owner (reviewer): `chatgpt_1`
- Paired independent review: `20260807-banana-disposition-review-local_codex_1` (same corpus,
  no contact between reviewers before both handoffs land)
- Area: retrospective disposition of the banana programme
- Base commit: `3bc4abc558d03d7e8768e535ec8dfdab6c48c2ee` (canonical `agent/local_claude_1`)
- Branch: `agent/chatgpt_1` (canonical — task branches cannot satisfy a v2 handoff)
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-07T10:05:00Z
- Last updated UTC: 2026-08-07T10:05:00Z

## Outcome

A document stating **what we should take from the recent banana work and what we should
discard**, covering every item in the shared corpus, with per-item verdicts and the two required
retrospective sections.

## Corpus, deliverable format, and verdict vocabulary

Defined once, identically for both reviewers, in
**`coordination/tasks/20260807-banana-work-disposition-corpus.md`**. Read it first. Do not edit
it; if you believe the corpus is missing an item, report that as a finding and include your
disposition of the missing item.

## Why two independent reviews

You and `local_codex_1` review the same corpus separately. Agreement is strong evidence;
disagreement localises exactly the items that need the integrator's attention. Do not coordinate
with the other reviewer, and do not read their handoff before publishing yours — if you see it
first, say so in your artifact.

## Conflict of interest — declare it, do not avoid it

You authored a substantial part of the corpus: the entire solve arm (`bbe54a48`, `7ad9d784`,
`build_candidate.py` and v2–v11), the corpus-D gate/contract layer, the CI workflows, the
earlier factory/ring lineage, and two of the review documents in corpus E. **Review them
anyway** — you know them best — but mark every such verdict `SELF-AUTHORED`. Those verdicts are
weighted against `local_codex_1`'s independent read of the same items, which is precisely why
the paired structure exists.

Judge your own work by the same evidence standard you applied to claude_1's design in your
round-3 review. A `DISCARD` on your own artifact is a valuable result, not a concession.

## Specific questions you are best placed to answer

1. The **v11 stability layer** turned 22 blocking games into 89. Was the layer's *idea* (a
   final-command stability pass over every lifecycle phase, forcing carriers onto DROP or a
   strictly door-closing MOVE) wrong in principle, or wrong in that implementation? This matters
   directly to the owner's strict rule, which now requires repairing inherited D-1/D-4.
2. Of the eleven `build_candidate*.py` generations, which arm is the best starting point under
   the strict rule, and why?
3. Your **terminal-D7 finite-trace analysis** (post-`C_T` referee state rather than command-text
   inference) — is it a correct observation that was misapplied as an exemption, and is it worth
   keeping as a detector-semantics fix referred to `local_codex_1`?
4. The **gate-contract-v1 policy** (inherited exemption set to false) survived claude_1's packet
   review as correct while its runner did not. Is the contract worth keeping independently of
   `run_stable_gate.py`?
5. Corpus F: does anything in the factory/ring lineage still carry value, or is it fully
   superseded?

## Prohibitions

No edit to any file in the corpus, to `trace_detectors.py`, `fuzz_panel.py`, any gate config,
any candidate source, any frozen artifact, another agent's namespace, or any task record other
than your own status/messages. No CI workflow may be created, restored, or modified anywhere in
this repository. No host run request, value protocol, TestSession, submission, restore, or Arena
action. Read-only against `data/`; do not open sealed ranges or the official holdout.

## Standing verifiability conditions

After the 2026-08-06 fabricated-verdict finding, every quantitative claim in this review must be
reproducible from committed inputs, with the exact command and the SHA-256 of every input
embedded in the artifact; no acceptance verdict may be attributed to another agent without the
exact message path; and the handoff must be v2-complete on canonical `agent/chatgpt_1` with
`artifact_commit`. These are about verifiability, not about discounting your technical
judgement — your m012 finding was correct and has been adopted, and your 22/240 reproduction was
honest and correct.

## Sequencing

Complete `20260807-gate-architecture-review` first, then claim this. If you judge the ordering
wrong, say so and propose the alternative rather than silently reordering.

## Deliverables

One handoff to `local_claude_1` on canonical `agent/chatgpt_1` carrying the disposition
document, a per-corpus-item verdict table, the lessons and dead-ends sections, and an explicit
list of items you marked `SELF-AUTHORED`.
