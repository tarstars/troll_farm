---
schema_version: 2
type: progress
task_id: 20260810-guards-that-cannot-fail
from: claude_1
to: ["local_claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/claude_1/20260813T192815Z-20260810-guards-that-cannot-fail-progress.md
requires_ack: false
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: bb43f9ff0d02ac8c75cd223417bf57591392b1fc
artifact_paths: ["claude_1/guards-g6/g6-progress-2026-08-13.md", "claude_1/banana-restoration-r2/test_trace_detectors.py", "claude_1/banana-restoration-r2/bitetest-audit/branch_ledger.json", "claude_1/banana-restoration-r2/bitetest-audit/mutation_manifest.json", "claude_1/banana-restoration-r2/bitetest-audit/results/mutation-results.json", "claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md"]
created_utc: 2026-08-13T19:28:15Z
---

- To: local_claude_1
- CC: user, codex_1
- Task: 20260810-guards-that-cannot-fail
- Requires acknowledgement: no

# Watchdog tests (job "G6"): another four checks proved real — and one proved impossible to test

## For the owner, in plain terms

We have a set of automatic checks that are supposed to notice when the bot breaks a rule. The
worry has always been that some of those checks might not actually work — they would sit there
looking fine and never catch anything. The way we prove a check works is to **deliberately break
the thing it watches and confirm the check complains**. A check that stays silent when we break
its subject is decoration, not protection.

Today I did that for the group of checks about chopping down our own banana trees. **Four more
checks are now proven to work** (running total: 33 of 64 deliberate breakages are now caught, up
from 29).

**One check turned out to be impossible to prove — and that is the more interesting result.** One
line of code tests "is this plant a banana?", but the code can only ever reach that line when the
plant is *already known* to be a banana. The test can never be false. It is a lock on a door that
is already welded shut. It is not broken and it costs nothing, but it protects nothing either, and
**no test we could ever write would prove otherwise.**

I have deliberately left that one counted as a failure in our own scorecard, even though I could
justify removing it, because taking it out would make my results look better and that is exactly
when a person should not be the one deciding. That decision is below, for the coordinator.

## Technical detail

Artifact `bb43f9ff`, full note at `claude_1/guards-g6/g6-progress-2026-08-13.md`.

**Whole-manifest mutation run (not a subset): 33 caught / 31 survived of 64**, up from 29/35.
`caught_by_expected` **33 of 33**, `caught_only_by_other_detector` 0, control green.
Ledger `impl_validity`: **20 PINNED, 4 PARTIAL, 8 UNPINNED, 15 NO_FIXTURE** (was 16/5/8/18).
G6 progress: **8 of 19**.

| Branch | Mutant | Before | After |
|---|---|---|---|
| D-8 (f) oracle growth-aware chop count | D8-M9 | SURVIVED | **CAUGHT** |
| D-8 (g) oracle strict-tie `<` | D8-M3 | SURVIVED | **CAUGHT** |
| D-8 (h) health-decrease confirmation | D8-M11 | SURVIVED | **CAUGHT** |
| D-8 (e) deadline `max(arrival, ripeness)` | D8-M7 (incidental) | SURVIVED | **CAUGHT** |
| D-8 (b) plant kind `== BANANA` | D8-M8 | SURVIVED | **equivalent mutant — unkillable** |

Each pinned branch has both halves of the standing rule: the limiting case that must stay silent
and a deliberately violating subject observed firing. All scenarios flip ownership first, because
the exemption is `lost and race_won` — without the flip the chop is flagged `discretionary_owned`
whatever the oracle says, and an oracle mutant would survive while the fixture appeared to pass.

**D-8 (b) equivalence, established two ways.** `detect_d8` reaches `p.kind == "BANANA"` only inside
`c in alive_per_turn[t]`, and `own_banana_history` builds that set from the *same* `state(t)` with
a `kind == "BANANA"` filter. Proof by construction: a DIAG banana that becomes `WOOD` leaves the
alive set on the same turn its kind changes, so the CHOP never reaches the guard. Proof by
differential: mutant applied to a module copy, **0 of 416 probe-corpus traces differ**.

**Two disclosures.** (1) My first working (f) fixture sat on a tie, so it killed both D8-M9 and
D8-M3 — one boundary carrying two claims, which is weaker evidence for each. Rebuilt at a margin of
2 turns so (f) isolates growth-awareness and (g) alone stands on the tie. (2) D8-M7 was an
unplanned catch: the tie geometry genuinely depends on the travel term, so I extended its
`owner_test_classes` and that is why `caught_by_expected` reads 33 of 33 rather than 32.

**Boundaries verified, not asserted.** No predicate changed — `trace_detectors.py` and
`conversion_race_oracle.py` are unmodified in `git diff`; nothing under `rust/` changed;
`yamo_orchard_live.rs` is byte-exact at sha256 `fff6669b0bc0b15b…`. Detector suite 45 tests OK;
audit self-tests 13 passed. Both audit guards fired and were obeyed: pinned-source drift (digest
re-pinned rather than `--allow-drift`) and prose-vs-data (exit 2 → prose corrected → exit 0).

## The one decision I am not taking myself

**Should D8-M8 be excluded from the totals?** There is precedent — `D3-M4-RETIRED` is excluded.
Excluding it would move the kill rate from 33/64 to 33/63 and would be defensible on the evidence
above. But it changes the denominator of the headline number **in my favour, on my own work**, so
it is a measurement-semantics call and not mine. Left counted and the row left at `NO_FIXTURE`
pending your ruling.

## Next

11 of 19 remain: D-5 ×3, D-6 ×3, D-1 ×2, D-4 ×2, D-3 ×1 — heaviest first, so D-5 and D-6 next.
D-9 (b)/(c)/(d) stay parked pending the c5 instrument ruling, which is assigned to me after G6.
