# Per-opponent continuation feasibility — result, 2026-07-19

## Verdict

**Close aggregate proxy reconstruction.**  Stable agent identity improves on an identity mean,
but identity-conditioned state/history retrieval does not beat the stronger population-state
continuation on held games.  The result fails three of five material gates, including the crucial
turn-100 gate.

The read-only panel contains 144 SHA-selected completed games—24 for each of six exact submitted
agents—and 288 cutoff examples.  No games or submissions were started.

## Integrity and selection

- all six battle endpoints exposed at least 154 non-consumed exact-agent games;
- 240 unique replays were fetched with zero fetch failures;
- one of the first 40 Bondo occurrences was ineligible, leaving 39; every other agent had 40/40;
- the first 24 eligible hash-ordered games per agent were retained as frozen;
- each agent contributes 16 discovery and eight confirmation games; and
- all 288 cutoff examples have exact decoded turns and complete targets/features.

Discovery selected `k=5` for population map/state, `k=3` for population history, `k=5` for
identity map, and `k=3` for identity state/history.

## Held-game result

| Gate | Required | Observed | Pass |
|---|---:|---:|:---:|
| Identity history vs population state | >=10% lower error | **0.54% higher** | no |
| Identity history vs identity mean | >=5% lower error | 11.94% lower | yes |
| Turn-100 identity history vs population state | >=10% lower error | **8.73% higher** | no |
| Agents improved | >=4/6 | 4/6 | yes |
| Paired confirmation wins | >=55% | 50/96 = 52.1% | no |

Overall normalized MAE is 0.776 for population state and 0.780 for identity history.  Identity
helps at cutoff 50 (9.2% below population state) but reverses after cutoff 100, exactly where the
continuation model is needed most.  Per-agent gains are heterogeneous: +13.6% Bondo, +5.6%
celeria, +0.7% viewlagoon, +0.2% MSz, -5.6% Meruem, and -18.4% gaha.

The strongest portable result across both retrieval studies is therefore simple: current state
has momentum, while policy identity and recent aggregate actions add too little or actively hurt.

## Consequence

Do not hand-build another proxy, replay another bot's command stream, or tune aggregate retrieval
features on these panels.  Offline opponent models may remain diagnostic, but they cannot judge a
candidate.  Return to direct causal, baseline-preserving interventions and use official replays
only to establish mechanism activation and failure concentration before a controlled arena test.

Artifacts: `per-opponent-continuation-protocol-2026-07-19.md`,
`per-opponent-continuation-panel-2026-07-19.json`,
`per-opponent-continuation-2026-07-19.json`,
`cgauto/per_opponent_continuation_dataset.py`, and
`cgauto/per_opponent_continuation.py`.

