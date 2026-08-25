---
schema_version: 2
type: handoff
task_id: 20260814-iteration-3-work-plan
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260814T063203Z-20260814-iteration-3-work-plan-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260814T062010Z-20260814-iteration-3-work-plan-a1-acceptance-ack.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: ee8658a3d9dc7e09e739f869e6299c1f9b1b3342
artifact_paths: ["claude_1/guards-g6/a2-d9-recalibration-2026-08-14.md", "claude_1/banana-restoration-r2/test_trace_detectors.py", "claude_1/banana-restoration-r2/bitetest-audit/branch_ledger.json", "claude_1/banana-restoration-r2/bitetest-audit/mutation_manifest.json", "claude_1/banana-restoration-r2/bitetest-audit/results/mutation-results.json", "claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md"]
created_utc: 2026-08-14T06:32:03Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260814-iteration-3-work-plan
- Requires acknowledgement: yes

# A-2 delivered: the three D-9 checks are fixtured and pinned — and no check anywhere is now untested

## For the owner, in plain terms

Three checks watch whether the bot trains its second worker **late**, **not at all**, or **with
different settings**. Yesterday's ruling established the recording equipment can see all three.
This item gave each one a proper test: break the thing it watches, confirm it complains; then show
an honest case where it correctly stays quiet.

**All three now catch their staged breakage.** And a milestone worth naming: when this audit opened
it said *"22 of 47 checks have no test at all — that, not the catch rate, is the load-bearing
measurement."* **That count is now zero.**

The catch rate reads 54 of 65, up from 51 of 62. **It moved because we added three new things to
test and caught all three** — not because anything was excluded. Both kinds of movement have
happened this week and the audit now records them separately, so nobody has to guess which one a
change was.

## Technical detail

Artifact `ee8658a3`; note at `claude_1/guards-g6/a2-d9-recalibration-2026-08-14.md`.

| row | before | after |
|---|---|---|
| D-9 (a) `banana_before_train` | PINNED / **INSTRUMENT_UNSUPPORTED** | PINNED / **APPLICABLE** |
| D-9 (b) `train_late` | **NO_FIXTURE** / INSTRUMENT_UNSUPPORTED | **PINNED** / **APPLICABLE** |
| D-9 (c) `train_missing` | **NO_FIXTURE** / INSTRUMENT_UNSUPPORTED | **PINNED** / **APPLICABLE** |
| D-9 (d) `train_stats_differ` | **NO_FIXTURE** / INSTRUMENT_UNSUPPORTED | **PINNED** / **APPLICABLE** |

Whole-manifest: **54 caught / 11 survived of 65**, `caught_by_expected` **54 of 54**, control green.
Ledger: **36 PINNED, 3 PARTIAL, 6 UNPINNED, 2 EQUIVALENT_GUARD_UNTESTABLE**, `NO_FIXTURE` **0**.
Applicability **47 of 47 APPLICABLE** — no `INSTRUMENT_UNSUPPORTED` row remains in the audit.

**The denominator moved by addition.** These clauses had never carried a staged breakage, so
fixturing them required writing their mutants: `D9-M5` (b), `D9-M6` (c), `D9-M7` (d), all caught by
`TestD9Paired`. **62 → 65: caught +3, denominator +3, survivors unchanged at 11** — the opposite
direction from the two exclusion rulings, and flagged as such in the audit.

**Halves that do real work**, beyond the obvious firing cases:

- (c) — when the **parent** never trains, a candidate that also never trains is **silent**.
  Without that, the clause could be firing on "candidate did not train" alone, a different and
  wrong predicate.
- (b) — training **earlier** than the parent is **silent**. The clause is `>`, not `!=`; a
  candidate that trains sooner has not delayed anything, and flagging it would invert the rule.
- (d) — a candidate that is late **and** different reports `train_late` **only**, pinning the
  `elif` ordering so one divergence yields one finding.
- The innocent case is the **first** test in the class, because three clauses that fired on
  everything would still have passed the three firing cases.

## The restriction recorded on every row, not just in this message

All three remain **`SUPPORTED` with a witnessed population of `0 of 240`** in corpus c5. The
fixtures are constructed cases pinning implementation against spec; **no live-corpus claim may rest
on them.** That sentence is on each ledger row so citing the row alone still carries it.

## Boundaries

No detector predicate changed — `trace_detectors.py` and `conversion_race_oracle.py` unmodified in
`git diff`, nothing under `rust/`, `yamo_orchard_live.rs` byte-exact at sha256
`fff6669b0bc0b15b…`. Detector suite **74 tests OK**; audit self-tests **13 passed**; prose-vs-data
exits 0 on all five axes; pinned-source drift re-pinned rather than overridden.

**I authored this and review none of it.** `codex_1`'s rerun of the A-1 demonstration gates A-2
closing; I supplied the exact recipe in `20260814T062625Z` so a disagreement is informative rather
than a setup difference. If any of the four cases fails to reproduce for them, stop me — these
fixtures rest on that demonstration.

**Next:** A-5 (H3a trigger preflight) is claimed and starting; A-3 / A-4 remain as read-only
fillers. D89a-LI is not claimed and will not be.
