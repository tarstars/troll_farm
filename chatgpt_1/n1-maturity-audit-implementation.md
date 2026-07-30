# N1 maturity-curve audit — implementation record

Prepared UTC: 2026-07-30T15:37:00Z  
Task: `20260730-n1-maturity-curve`  
Branch: `agent/chatgpt_1-n1`  
Base shared head: `ecb0d64ca4762326ed18293f2eee1f8dc59f748f`

## Delivered code

- `cgauto/maturity_curve_audit.py` — executable, result writer, synthetic self-test.
- `chatgpt_1/n1_maturity_io.py` — immutable-snapshot loader, raw-field inventory, exact-agent panel and interval construction.
- `chatgpt_1/n1_maturity_model.py` — identifiability gates, within-agent/snapshot fixed-effects model, clustered bootstrap, resident projection and verdict.

Remote commits:

- `09b548ec228eca23049516a8c24659ab148d46ef`
- `ae9aa4e710d55fef332828f35970a43bbb021dde`
- `1a386bcae60844b33ac7c107e297279c4a45b64e`

Local source SHA-256 values before publication:

- `n1_maturity_io.py`: `7e7394597302bdfefb98f816e8c6baa0208db8b9479ef93d778b36c698050267`
- `n1_maturity_model.py`: `fe6207eadffe88a87ac7872d5acea1a105e36a98b25e1393f580373073a18255`
- `maturity_curve_audit.py`: `97de2ae3c5f40060119282965c3536870306263b3145030faa1e9c113dd90962`

Validation performed before publication:

```text
python3 -m py_compile chatgpt_1/n1_maturity_io.py chatgpt_1/n1_maturity_model.py cgauto/maturity_curve_audit.py
python3 cgauto/maturity_curve_audit.py --self-test
self-test: ok
```

## Scientific design

The audit does not use the anecdotal 3–4 point effect as a prior. It:

1. inventories `creationTime`, `updateTime`, possible lifetime battle-count fields and raw battle-list fields;
2. constructs an exact-`agentId` repeated panel and checks stable `agentId`→`userId` and `creationTime` identity;
3. separates score changes from rank-only pool drift;
4. audits whether score changes coincide with advancing `updateTime`;
5. treats recent battle-list length as right-censored and records visible new/dropped battle IDs rather than calling the list length total experience;
6. emits `FULL`, `PARTIAL`, or `UNIDENTIFIABLE` identification support before fitting;
7. fits only repeated agents, using individual fixed effects, snapshot fixed effects, nonlinear age bins, and an agent-cluster bootstrap;
8. includes lifetime battle count only when an invariant count has ≥80% coverage and at least five positive within-agent deltas;
9. reports the resident’s remaining maturity uplift and projected gaps to 24.70 and 25.40;
10. returns `MATERIAL` only when the 95% lower bound is at least +1.0, `IMMATERIAL` when the 95% upper bound is below +0.5, otherwise `MODEST`; missing uncertainty produces `UNIDENTIFIABLE`.

## Generated outputs

A host run creates:

- `coverage-and-result.json`
- `panel.csv`
- `intervals.csv`
- `report.md`

## Execution limitation

The seven D61p snapshots are bulk data on the project host/external volume and are not present in the GitHub contents tree or this execution runtime. Therefore no empirical verdict is claimed in this record. The coordinator has been asked to execute the remotely verified analyzer against the authoritative snapshot root and return the result artifacts and hashes. This is a materialization blocker, not a scientific `UNIDENTIFIABLE` verdict.
