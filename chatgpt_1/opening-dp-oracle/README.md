# Opening DP oracle prototype

A self-contained prototype of the hybrid opening search proposed by `chatgpt_1`:

```text
quick greedy/trial sequence -> incumbent upper bound
                              -> event-driven A* search
                              -> DP dominance pruning
                              -> exact optimum or a live [lower bound, upper bound] gap
```

The implementation is intentionally isolated from the active Stage 2A bot build. It neither edits nor imports Claude's opening solver yet. The included reduced model uses the real training-cost shape and models asynchronous workers, finite resources, planting, future crops, shack release and one TRAIN per turn. It is a search-instrument test bed, not a referee-equivalent simulator.

## Files

- `oracle.py` — generic A*/dynamic-programming engine, incumbent branch-and-bound, dominance frontiers, path reconstruction and optimality certificate.
- `reduced_opening.py` — finite event-driven opening model plus greedy incumbent and three deterministic example problems.
- `demo.py` — prints the greedy result, exact/anytime result, certificate and chosen actions.
- `test_oracle.py` — five fast regression tests.
- `DESIGN.md` — rationale, proof boundaries and the adapter plan for real panel maps.
- `RESULTS.md` — executed checks and the larger reduced-model benchmark.

## Run

From this directory:

```bash
python3 test_oracle.py
python3 demo.py
```

Turn exact A* into a bounded anytime search:

```bash
python3 demo.py --case assignment --max-expansions 0
```

The result reports:

- best feasible completion turn;
- whether optimality was proved;
- the smallest surviving lower bound;
- the unresolved optimality gap;
- generated, expanded and pruned state counts.

The larger two-stage example is available but deliberately not part of the fast default:

```bash
python3 demo.py --case two-stage --max-expansions 10000
```

## Verified local result

```text
5 tests passed

global worker assignment: greedy 9, A*/DP 6, proved optimal
plant now vs distant harvest: greedy 13, A*/DP 10, proved optimal
```

“Proved optimal” here always means **within `reduced_opening.py` and its macro-action vocabulary**. It is not yet a statement about a real Troll Farm map. The next honest gate is the fixed-roster adapter and independent `sim/engine.py` replay described in `DESIGN.md`.
