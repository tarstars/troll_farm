# G-2 execution review — real-game dance attribution

- Reviewer: codex_1
- Reviewed artifact: `claude_1/dance1/g2-execution-2026-08-24.md` and nine companion paths
- Pinned delivery: `agent/claude_1@d75cb2f0b9fbb9dd9dd6f43d872a6e00d099abda`
- Verdict: **EXECUTION_ACCEPTED**

The handoff is canonical: the full artifact commit is reachable from
`origin/agent/claude_1`, every declared path exists at that commit, and the handoff message is on
the sender's canonical branch.

I extracted the pinned commit into a fresh temporary archive and separately extracted the exact
input packages from coordinator commits `3256dafb164dc17417ddb84e00909157f5eb763a` and
`4b9bd563f127da1d79ffe94034103d8c33712daf`. The clean command was:

```text
python3 claude_1/dance1/run_dance_panel.py --inputs review-inputs --out-dir review-run
```

It returned `STATUS PASS`. K0 through K5 all fired and passed: batch-1 identity reproduced
22 D-1 episodes in 17 games with D-2/D-3 zero; K2 reproduced all 38 frozen mechanism labels;
K3 reproduced 9/9 positives and found 3,256 negative ticks in 132/141 pairs; K4 decoded all 469
instrument games without refusal; K5 was exhaustive on all four batches. The K3 pre-committed
remedy was applied before grading, so class 3 is the descriptive `POSITIONAL_EXCHANGE`, never the
causal `SWAP_FLAP` name.

The clean run regenerated all three delivered result files byte-for-byte:

- panel: `dc3286f33fcdc242b20c1ef0f4ae91df917035c704c80e83f1426b1f7818560a`
- instrument facts: `7cd3631ce13205ec681941224b78834dbcbadc3a542495c145188cb08e8937b6`
- champion facts: `55562205d3f216b22551d820c506c1682536bdc926ed605baf42caf3db43e627`

Independent checks confirmed 80 instrument rows and 382 champion rows, exact class-total
identities, no `NO_TELEMETRY` instrument row, and only the four permitted telemetry-free classes
on the champion pass. The champion episode list reproduced exactly: 382 matched, zero only in
either side.

The ambiguity audit is adequately exposed rather than cleaned up: `NO_TARGET` is empty;
`UNCLASSIFIED` retains all 21 no-blocker `MIXED` rows; the swap-by-blocker cross-tab preserves the
eight swap ticks absorbed by blocker-first precedence; the short-window table shows that none of
the 11 instrument blockers at k=3 remains stationary. These are facts for a later owner ruling,
not retroactive boundary changes.

This accepts execution and the four-corpus classification only. D-1 replay counts remain an
**upper bound** because reconstructed plant clocks can invent dances. No bug ruling, cure,
candidate, behavior change, origin claim, broader prevalence claim, or Arena action is accepted.

Deferrals: none.
