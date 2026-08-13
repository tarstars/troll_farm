---
schema_version: 2
type: handoff
task_id: 20260810-guards-that-cannot-fail
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260813T200014Z-20260810-guards-that-cannot-fail-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: bb845da522bc0904f45a6e149c08d137ee3c4c61
artifact_paths: ["claude_1/guards-g6/g6-progress-2026-08-13.md", "claude_1/banana-restoration-r2/test_trace_detectors.py", "claude_1/banana-restoration-r2/bitetest-audit/branch_ledger.json", "claude_1/banana-restoration-r2/bitetest-audit/mutation_manifest.json", "claude_1/banana-restoration-r2/bitetest-audit/results/mutation-results.json", "claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md"]
created_utc: 2026-08-13T20:00:14Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260810-guards-that-cannot-fail
- Requires acknowledgement: yes

# Watchdog-test job (sub-item "G6") is COMPLETE — all 19 checks resolved

## For the owner, in plain terms

We have automatic checks that are supposed to notice when the bot breaks a rule. Nobody knew
whether they all actually worked. The way to find out is to **deliberately break the thing each
check watches and see whether it complains** — a check that stays quiet when you break its subject
is decoration, not protection.

Nineteen checks had never been tested this way. **All nineteen are now settled.** Seventeen were
proven to work. **Two turned out to be untestable — not broken, but incapable of ever noticing
anything**, because the situation they look for cannot arise in the code around them. Proving that
took as much work as testing the others and is the more useful result: it tells us those two lines
protect nothing, so nobody should rely on them.

Across the whole set of staged breakages, the score went from **21 caught out of 64 when the audit
opened, to 51 of 64 now.**

Two decisions are left, and I deliberately did not take either of them, because **both would make
my own results look better**: whether those two untestable checks should stop counting as failures
in the scoreboard. That is a judgement about what we are measuring, so it belongs with the
coordinator, not with the person whose score it flatters.

## Technical detail

Artifact `bb845da5`. Full notes: `claude_1/guards-g6/g6-progress-2026-08-13.md` (D-8, D-5, D-6 and
final groups) and `g6-progress-2026-08-12.md` (D-7).

**Whole-manifest mutation run: 51 caught / 13 survived of 64**, `caught_by_expected` **51 of 51**,
`caught_only_by_other_detector` 0, control green. Ledger `impl_validity`: **33 PINNED, 3 PARTIAL,
6 UNPINNED, 5 NO_FIXTURE** — from 12 PINNED / 22 NO_FIXTURE when G6 opened.

| group | branches | mutants newly caught | running total |
|---|---|---|---|
| D-7 | 4 | D7-M5, M1, M8, M2, M6 | 29/64 |
| D-8 | 3 + 1 incidental | D8-M9, M3, M11, M7 | 33/64 |
| D-5 | 3 + 2 incidental | D5-M4, M5, M8, M2, M3, M7 | 39/64 |
| D-6 | 3 + 1 incidental | D6-M3, M4, M6, M7, M5, M2, M8 | 46/64 |
| final (D-1, D-3, D-4) | 4 + 1 incidental | D1-M5, M4, M7, D3-M3, D4-M5 | **51/64** |

Every pinned branch carries both halves: the innocent case that must stay silent and a
deliberately violating subject observed firing. Where a fixture killed a mutant it was not aimed
at, I traced the reason, extended `owner_test_classes` and reported it — nine of the newly caught
mutants this run were incidental, and `caught_by_expected` was short until each was named.

## The two branches that cannot be pinned

**D-8 (b) `plant kind == BANANA` (`:1115`).** Reached only inside `c in alive_per_turn[t]`, and
`own_banana_history` builds that set from the *same* `state(t)` filtering on exactly that kind. The
test is true whenever evaluated. Proved by construction (a DIAG banana turning to WOOD leaves the
alive set on the same turn) and by differential (**0/416 probe traces differ**).

**D-4 (e) DROP-at-door commitment start (`:789`).** The DROP that starts the interval is not in
`D4_BANNED_VERBS`, so no episode can be raised on that turn; `executed_drop` clears `committed` on
the same turn; and the only residue, `nd_run = 0`, is set by every commitment start anyway. Born
and closed in one turn having emitted nothing. Differential: **0/416**.

Both are left **counted** in the totals with their rows at `NO_FIXTURE`, and both carry a test that
pins the *reasoning* rather than pretending to pin the branch — so if the surrounding code changes
and the branch becomes load-bearing, the test fails to say so.

## Two dispositions for your ruling

1. **Exclude D8-M8 from the totals?** Precedent exists: `D3-M4-RETIRED` is excluded.
2. **Exclude D4-M6 from the totals?** Same argument.

Excluding both moves the headline from **51/64 (79.7 %)** to **51/62 (82.3 %)**. I have not taken
either decision: it changes the denominator of my own result, which is precisely when the person
holding the pen should not be the one deciding.

## A third finding, reported not repaired

**D-6 clause (a1) is close to inert.** It tests `opp_h <= min_own`, but the planting unit stands on
the cell it plants, so `min_own` is always 0 at a PLANT event and the clause can only fire when an
opponent harvester shares that exact square. It is pinnable — I pinned it that way — but a reader
of the spec text would not expect it. Whether the intended reading is "minimum over own units
*other than* the planter", or an ETA measured from the turn after the plant, is a detector-semantics
question and G6 changes no predicate.

## Boundaries and verification

No predicate changed: `trace_detectors.py` and `conversion_race_oracle.py` are unmodified in
`git diff` across all five groups; nothing under `rust/`; `yamo_orchard_live.rs` byte-exact at
sha256 `fff6669b0bc0b15b…`. Detector suite **67 tests OK**; audit self-tests **13 passed, 2
subtests**. The pinned-source guard fired at every group and was re-pinned rather than overridden,
so published results always name the test file they were produced against; the prose-vs-data check
exits 0 on all five axes.

**Reviewer:** I authored all of it, so I review none of it. `codex_1` per the standing terms.

## Next

D-9 (b)/(c)/(d) remain parked pending the **c5 instrument ruling, which is assigned to me after
G6** — that is now unblocked and is the natural next item unless you sequence otherwise.
