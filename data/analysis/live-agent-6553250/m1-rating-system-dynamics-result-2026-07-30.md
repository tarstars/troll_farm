# M1 rating-system dynamics — DESCRIPTIVE_ONLY

Prepared UTC: 2026-07-30T18:58:00Z  
Task: `20260730-m1-rating-system-dynamics`  
Protocol: `docs/m1-rating-system-dynamics-protocol-v2-2026-07-30.md`

## Verdict

**PARTIAL final support; `DESCRIPTIVE_ONLY`. No wins-per-+1 estimate is earned.**

The stored evidence is broad and internally consistent enough to test simple observable
rules: 8,014 raw game responses (2,564,403,129 bytes) hash-verify, and 307/329 internal
score transitions are outcome-complete across 45 agents. This clears the preregistered
pre-model FULL source threshold. Rule recovery nevertheless fails decisively: neither
win/loss counts, net wins, nor an Elo-like expected-result residual predicts held-agent
score changes materially better than predicting no change.

Final support is therefore PARTIAL under the frozen ladder: the platform score is
observable and batch transitions are well covered, but the update function is not
recovered. A linear coefficient from the failed fit must not be inverted into “wins per
point.”

## Source and semantics

- Seven D61p collections contain six unique leaderboard responses; the two
  `20260728T050038Z` directories share one leaderboard hash but preserve distinct battle
  request times.
- All **2,549** score-changing exact-agent leaderboard intervals coincide with advancing
  `updateTime`; 2,580 intervals advance `updateTime` in total.
- The raw game's `agents[].score` matches the contemporaneous rounded leaderboard score in
  **236/243 = 97.12%** of comparisons.
- There are **229** constant-score epochs with at least five games and both wins and
  losses. This supports the prior-outcome-batch → next-score convention and rejects a
  naive per-game displayed-score update.
- Battle lists are recent/censored windows: 243 observations for 55 agents, lengths
  101–274; 122 observations drop old IDs and 88 add new IDs.
- The manifests record 105 raw-result fetch failures and 1,931 battle IDs with no admitted
  raw result. The completeness checker excludes any unverified game inside a transition
  bracket; source integrity still passes for every consumed response.

## Transition panel

- Internal score transitions: **329**.
- Outcome-complete: **307 = 93.31%**, across **45 agents**.
- Complete outcomes: **2,147 wins, 2,511 losses, 0 ties**.
- Score deltas span −2.6262 to +1.6480; both directions are represented.
- Games per completed score epoch: median 4, range 1–117.

Resident agent `6561795` has five observed score epochs and three complete transitions:

| from → to | delta | preceding wins–losses |
|---|---:|---:|
| 22.1823 → 21.9738 | −0.2085 | 6–17 |
| 21.9738 → 21.7608 | −0.2130 | 3–5 |
| 21.7608 → 21.4726 | −0.2882 | 7–8 |

Even within the resident, net losses of −11, −2, and −1 map to similar or larger drops in
the opposite magnitude order. That is a concrete warning against pricing score with a
single net-win coefficient.

## Held-agent rule validation

| candidate | validation MAE | median absolute error | zero-change MAE |
|---|---:|---:|---:|
| affine wins/losses/ties | 0.479389 | 0.307776 | 0.478583 |
| net wins | 0.481121 | 0.289683 | 0.478583 |
| Elo-like residual | **0.477313** | **0.284044** | 0.478583 |

The best model uses score scale 8 and K 0.025, but improves MAE by only **0.27%**. The
frozen gates require MAE ≤0.05, median absolute error ≤0.02, and at least 50% improvement
over the zero-change baseline. It also fails the per-agent mean-residual gate. The affine
and net-win fits are worse than the baseline.

The alternative next-epoch convention also fails (best MAE 0.506962 versus baseline
0.537687). Excluding the first July 21 snapshot does not rescue the result (best MAE
0.364893 versus 0.365990).

## Interpretation and decision consequence

The platform exposes a batch-associated score, but the visible outcomes in one constant
score epoch do not reconstruct the next score. Plausible missing state includes the exact
platform recomputation membership, a longer rolling history, uncertainty/experience terms,
or a different hidden scoring formula. The audit cannot distinguish these.

Therefore:

- do not convert terminal-margin gains into ladder points or “wins required”;
- continue using frozen terminal-margin gates for candidate selection;
- do not infer that wins are worth zero — only that this stored panel does not recover
  their platform transformation;
- reopen M1 only with exact timestamped/paginated membership for each recomputation and a
  documented pre/post score, or with the platform formula itself.

No bot, resident file, raw source, or Arena state changed.

## Reproduction

```bash
python3 -m py_compile cgauto/rating_system_dynamics.py
python3 cgauto/rating_system_dynamics.py --self-test
python3 -m pytest -q tests/test_rating_system_dynamics.py
python3 cgauto/rating_system_dynamics.py \
  --snapshot-root /home/tarstars/prj/troll_farm/data/raw/snapshots \
  --output-dir local_codex_1/m1-rating-system-dynamics
```

Observed: compile exit 0; `self-test: ok`; **5 passed**; empirical exit 0 with
`{"decoded_source_games": 8014, "outcome_complete_transitions": 307,
"support": "PARTIAL", "verdict": "DESCRIPTIVE_ONLY"}`.

Machine evidence:

- `local_codex_1/m1-rating-system-dynamics/result.json`
- `local_codex_1/m1-rating-system-dynamics/transitions.csv`
- `local_codex_1/m1-rating-system-dynamics/report.md`
