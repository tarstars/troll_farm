# Candidate 2 P3 read review — ACCEPTED

Reviewed handoff `coordination/messages/claude_1/20260825T221216Z-20260825-dance-cure-candidate-2-swap-handoff.md`, pinned to `agent/claude_1@7ea1df9fe214cf951c4c92a5feaa90538db34994`.

## Verdict

**P3_READ_ACCEPTED.** The candidate-arm read meets the frozen whole-game P3 bar on this panel: **0 violations over 240 seat views**. The result must travel with its exit decomposition: **228 views returned at the non-eligible guard, 12 eligible views compared byte-equal to the parent, and 0 views violated P3**.

This closes only the candidate-arm P3 read. It does not close G-1, C-12, the owner's C-5 stop-and-ask ruling, or any Arena gate.

## Independent reproduction

I exported the pinned commit to a fresh temporary directory and ran:

```text
python3 claude_1/cure2/p3_read.py
```

The run compiled the parent and candidate afresh and reproduced:

- 240 views: 12 orchard-eligible and 228 non-eligible;
- P3 exits: A-guard 228, B-compared-equal 12, C-violation 0;
- off-class counterfactual: 28 of 228 non-eligible views changed;
- verdict `COMPLETE`;
- output SHA-256 `e65abe93ccd579fd0384ec6746d4592d5f3d9051106aa86c2ae34b4b39a85c69`, byte-identical to the pinned result.

The subject hash is `5577cdce4789…`; the pinned commit is reachable from `origin/agent/claude_1`. All seven reported gates reproduced, including eligible-class inertness (12/12), population and margin parity, the 28-game census correspondence, and a live vacuity witness on all 28 changed off-class views.

## Interpretation boundary

The 228 guard exits are not comparisons. The earned part of the P3 result is the 12/12 eligible-view stream equality; the off-class 28/228 is a counterfactual size, not a P3 verdict. The reported score units must remain explicit: own-score delta −24, opponent-score delta −80, and margin delta +56 over the 240 views.

Next in the established queue is C-12 with the per-troll check enabled, followed by the complete G-1 handoff.
