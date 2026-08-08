---
schema_version: 2
type: handoff
task_id: 20260809-score-transparency-manifest
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260809T223000Z-20260809-score-transparency-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 790d76ac4de944e5c88b3d1d5f3f4a333c08eb07
artifact_paths: ["claude_1/banana-restoration-r2/score-transparency-review-claude_1-2026-08-09.md"]
created_utc: 2026-08-09T22:30:00Z
---

# Score-transparency review — the manifest audits the wrong program, and I verified it

Published independently; `chatgpt_1`'s review was not read.

## The finding that reframes the rest

**The manifest's evidence is drawn from `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`), but
the bot under review — `readable__no_orchard` — is
`cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`, SHA `98628e98…`.** I
confirmed the digest myself against `origin/main`; it is a different program, and **eight
functions the manifest's evidence depends on are absent from it.**

Concretely: its chop maximum is **1500/2400, not 3000/3900** (`turns >= 2`; the `.max(1)` is
dead), and `fruit_candidates`/`iron_candidates` have one call site each, so the band is **not
caller-set** in the shipped lineage. This is the same failure this programme keeps producing —
reasoning carefully about one artefact while the subject is another — and it now appears in the
manifest that was written to cure it. Point 2 is thereby evidenced twice over.

## Verdicts

P1 `AGREE_WITH_QUALIFICATION` (weights are roughly **a third** of the decision, not the whole
of it) · P2 `AGREE` · P3 `AGREE_WITH_QUALIFICATION` · P4 `AGREE` · P5
`AGREE_WITH_QUALIFICATION` · P6 `AGREE_WITH_QUALIFICATION`. **Two explicit `DISAGREE`s on the
manifest's own worked evidence** are in the artefact.

## Point 6 audited against the real artefact

**10 boundary crossings, 8 MEASURED end-to-end**, 2 measured-mechanism/suspected-reachability;
plus **3 hierarchy inversions** and **3 pieces of dead scoring code**. The hierarchy is
two-tier: banded and sound above `6_000`, **entirely unbanded below**, where three intentions
share `(0, 2400]` on scales differing by 10⁴.

**The largest crossing (X1) is temporal, not arithmetic:** the conversion intention is priced
`<= 187.5` on turn 250 and `7_000` on turn 251 — a **×37–×961 jump at a magic number**. No
arithmetic bounds check of the kind point 6 implies would ever find it, which is a qualification
the owner needs before commissioning that work.

## Top recommendation: item B first, and it is not a build

`cgauto/n4_candidate_pair_value_audit.py` **already** dumps every candidate, every compatible
pair, and both pre/post-rewrite winners. It was closed on `RUNTIME_CLOSE` — a **5 ms latency
gate for a 2,048-game census that does not bind on an offline tool** — and its resident SHA lock
still matches. Reviving it as a single-state `explain` is **under a day** and reopens L2/L3.

Two further reuse findings: **item A is about three-quarters written** across three unjoined
files, including an intent→band design document parked at "awaiting user review" for a month;
and **point 5's independence clause collides with decision D161** — which matters because
working out "the best action independently" must not reuse the scorer, or the comparison is
circular.

## One process note

The reviewer verified rather than transcribed a SHA and **caught itself copying one wrong** —
the same failure class this review is about. Recorded rather than smoothed over.
