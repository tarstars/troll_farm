# progress: 20260802-e7a-half-size-logical-simplification

- From: local_codex_1
- To: chatgpt_1, claude_1
- CC: user
- Created UTC: 2026-08-02T21:12:00Z
- Task: 20260802-e7a-half-size-logical-simplification
- Branch: agent/local_codex_1
- Requires acknowledgement: no

## Concrete progress

The 30,949-byte r5 proved the size ceiling but failed closed-loop value at -262.5 mean
paired margin and 14/16 catastrophes.  Functional repairs through r18 restored the fast
smoke to -6.625 mean delta, 3/16 catastrophes, and maximum period-2 target run 3, but r18
is 35,146 bytes and remains 3,736 bytes over the 31,410-byte ceiling.

r19's opponent-occupancy and travel-growth chop forecast grew to 35,589 bytes and regressed
the smoke to -11.4375, so both changes were rejected.  The builder now reproduces r18
byte-exact at SHA-256 `588c6c04...`.

## Evidence

- `data/analysis/live-agent-6553250/e7a-half-size-closed-loop-iteration-2026-08-03.md`
- `local_codex_1/e7a-half-size-logical-simplification/evaluate_motion_smoke.py`
- exact r18 and r19 motion-smoke JSON records in the same private directory

No Arena action.  Sacred source remains exact at `fff6669b...`.  Next target is real
structural simplification of the route-aware worker estimator and two-worker move guard.
