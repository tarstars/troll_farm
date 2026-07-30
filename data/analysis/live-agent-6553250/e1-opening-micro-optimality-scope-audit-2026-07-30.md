# E1 opening micro-optimality — scope audit

## Decision

**Verdict: `NARROWED_TO_N4_PREFIX_ORACLE`.** The approach register's broad statement that
the opening was “never audited for optimality” is false. The project has already tested a
complete first-worker grid, complete opening macro options, a terminal-valued turn-one
rollout controller, fixed opening prefixes, closed-loop opening portfolios, and one- and
two-batch semantic sequences.

One distinct diagnostic remains untested: a bounded multi-turn sequence over the
resident's own candidate-pair grammar during turns 1–5, scored by terminal continuation
rather than a 3–5-turn reward. That object depends on N4's candidate-surface exporter and
must not start before N4 Phase A is accepted. E1 is therefore narrowed and dependency-gated,
not an active experiment.

## What was already covered

| Class | Exact historical coverage | Binding disposition |
|---|---|---|
| First-worker choice | CONTROL + dynamic max-affordable + all 27 fixed `movement 1..3 / carry 1..3 / harvest 0 / chop 1..3` workers, both seats, eight continuations, six process realizations | No opponent-robust activation; exact-resident abstention. |
| Complete opening macro options | Farm-first orchard scale, adaptive max-bank, later-funding and harvest ablations | Farm-first −97.57 score / −27.46 wood; explicit later funding −56.78; closed. |
| Terminal turn-one rollout | CONTROL and immediate max-affordable harvest-0 option each rolled to terminal/stall before selecting | Locally +2.717 on the frozen block, then rejected in Arena at 21.7 versus 24.1 control; exact option/selector closed. |
| Fixed opening prefixes | Later-scaler first-crop order/species transactions | Best first-generation receipt only 45–60%; fixed one-source prefixes closed. |
| Closed-loop opening portfolio | Eight-action recurrent opening environment and 32 recurrent policies | Representation headroom exists, but explicit source-action breadth misses its 40% gate and the trained four-mode policy loses −1.758. |
| Short semantic sequences | All four one-batch options at 576 roots, then all 16 two-batch sequences | One-deviation breadth 38.54% <55%; fixed two-batch means span only 3.455 <15; adding a third batch was explicitly closed. |
| Primitive resident residual | Up to 14 joint commands, 4/16-turn rollout, at most one MOVE redirect, exact resident continuation | Starts at turn 80 rather than the opening; all-MOVE +1.200 and bank-only +0.508 fail effect/timing gates. |

Primary sources:

- `data/analysis/live-agent-6553250/phase2-macro-option-study-2026-07-17.md`;
- `data/analysis/live-agent-6553250/phase3-phase5-rollout-study-2026-07-17.md`;
- `data/analysis/live-agent-6553250/robust-first-option-discovery-2026-07-18.md`;
- `data/analysis/live-agent-6553250/resident-residual-search-2026-07-18.md`;
- D69–D75 entries in
  `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md`;
- `docs/CONSTRAINTS.md` §(a), §(e), and §(f).

## Why the literal E1 phrasing is not a valid experiment

“Exhaustive” needs an action grammar. Enumerating arbitrary legal command strings and MOVE
destinations produces a large, semantically duplicated tree and is not the resident policy's
decision surface. The project already learned that isolated first-worker enumeration is
complete and negative, while short semantic sequences are too weak.

“Short-horizon” also cannot mean short-horizon reward. Replay archaeology found the
foundational farmer below its pre-train bank through +50 turns and recovering only around
median +68. A 3–5-turn reward would reject delayed opening investments mechanically. Any
remaining opening-prefix audit must mutate only the first few decisions but evaluate the
whole terminal game under a fixed continuation.

## Exact surviving scope

The surviving question is:

> At exact early states, how much terminal hindsight value is available from depth-limited
> sequences of the resident's own legal candidate pairs, after returning to exact resident
> control, across both seats and the frozen opponent families?

This is distinct from the closed classes because it combines multiple early resident-native
pair choices before returning to control. It is not yet implementable without redefining or
duplicating the resident candidate surface. N4 Phase A is already building the bounded
candidate-pair publication/census needed to establish that surface.

If N4 is accepted and exposes a mechanically exact, bounded pair set, a later E1 protocol
may freeze fresh roots, depth, pruning, terminal continuation, family/both-seat breadth,
integrity, and a hindsight-value gate. Its output would be a value bound only. A positive
oracle would not authorize a selector, opening book, candidate, or Arena cycle: D63/D91 and
the turn-one rollout failure keep selection/transfer as separate gates.

## Boundary

- Do not rerun first-worker stats, max-bank/farm-first options, fixed source prefixes,
  one/two-batch semantic sequences, or short online MOVE rollout.
- Do not evaluate the remaining question with a 3–5-turn reward.
- Do not build an arbitrary-primitive exhaustive tree.
- Wait for an accepted N4 candidate-pair surface; then freeze a separate diagnostic
  protocol or close E1 if N4 cannot expose the required surface.
- S2 opening books and learned opening selection remain separate downstream questions.
