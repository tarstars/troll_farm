# RESULT — ownership defect REPAIRED, all 50 issues gone, strength gate FAILED

**Verdict: FAIL. Do not promote, do not publish.** The demonstrated ownership
failure is fixed and verified: candidate referee issues on the 16 known
map/seat/adaptive-opponent-1 controls went **50 → 0** (0 critical). But the
candidate is still **not stronger**: paired point delta **+0.0** (W/D/L 14-0-2
both arms, unchanged), own score **−17** over 16 games (was −54). Per the ticket
the prerequisites therefore failed, so I ran **no 192 panel and no compact
export**, and I am not proposing another repair chain.

**Changed files (mine only; all pre-existing content archived first).**
Parent `claude_candidate_policy_flat.rs` `95ee691e…`, `bot.rs` `44e3daca…`,
`submission.rs` `7f61a6cd…` **unchanged** (verified by hash).
`claude_candidate_seedplan_core.rs` `a5e27245…`;
`test_claude_candidate_seedplan.rs` `600d3d62…`; generated
`_a.rs` `fcf657e2…`, `_a_module.rs` `aa2525c3…`, `_a_tests.rs` `21e963e4…`;
`claude_candidate_seedplan.py` `42a2a106…` and `_control_module.rs` `526cd9cc…`
unchanged.

**What was repaired** (three actual-state fixes, no economic/spec/horizon change):
1. Deferral is now conditional on the parent transaction being **legal in actual
   state** (`parent_transaction_legal` restates the referee's `no_capacity`,
   `out_of_stock`, `no_shack`, `no_grass`, `existing_plant`, `no_seeds`).
2. New `Phase::Return`: every cancellation route (deadline, plot loss,
   disruption, deferral cap) routes a worker still holding our withdrawn seed to
   **plant it at the plot or bank it**, then hands the worker back EMPTY.
   `Return` ends the moment the pack is clear and is bounded by
   `SEED_RETURN_LIMIT = 30`, so it cannot stall.
3. `resolve_endpoints`: complete joint own-side endpoint validation after the
   override (shared destinations and moves into stationary own units), in two
   priority stages, shortening along each unit's own target. No obstacle BFS.

**Tests.** `rustc 1.90.0` (absolute path, `--edition 2021`)
`-O --test claude_candidate_seedplan_a_tests.rs` → **26 pass / 0 fail**,
including two new fixtures (safe cancellation with a carried seed; joint endpoint
legality) and the never-displace fixture rewritten to explicit semantics: a
**legal** parent PICK is deferred to, an **illegal** one is not.

**Evidence** (this run dir): `gate16b.tsv`, `gate16b-summary.txt`, `rows.txt`,
`issues.txt`, `tests-1.90.log`, `HASHES.txt`, `build-gate2.log`, `archive/`.

**Limitations.** One opponent, 16 development controls, one seat pair diagnosed.
`9947503` seat 1 improved −74 → −37 but still dominates the loss. No compact
export, no 16-stream equality, no latency measurement, no 192 panel. No jobs left
running.

**Next action.** Owner decision: this family is legal and clean but flat, so
either park it or investigate why `9947503` seat 1 still loses 37 points.
