# Executed checks

Run on 2026-09-03 with Python 3 in the interactive `chatgpt_1` workspace.

```text
python3 -m unittest -v test_oracle.py

Ran 5 tests in 0.004s
OK
```

Default deterministic examples:

| case | greedy upper bound | A*/DP result | certificate | expanded | dominance-pruned |
|---|---:|---:|---|---:|---:|
| global worker assignment | 9 | 6 | optimal in reduced model | 81 | 32 |
| plant now vs distant harvest | 13 | 10 | optimal in reduced model | 17 | 3 |

Optional larger two-stage example:

```text
greedy upper bound: 22
A*/DP result: 19
certificate: optimal in reduced model
expanded: 182,787
generated: 333,966
dominance-pruned: 107,999
peak queue: 24,771
elapsed: 11.25 s
maximum resident memory: 390,804 KiB
```

The larger result demonstrates both sides of the design: the exact method improves the incumbent, but an uncompressed state representation is already memory-hungry. The real-map adapter should therefore start on the 22 known miss cases, strengthen the lower bound, and measure state-key variants before attempting all 400 map-seats.
