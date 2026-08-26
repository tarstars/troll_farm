# Candidate 1 hold — independent G-1 execution review (2026-08-25)

Verdict: **G-1 FAIL / REVISION_REQUIRED. Do not advance this build to G-2.**

I reviewed the canonical handoff at commit
`abeda52a6f42d6f34e57e5268c9a7188732b98f3` and independently extracted that exact commit with
`git archive` into a fresh `/tmp` directory. The package rebuilds and the compact evidence
reproduces:

- generated arm SHA-256 values are exact: instrument `5e1e5b27322587e...`, candidate
  `7651b69847aa5a70...`, rule-off `b1b565b85fddf16d...`;
- rule-off alpha parity is 34/34 fixtures and 240/240 panel games, including identical next
  referee state and zero telemetry errors;
- candidate and instrument gameplay are identical in 240/240 games;
- resolver controls report 10/10 with the equal-distance case explicitly `N/C`, and the v4
  decoder controls fire 38/38;
- the matched panel reproduces blocking 43 -> 41, D-1 27 -> 1, P4 16 -> 15, **P3 0 -> 1**, and
  **D-4 10 -> 102**; 96/102 candidate D-4 episodes contain the rule's own hold turn;
- the poison arm independently reproduces 2,689 hold turns and a 194-turn maximum consecutive
  hold run while P4 remains 16 -> 16. Its command exits 1 with the explicit verdict that the
  gate cannot see the parked troll.

The equal-distance detour control is correctly retired as unconstructible. On this four-connected
reachable grid, adjacent reachable cells differ in BFS distance by one, so the accepted `<=`
branch has no equality case. This does not block the implementation by itself.

The implementation nevertheless fails the published fail-first G-1 contract twice. The charter
requires P3 clean, but `m004 seat 0` is a new P3 game. More fundamentally, the required poison
control demonstrates that the P4 safety clause is not fit for the promised property: game-level
progress from a teammate masks a unit parked for 194 turns. Therefore the candidate's nominal
P4 16 -> 15 cannot license it. D-4 10 -> 102 is additional measured injury attributable to the
hold rule, not a reason to reinterpret either failed gate.

The literal 35-versus-matched-base-43 ambiguity does not affect this verdict. The candidate fails
before that choice matters. No G-2 read, Arena action, candidate acceptance, or resident change is
authorized by this review.

Reproduction commands run from the fresh archive:

```text
python3 claude_1/cure1/make_cure1_source.py
python3 claude_1/cure1/build_arms.py
python3 claude_1/cure1/alpha_parity.py
python3 claude_1/cure1/make_control_probe.py
python3 claude_1/cure1/run_controls.py
python3 claude_1/narrate4/controls.py
python3 claude_1/cure1/panel_parity.py
python3 claude_1/cure1/arm_equivalence.py
python3 claude_1/cure1/panel_costs.py --controls
python3 claude_1/cure1/d4_attribution.py
python3 claude_1/cure1/poison_arm.py
```

DEFERRED: none for `codex_1` on Candidate 1. A replacement build or gate revision belongs to a
new ack-required card/ruling; this failed build remains stopped before G-2.
