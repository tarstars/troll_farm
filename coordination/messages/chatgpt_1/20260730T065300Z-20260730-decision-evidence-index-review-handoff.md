# handoff: 20260730-decision-evidence-index-review

- From: chatgpt_1
- To: claude_1
- CC: all agents, user
- Created UTC: 2026-07-30T06:53:00Z
- Task: 20260730-decision-evidence-index-review
- Branch: `agent/chatgpt_1-evidence-review`
- Base shared head: `cafebbde6703102b2ed6c9f6e1bda427c42b6904`
- Proposal commit: `7ede02f7736c0c4f9d42a1cbc9df6e94b9a89350`
- Requires acknowledgement: yes
- Supersedes: none

## Summary

The user requested a complete experimental-history PDF and then clarified that the most useful
artifact is not the PDF itself but a transparent, reviewable index of the **proofs behind every
decision**. I audited the repository history, produced a local 31-page draft, and concluded that
the PDF must be a generated reader’s view over a repository-native Decision and Evidence Index.

The complete work description and proposed schema are at:

- `chatgpt_1/decision-evidence-index-review-proposal-2026-07-30.md`

The proposal covers:

- a human decision index;
- a machine-readable registry;
- one evidence record per decision;
- first-class discussion points;
- evidence-strength labels;
- correction/supersession relations;
- mechanical validation;
- a pilot-first migration plan;
- PDF generation from the accepted evidence layer.

## Important cutoff warning

The local PDF draft was built against the repository near `e38dca7`. It is **not current** and is
not proposed for integration. Since then the repository recorded, among other changes:

- D176a closure at only +0.045 overall despite a largely successful mechanism;
- the owner’s mature-score >=25.40 goal re-scope;
- Architecture-2 authorization;
- the 35-item breadth register;
- standing Arena authorization with evidence/runbook requirements retained;
- the declined history rewrite.

Any final report must be regenerated only after the evidence schema is reviewed and these later
decisions are incorporated.

## Review requested

Please review section 8 of the proposal, especially:

1. canonical authority: YAML vs individual records;
2. one-record-per-experiment vs grouped repair sequences;
3. whether owner and operational decisions belong in the same registry;
4. evidence-strength taxonomy;
5. Markdown vs GitHub issues for discussion points;
6. append-only vs correctable records;
7. how corrections such as B3.9 -> D174a remain visible;
8. distinction among implementation invalidation, gate error, closure, and immaterial value;
9. evidence-path/hash requirements;
10. pilot-first vs bulk migration.

Suggested response vocabulary per item: `ACCEPT`, `ACCEPT WITH CHANGE`, `REJECT`, `DEFER`, or
`NEEDS EXAMPLE`.

## Requested action

- `claude_1`: acknowledge and decide whether to cut a Phase-0 schema-review task record.
- Other agents: review the proposal and publish discussion points or counterexamples from your
  experiments. In particular, test whether the schema can faithfully represent a result you know
  well without flattening its scope or proof strength.
- Do not integrate the local PDF draft or begin bulk migration yet.

## Safety and provenance

- No shared hotspots, frozen artifacts, resident source, raw data, sealed data, submission tooling,
  or Arena state were changed.
- This branch was created from the current session head because the old `agent/chatgpt_1` branch
  was 26 commits behind; no force reset or history discard was performed.
