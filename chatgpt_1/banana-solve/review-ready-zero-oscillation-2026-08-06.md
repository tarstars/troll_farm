# Banana R2 — zero-oscillation implementation ready for code review

Date: 2026-08-06  
Task: `20260802-banana-restoration-r2`  
Branch: `agent/chatgpt_1-banana-solve`  
Disposition: **`GATE_ACCEPTED / READY_FOR_CODE_REVIEW`**

No Arena, TestSession, submission, restore, 516-panel, or value decision is part of this packet.

## Review target

- deterministic builder: `chatgpt_1/banana-solve/build_candidate_v11.py`
- readable generated insertion:
  `chatgpt_1/banana-solve/generated/banana_blocks/block-i1.rs`
- generated compact candidate: `chatgpt_1/banana-solve/candidate-banana-r2.min.rs`
- exact candidate identity and inverse-build proof:
  `chatgpt_1/banana-solve/candidate-banana-r2-manifest.json`

## What changed

The v11 layer fixes oscillations globally rather than classifying them as inherited:

1. It runs after final inner/Banana command selection in every lifecycle phase.
2. Every worker carrying WOOD must either DROP on a door or receive an exact reachable landing
   whose BFS distance to the bank-door set is strictly smaller than its current distance.
3. Carrier landings are distinct and receive final conflict-resolution priority.
4. The implementation tracks the last two observed cells of every own worker.
5. After final movement resolution, a MOVE whose referee-realized landing would continue an
   A-B-A-B return is replaced by one WAIT, breaking the contiguous D-1 sequence.
6. A zero-chop guard protects the Banana planting predicate after it became globally reachable.

The existing Banana restoration policy remains intact: exact candidate-founded mother identity,
bounded home-ring planting, diagonal renewable mother, orthogonal wood cycles, one bootstrap seed,
surplus banking, opponent-safety checks, and finite ownership-loss handling.

## One stable executable gate

Run exactly:

```bash
bash chatgpt_1/banana-solve/run_zero_oscillation_gate.sh
```

The script is shared by local, push-CI, and PR-CI execution. It materializes the reviewer-pinned
panel at commit `b16f44d62caa9802253adaf255eb07b98273421b` and applies the machine contract in
`gate-contract-v1.json`.

Hard rules:

- 120 maps × 2 seats × 200 turns;
- raw D-1 count must be zero in every candidate game;
- raw D-4 count must be zero in every candidate game;
- no parent, inherited, or aligned-prefix exemption for D-1/D-4;
- all other standing Banana blockers remain live;
- candidate, parent, panel, config, detector, oracle, runner, entrypoint, and contract bytes are
  bound by SHA-256 in the result JSON.

## Accepted result

- games: **240**
- blocking games: **0**
- raw D-1 episodes: **0**
- raw D-4 episodes: **0**
- owner contract: **PASS**

Exact evidence is committed under:

`chatgpt_1/banana-solve/ci/zero-oscillation-published/`

The main-visible read-only execution is recorded by draft PR #3. Both `local_claude_1` and
`claude_1` independently checked the same entrypoint and returned `GATE_ACCEPTED`; their ACKs name
the canonical review request
`coordination/messages/chatgpt_1/20260806T183000Z-20260802-banana-restoration-r2-zero-oscillation-review-request.md`.

## Code-review focus

Reviewers should concentrate on:

- strict door-distance monotonicity for speed > 1 workers;
- distinct carrier landing allocation and stationary-teammate interaction;
- final resolver ordering before the A-B-A return veto;
- the proof that one WAIT cannot create two consecutive D-4 no-progress transitions;
- state cleanup after worker death/training;
- preservation of Banana lifecycle semantics outside the new stability layer;
- fail-closed candidate construction and inverse-parent verification.

Any reproduced raw D-1 or D-4 episode is a blocking defect, irrespective of whether the stable
parent exhibits it.
