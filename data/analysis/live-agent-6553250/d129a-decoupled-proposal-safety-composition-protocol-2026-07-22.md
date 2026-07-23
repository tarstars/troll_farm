# D129a decoupled proposal-safety composition — frozen retrospective protocol

Date: 2026-07-22  
Status: frozen before D129 safety training or matrix scoring

## Question

D128 shows that absolute-value regression and relative ranking conflict when they share one
proposal logit. Test whether a separate 379→16→1 safety classifier can improve the already-fixed
D126 controller without perturbing its ranker or state gate.

Reproduce D126's D119 seed `11903`, model hash
`476669bc4624a85b870cb31baba450dfcf7d98699365369edf4f8ebacd31ef43`, and gate offset
`-0.10121648758649826`. Train four independent safety heads with seeds `12901--12904`, D115's
root- and class-balanced binary cross-entropy target `act_advantage > 0`, 40 epochs, batch size
1,024, Adam `1e-3`, weight decay `1e-4`, and one deterministic thread. The combined architecture
has 12,723 parameters; deployment size is descriptive only.

For each safety head, derive strict-approval thresholds only from fit-panel nonpositive arms. Use
the smallest observed logit threshold that rejects at least 70%, 80%, 90%, 95%, or 98% of those
arms; approve only logits strictly above the threshold. Do not scan raw thresholds on development.

Compare exactly three compositions after the unchanged state gate passes:

1. `winner_veto`: choose the D119 rank winner and act only if the safety head approves it;
2. `filter_rank`: discard nonapproved proposals and choose the D119 rank winner among survivors;
3. `safety_rerank`: discard nonapproved proposals and choose the maximum safety-logit survivor.

If a root has no admissible choice, continue to the next boundary. Keep exact control when no
boundary acts. Use original row order for exact ties.

## Authority and outputs

Score all `4 × 5 × 3 = 60` cells on the fit panel and the already-consumed D126 panel. Report
unchanged D118 fit gates and D126 relative development gates, intervention confusion, and
cross-seed aggregates. A stable cell may define one later prospective controller, but no D129
cell can qualify, emit a checkpoint, open fresh seeds, start Rust integration, or authorize an
Arena submission. Require two complete result artifacts to be byte-identical.
