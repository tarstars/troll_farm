# Persistent-planner spatial-root rank audit

## Outcome

The planner's spatial action generation can be retained without its generic simulator. Across the
complete frozen corpus, every direct planner change selects one of at most two distinct
non-baseline command roots produced by the V439-derived policy. This advances a smaller specialized
chooser architecture; it does not yet justify a candidate or platform request.

Claude implemented and ran the audit under a USD2.75 cap. The call reached its cap after the
complete report was safely written. Primary reviewed the reversible instrumentation, verified the
report, and reran all focused tests: **42 passed in 0.49 seconds**.

## Exact audit

The instrumented combined planner compiled with matched Rust 1.90.0 and zero diagnostics. Its
stdout and cumulative search/change/fallback counters match the frozen planner report on every one
of 43,263 turns in 160 games. Every selected command is verified against the corresponding emitted
root; no inference from verbs or command shape is used.

There are 9,635 late-game searches:

- 964 expose only the baseline root;
- 2,040 expose baseline plus one distinct alternative;
- 6,631 expose baseline plus two distinct alternatives;
- 9,247 retain baseline, 251 select alternative slot 1, and 137 select alternative slot 2.

Thus all 388 direct root changes are a choice among at most three distinct command lines. Raw
selection ranks are 1:180, 2:117, 3:31, 4:35, 5:12 and 6:13. Ranks above two occur only because
the policy probes through duplicate command outputs to find the first or second distinct
alternative. The audit records 19,827 duplicate probes; their cloned policy state is discarded and
never changes live memory.

The full V439/planner stream difference remains 422 turns: 388 direct selections and 34 later
memory divergences. Every memory divergence follows an earlier non-baseline root in the same game;
median gap is one turn and maximum six. Only the first changed turn in each of 101 affected games
is still in exact V439 policy memory; 321 changed turns are evaluated after the planner has already
committed counterfactual memory. A selector analysis must therefore distinguish direct root labels
from downstream memory effects.

Evidence directory:
`/data/separate_troll_farm-working/planning/2026-09-05/root-rank-audit/`.
Report SHA `c0375ded90f3f105264e97c7784b33bc8324483f42e9cedf736b3f3a84d5024e`;
instrumented source SHA `b5453ac97af2daaf51f4f1bb10e9fc1a83df93c435fa718f5adfe59ed9acb800`;
auditor SHA `dd9c4fb26719528bbe4afbfe7e37ea8aa2605eba385d5212524cf1fbb9d92096`;
test SHA `6c129e21ad35bf70671ec436df0fa3d6269f006c3a1f11ea4deeaf41c9cad0dd`.

No Rust submission candidate, adaptive panel, platform game, or publication was opened. The next
bounded experiment is to score these already-generated root alternatives with a small
action-specific late-game evaluator. It must compile near V439 and reproduce enough persistent
planner selections on whole-game holdouts before any competitive panel.
