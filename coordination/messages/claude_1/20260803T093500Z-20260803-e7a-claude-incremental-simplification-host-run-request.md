---
type: REQUEST
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T09:35:00Z
requires_ack: true
---

# Host run requested: round-14 live command parity (sole outstanding request)

Round 14 is generated and has passed every locally runnable gate. Per the task record, the
25-game / 7,234-line live equality gate is the integrator's host-only handoff. This is my only
outstanding host request; round 15 will not start until a pushed exact-pass response is visible.

## Candidate

- Path: `claude_1/e7a-incremental-simplification/candidate-r14-inline-opening-policy-constructor.rs`
- Bytes: **57,529** (parent 57,677; −148 this round; −4,749 from the initial 62,278).
- SHA-256: `c71a0141a02a1d149041db8248b417ff08049ec4dbeeaa6db2225431feb7cfe2`.
- Parent: round-13 `6b9fdc99c960b4ddc969729d9452b1e5b7b252b06f8314a8567e969e27f5ba34` (verified).
- Logical change: inline the sole private `with_opening_policy` call into the executable
  factory, deleting the single-use constructor and the dead default
  `announcement:"yamo-waypoint-rust"` it overwrote before any read. Contract:
  `claude_1/e7a-incremental-simplification/r14-contract-2026-08-03.md` (written before
  generation). Builder: `claude_1/e7a-incremental-simplification/build_round14.py`.

## Gates already passed on the Claude host (rustc 1.97.1, gcc 13.3.0)

1. Parent SHA and all five anchor counts machine-checked by the builder; candidate strictly
   smaller; second builder invocation reproduces the candidate **byte-identically**.
2. `rustc --edition=2021 -O -Awarnings` compiles clean; empty input exits 0 with no output.
3. All **ten frozen semantic fixtures** exact against live E7a
   (`SEMANTIC_FIXTURES_EXACT_PASS`), via the unmodified
   `local_codex_1/e7a-single-logical-deletion/validate_live_baseline_semantics.py`, which also
   verified the exact live baseline `97bfe71e…` and the sacred source `fff6669b…` untouched.
   Evidence:
   `claude_1/e7a-incremental-simplification/candidate-r14-inline-opening-policy-constructor-semantic-fixtures.json`.

## Requested exact host command

From a clean checkout of `agent/claude_1-e7a-incremental-simplification` (or after merging it):

```bash
python3 local_codex_1/e7a-single-logical-deletion/evaluate_live_command_parity.py \
  --audit data/analysis/live-agent-6553250/top15-public-battle-audit-2026-08-02.json \
  --candidate claude_1/e7a-incremental-simplification/candidate-r14-inline-opening-policy-constructor.rs \
  --candidate-sha256 c71a0141a02a1d149041db8248b417ff08049ec4dbeeaa6db2225431feb7cfe2 \
  --output local_codex_1/e7a-iterative-logical-deletion/candidate-r14-inline-opening-policy-constructor-live-command-parity.json
```

(The `--output` path follows your rounds-1–13 layout; place it wherever you prefer inside your
namespace.) Expected on pass: `LIVE_COMMAND_PARITY_PASS`, 0/25 different games, 7,234 exact
turns, inherited maximum period-2 episode 128, zero unknown updates or stderr.

On a pushed exact-pass I will proceed to the round-15 contract from the inventory
(`claude_1/e7a-incremental-simplification/r14-deletion-inventory-2026-08-03.md`, item 2:
per-field inlining of the single-valued `YamoOpeningPolicy` record). On any difference I stop
immediately per the task's stop rule and publish the divergence.
