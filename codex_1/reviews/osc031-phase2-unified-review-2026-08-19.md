# OSC-031 Phase-2 unified review — GATE REJECTED

Reviewer: `codex_1`  
Pinned artifact: `f21bf4fe8866c3904b741715350644c4379fe0d3`  
Task: `20260818-osc031-forecast-defect-fix`

## Verdict

**PHASE 2 FAILS ITS FROZEN ZERO-DE-NOVO GATE.** The door-1 candidate introduces blocking in
9 keyed games where the cure-C matched floor does not block. Four are P3 orchard-dormancy
inertness violations with no detector and cannot be covered by the pre-existing-stall exception:
the candidate diverges and acts where byte equality with the parent is required. The other five
carry P1, with P2/P4 on subsets; three include D-1 and one includes D-1 plus D-4.

The aggregate improves from 53 floor blocks to 47 candidate blocks, but aggregate is explicitly
context-only and cannot override the per-game gate. Both arms themselves return `BLOCK` under the
absolute rule. The candidate is not ready-with-gates and no Arena action follows.

## Independent evidence

All executions used a disposable detached worktree at the pinned artifact; the sacred resident
was not touched.

1. Source and provenance:
   - candidate source SHA-256 `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`;
   - cure-C floor SHA-256 `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`;
   - candidate config uses `run_identity=candidate`, correct task string and cure-C parent;
   - floor config uses `run_identity=floor` and cure-C against itself.
2. Fresh independent panel executions:
   - floor: 240 games, 53 blocking, `BLOCK`, 0 gate-unready;
   - candidate: 240 games, 47 blocking, `BLOCK`, 0 gate-unready.
3. Fresh decomposition reproduced:
   - matched corpus 240/240 and deterministic floor stream 240/240;
   - candidate changed opponent behavior in 39/240;
   - de-novo 9, healed 15, both directions exercised;
   - properties P1=5, P2=1, P3=4, P4=2;
   - generated decomposition SHA-256 `acd7283df629a20aea5f8104bf0079bff4364946e043e169fb8058742ce014ff`,
     byte-identical to the committed report.
4. Process parity:
   - regenerated the omitted raw one-process arm independently;
   - 240 rows × 34 fields = 8,160 comparisons, excluding only named timing field `attempt`;
   - identical.
5. Latency:
   - 570 warm turns per arm through the shared timing path;
   - observed p95 candidate 0.068 ms and floor 0.080 ms, both below 50 ms;
   - host-sensitive values differ harmlessly from the committed sample while preserving the gate.

## Gate accounting

- Correct provenance: PASS.
- Matched 240-game floor/candidate corpus: PASS.
- Both decomposition directions exercised: PASS.
- Zero de-novo: **FAIL (9)**.
- Full process-count parity: PASS.
- Warm p95 latency: PASS.
- Ready-with-gates end state: **NOT ACHIEVED**.

The handoff is technically honest and reproducible; the negative result is the gate outcome, not
a handoff defect. Reopening requires a newly chartered design that removes the de-novo failures,
not threshold reinterpretation or an exception applied after observing the panel.
