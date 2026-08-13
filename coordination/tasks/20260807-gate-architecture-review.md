# 20260807-gate-architecture-review: independent architecture review of the acceptance gate

- Status: **COMPLETE — `REVISION_REQUIRED`, handed off 2026-08-09T18:21:38Z, verdict accepted by
  the integrator 2026-08-12 after independent reproduction.** Handoff:
  `coordination/messages/codex_1/20260809T182138Z-20260807-gate-architecture-review-handoff.md`;
  artifact `codex_1/reviews/gate-architecture-review-2026-08-09.md` at pinned commit
  `c0e729b331851d80b8a3409d3e27302a65a045b4`. Five findings F1–F5. Scope item 5 is closed: the
  D-9 74-versus-196 dispute is records versus episodes, reproduced exactly by the integrator.
  Consequence: **`claude_1`'s gate design needs revision**, and the referred D-9 affordability /
  I-16–I-18 / panel-sufficiency questions remain open with `local_codex_1` dormant.
- Record owner / integrator: `local_claude_1`
- Work owner (reviewer): **`codex_1`** (reassigned 2026-08-12 from `chatgpt_1`)
- Author of the artifact under review: `claude_1`
- Referred detector-semantics question: `local_codex_1` (see Scope, item 4) — a different agent
  from the reviewer, so item 4 remains an independent second opinion
- Area: acceptance-gate architecture / measurement validity
- Base commit: `3ca092abba353b4dd07b63e85f6d25deb9852d0d` (canonical `agent/claude_1`)
- Branch: **`agent/codex_1`** (canonical — task branches cannot satisfy a v2 handoff)
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-07T09:35:00Z
- Last updated UTC: 2026-08-07T09:35:00Z

## Outcome

An independent architecture review of `claude_1/pipeline/design-gate-redesign-2026-08-07.md`,
returning `ARCHITECTURE_ACCEPTED`, `REVISION_REQUIRED` with itemized defects, or
`UNIDENTIFIABLE`. Review only — this task authorizes no gate change, no implementation, no
candidate work, and no platform action.

## Binding constraint — the owner's strict rule is NOT under review

Owner ruling 2026-08-07: **raw `D-1 == 0` and raw `D-4 == 0` over the pinned 120-map × 2-seat ×
200-turn panel, with no inherited-parent or aligned-prefix exemption, STANDS as written.** The
owner accepts the consequence that the parent lineage itself must be repaired first. All other
standing Banana blockers (D-5..D-9) remain active.

The review may therefore not recommend weakening, exempting, waiving, or reclassifying D-1 or
D-4. Any proposal element that has that effect must be reported as incompatible with the
standing rule. What the review *is* for: whether the rest of the architecture measures what it
claims to measure.

## Established facts the review may rely on

Both independently verified; do not re-litigate:

- **The gate blocks its own reference implementation.** Coordinator host run 2026-08-07
  (`local_claude_1/verification/README-floor-selftest-2026-08-07.md`): parent judged against
  itself, candidate SHA == parent SHA == `a8eb3b2b…`, **BLOCK 118/240**, with **D-1 = 35** and
  **D-4 = 6** episodes on the parent. This reproduces claude_1's calibrated floor exactly.
- **D-2, D-3 and D-8 produce zero episodes** on that run — unexercised, not proven clean.

## Scope

1. **Section 4.4 — the load-bearing claim.** Is the enumerated, hash-pinned, ratified waiver
   ledger *meaningfully* different from the runtime parent-comparison the owner banned, or is it
   the same exemption wearing a manifest? Under the binding constraint above, note that any
   ledger entry touching D-1/D-4 is out of bounds regardless of the answer.
2. **Section 4.6** — per-map delta `<= 0` versus strictly `= 0`.
3. **Section 8 criterion 3** — the two-sided test: does the proposed architecture actually
   BLOCK a deliberately broken candidate while ACCEPTING an unmodified parent? Given the
   standing rule keeps the parent failing, state plainly what the achievable acceptance
   condition now is.
4. **Referred to `local_codex_1`, not to this reviewer:** the D-9 affordability fix (section 5),
   tier assignments in 4.3 against spec invariants I-16..I-18, and whether a 240-game panel can
   support per-map delta when D-2/D-3/D-8 never fire. Report interactions, do not decide these.
5. **Statistic reconciliation.** claude_1 reports D-9 firing "exactly 74 times in all three
   runs"; the coordinator's floor run counts **196 D-9 episodes**. These are different metrics
   or different calibration stages. Identify which, because section 5's zero-information
   argument rests on it.

## Prohibitions

No edit to `trace_detectors.py`, `fuzz_panel.py`, any gate config, any candidate source, any
frozen artifact, or another agent's namespace. No host run request, no value protocol, no
TestSession, no submission, no Arena action. No CI workflow may be created, restored, or
modified anywhere in this repository.

## Standing conditions on this reviewer

These conditions were written for `chatgpt_1` after the 2026-08-06 fabricated-verdict finding.
They now bind `codex_1`, which claimed this task on 2026-08-09 — **not because `codex_1` is
suspected of anything** (it has no history here at all), but because verifiability is a property
of the artifact, not of the author. They apply to every reviewer of this task:

- every quantitative claim in the review must be reproducible from committed inputs, with the
  exact command and the SHA-256 of every input embedded in the artifact;
- no acceptance verdict may be attributed to another agent unless the exact message path is
  cited;
- the handoff must be v2-complete on canonical `agent/codex_1` with `artifact_commit`.

For the record: chatgpt_1's m012 byte-identity finding was correct and has been adopted; its
honest 22/240 reproduction was correct. The conditions above are about verifiability, not about
discounting its technical judgement.

## Deliverables

One handoff to `local_claude_1` on canonical `agent/codex_1`, carrying the review artifact,
one verdict, itemized findings with evidence, and an explicit statement of which findings (if
any) are incompatible with the owner's standing strict rule.
