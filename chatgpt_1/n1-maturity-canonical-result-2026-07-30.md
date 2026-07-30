# N1 maturity-curve measurement — canonical result

Prepared UTC: 2026-07-30T17:14:00Z  
Task: `20260730-n1-maturity-curve`  
Work owner: `chatgpt_1`  
Host executor: `local_codex_1`  
Analyzer commit executed: `836cfff055c4c07964cbb6d2e1730a316f1f1675`

## Verdict

**PARTIAL identification support; IMMATERIAL remaining maturity effect under the frozen decision rule.**

The seven stored snapshots support a within-agent age analysis because `creationTime` and
`updateTime` have 100% coverage, exact `agentId` identities are stable, 1,008 agents repeat,
2,549 score-changing intervals all coincide with advancing `updateTime`, and 41 within-agent
age-bin crossings are observed. The model does not identify a separate games-played effect:
there is no invariant lifetime battle-count field, and recent battle lists are right-censored.

## Resident result

At the latest included snapshot (`20260730T021701Z-d61p-wide`), the resident was:

- score: **21.47**;
- age: **10.356 days** (`d7_14` bin);
- estimated remaining maturity uplift: **−0.1612**;
- agent-cluster bootstrap 95% interval: **[−0.7525, +0.4567]**;
- projected mature score: **21.3088**;
- projected gap to interim 24.70: **3.3912**;
- projected gap to target 25.40: **4.0912**.

The estimate does **not** establish that aging lowers score. Zero is well inside the interval.
The operational conclusion is narrower: under the preregistered rule, the interval's upper
bound (+0.4567) is below the +0.500 immateriality threshold, so passive remaining maturity is
not an identified path to a decision-relevant gain.

## Boundary sensitivity

The categorical verdict is close to its threshold: +0.4567 is only **0.0433** below +0.500.
Therefore `IMMATERIAL` is accepted as the frozen-rule verdict, but it should not be presented
as a high-margin scientific separation. Small reasonable changes to binning, weighting, or
the threshold could change the label to `MODEST`; they would not support the earlier
anecdotal +3–4 point maturity claim or a +1.0 experiment-value case.

The two July 28 snapshots are separate collections about two hours apart. Their ladder rows
are largely unchanged while battle visibility differs. Keeping both is acceptable repeated
panel evidence: the model has snapshot fixed effects and the bootstrap clusters by agent.
They should not be described as two independent score recomputations.

## Identification and confounds

- Individual fixed effects remove stable agent quality.
- Snapshot fixed effects absorb pool-wide score shifts.
- Rank-only movement is measured separately and is not treated as maturity.
- `updateTime` is used to audit discrete score recomputation; no observed score change lacks
  advancing `updateTime`.
- Battle-list length is not treated as lifetime experience.
- The anecdotal 3–4 point figure is not used as a prior.

This is **PARTIAL**, not FULL, identification because time-since-submission is observable but
battle accumulation is censored. The result estimates the net within-agent age-bin association
after snapshot effects; it does not decompose elapsed time from games played.

## Decision consequence

N1 closes the passive-maturity branch for planning purposes. The resident should be evaluated
against its measured current score and architecture/policy improvements, not against an
assumed +3–4 point future maturation bonus. No Arena action follows from this analysis.

## Reproduction and evidence

Host command completed with exit 0, empty stderr, Python compile pass, and synthetic self-test
`ok`. Seven immutable snapshots were read from
`/home/tarstars/prj/troll_farm/data/raw/snapshots`.

Canonical host bundle: `local_codex_1/n1-host-run-20260730/`.

SHA-256 values reported by the host executor:

- `coverage-and-result.json`: `ebafcdbe1ad300973302a2db6b05e24bd4d643957d4cc27be022d495ccdac435`
- `intervals.csv`: `39f7f4bfade672bc31a896f47a9fd95676a5c034442f31f75aad86802f835c9d`
- `panel.csv`: `148a1dee8b41d4324f0afc3e2f90670441817e40c382e1970c04c83b2f84efbb`
- `report.md`: `20f7f4be2fb338cfa70300f1ec70fad3968b6cb6d7b40291225d67e27a36c3a0`

Analyzer source remains:

- `cgauto/maturity_curve_audit.py`
- `chatgpt_1/n1_maturity_io.py`
- `chatgpt_1/n1_maturity_model.py`
