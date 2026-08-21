# OSC-031 G-4c.3 distribution review — 2026-08-18

Verdict: **REVISION_REQUIRED** on evidence deliverables. The aggregate execution result
reproduces, but the committed artifacts do not preserve the chartered per-turn/per-tree
distribution or the required short Markdown table.

Pinned artifact: `7d05cafd19c468ac03dd83f67bd0eddf4432e1d6` on
`agent/claude_1`.

## Independently reproduced result

`g4c3.py` regenerates the committed JSON byte-for-byte and reports:

- pinned manifest SHA-256
  `b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5`;
- exact coverage of all 167 named-subset turns, with zero missing;
- 31 evaluation turns outside the manifest, explicitly counted;
- OSC-031 instrument/resident parity identical;
- all 727 invocations accepted by the G-4c.2 chain reconciler; and
- 315 terminal evaluations in the named subset, all `PREDICT_TREE_NONE`.

The aggregate attribution is therefore reproducible. This review does not dispute its
numeric result.

## Blocker 1: JSON loses per-turn/per-tree multiplicity and identity

The task record requires the named clause(s) with **per-turn/per-tree distribution**.
The JSON stores each turn as `sorted(set(per_turn[t]))`, which preserves only the unique
clause names observed on that turn. It discards how many evaluations occurred and every
`(call, plant)` identity.

This loss is directly measurable:

```text
aggregate terminal evaluations:              315
turn entries in per_turn_clauses:             167
evaluations recoverable from those arrays:    167
```

Thus a reader cannot reconcile 315 from the attached per-turn evidence, distinguish one
evaluation from several identical evaluations, or audit the per-tree claim without
rerunning the program.

Required repair: emit a lossless named-subset record for every terminal chain, minimally
`call`, `turn`, `unit`, `plant`, `terminal_clause`, and preferably the complete ordered
clause-verdict chain. Also emit per-turn terminal counts and assert:

- the sum of per-turn counts equals the number of lossless evaluation records;
- both equal the aggregate clause-distribution sum (315 in the current result);
- every record's turn belongs to the pinned manifest; and
- the selected observed turn set equals the manifest exactly.

Include the explicit 31-turn outside-manifest list, not only its count, so the exclusion
accounting is inspectable while remaining outside the deliverable population.

## Blocker 2: required short Markdown table is absent

G-4c.3 requires “clause-decision table (JSON + short md)” attached to the handoff. The
pinned artifact paths contain only `g4c3.py` and the JSON; `git ls-tree` confirms there is
no G-4c.3 Markdown report at the artifact commit. The handoff prose is not an artifact in
the pinned evidence commit and cannot replace the declared deliverable.

Required repair: commit and attach a short neutral Markdown report containing the
manifest pin, parity/reconciliation facts, exact population accounting, complete
terminal distribution including explicit zeros, per-turn/per-tree reconciliation
summary, and the no-fix/no-judgment/no-class-wide-claim boundaries.

## Gate disposition

- Aggregate execution and attribution: **REPRODUCED**.
- Lossless per-turn/per-tree evidence: **REVISION_REQUIRED**.
- Chartered short Markdown table: **MISSING**.
- G-4c.3 overall: **REVISION_REQUIRED**.
- Owner brief and bug-vs-caution ruling remain unopened pending accepted deliverables.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
