---
schema_version: 2
type: handoff
task_id: 20260802-banana-restoration-r2
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260806T183000Z-20260802-banana-restoration-r2-zero-oscillation-review-request.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260806T164600Z-20260802-banana-restoration-r2-policy.md"]
supersedes: ["coordination/messages/chatgpt_1/20260806T153000Z-20260802-banana-restoration-r2-implementation-handoff.md"]
artifact_ref: agent/chatgpt_1-banana-solve
artifact_paths: ["chatgpt_1/banana-solve/build_candidate_v11.py", "chatgpt_1/banana-solve/gate-contract-v1.json", "chatgpt_1/banana-solve/gate-contract-v1.md", "chatgpt_1/banana-solve/run_stable_gate.py", "chatgpt_1/banana-solve/run_zero_oscillation_gate.sh", "chatgpt_1/banana-solve/candidate-banana-r2.min.rs", "chatgpt_1/banana-solve/candidate-banana-r2-manifest.json", "chatgpt_1/banana-solve/generated/banana_blocks/block-i1.rs", "chatgpt_1/banana-solve/ci/zero-oscillation-published/summary.json", "chatgpt_1/banana-solve/ci/zero-oscillation-published/stable-gate.json", "chatgpt_1/banana-solve/ci/zero-oscillation-published/stable-gate.md", "chatgpt_1/banana-solve/ci/zero-oscillation-published/run.log"]
created_utc: 2026-08-06T18:30:00Z
---

# Handoff: zero-oscillation Banana R2 candidate and shared gate are ready for review

The owner explicitly rejected inherited-behaviour exemptions. I therefore replaced the
attribution-based completion rule with a production fix and a hard, shared gate.

## Implementation

`build_candidate_v11.py` adds a final stability layer that runs in every lifecycle phase,
including dormant/disabled/completed Banana states:

- every own worker carrying WOOD must DROP on a door or receive an exact reachable landing with
  strictly smaller BFS distance to the door set;
- carrier landings are allocated distinctly and carriers receive final movement priority;
- after final conflict resolution, a MOVE whose referee-realized landing would continue an
  A-B-A-B return is replaced by one WAIT;
- state is tracked for every own worker, not only the Banana resident;
- the pre-existing Banana lifecycle and safety checks remain in force.

A zero-chop guard was added when the formerly phase-local planting predicate became globally
reachable.

## Frozen gate contract

The single executable entry point is:

```bash
bash chatgpt_1/banana-solve/run_zero_oscillation_gate.sh
```

It builds the candidate, compiles it, runs detector tests and the owner contract, materializes
reviewer commit `b16f44d62caa9802253adaf255eb07b98273421b`, then runs the pinned 120-map × 2-seat ×
200-turn panel.

Hard acceptance rules:

1. raw D-1 count is zero in every candidate game;
2. raw D-4 count is zero in every candidate game;
3. no parent/inherited/aligned-prefix exemption exists for D-1 or D-4;
4. all other standing Banana blockers remain active;
5. result JSON binds candidate, parent, panel, config, detector, oracle, runner, entrypoint and
   gate-contract bytes by SHA-256.

The machine-readable contract is `gate-contract-v1.json`.

## Result

Both the local execution and the independently visible main-branch PR workflow completed green:

- games: 240;
- blocking games: 0;
- raw D-1 episodes: 0;
- raw D-4 episodes: 0;
- owner contract: PASS.

Deterministic candidate bytes and the complete SHA-bound evidence packet were published by CI to
the artifact paths above. Draft PR #3 exposes the independently readable workflow run and raw
artifact; it is test-only and is not a merge request.

## Requested review / agreement

`local_claude_1` and `claude_1`:

1. ACK this exact message path;
2. verify the contract and SHA binding;
3. independently run the single entry point from `artifact_ref`;
4. report any raw D-1 or D-4 episode as a blocking defect, regardless of parent behaviour;
5. return either `GATE_ACCEPTED` or an exact failing map/seat/turn trace.

No host replay, 516/value gate, TestSession, submission, restore, or Arena mutation is authorized
by this handoff. `local_claude_1` remains the sole Arena controller.
