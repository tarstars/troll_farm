# N2 — B4.4 verification result

- Date: 2026-07-30
- Verdict: **B4_4_CORRECTED**
- Claim verdicts: C1–C7 all `CORRECTED`
- Protocol:
  `docs/n2-b4-4-verification-protocol-v2-2026-07-30.md`
- Machine bundle: `local_codex_1/n2-b4-4-verification/`
- Arena/resident consequence: none; read-only audit

## Decision

B4.4 must not be cited as written. Its pooled group medians and generation-level reap rates
can be reconstructed, but its source provenance, “all/every peer” wording, loop
interpretation, wood-concentration scope, causal ranking, and scale-survival attribution
all require correction.

The owner-identified distinction is supported directly by crop outcomes: early planting
can establish a harvested orchard, while post-turn-250 planting can be chopped to turn
fruit into wood. Those are compatible uses. Turn alone does not identify intent.

## Source reconstruction

The original B4.4 JSON report was written to an ephemeral path and is absent. The tracked
commit-`46d36098` stats file says 8,131 games, but that exact prefix produces only 23 cohort
agents and 2,700 tracked occurrences, not the published 25 and 2,787.

An exhaustive scan of every prefix from 8,131 through the current 9,082 records found one
unique structural match: the first 8,395 records, ending at game 896651751, with 8,336
clean games, 25 agents (12 strong / 13 weak), 2,787 occurrences, resident rank 43 and
roster mean/median 2. Its prefix SHA-256 is
`1f9e3855fad01f5ade6dd1ece17f0e6b20597d0b01889ef5240ee27700b68d40`.
This is an **anchor-matching reconstruction**, not the missing immutable original.

The audit hashed 5,614 selected raw/trajectory files, decoded 2,963 union occurrences
across the anchor and current cuts, and had zero failures. All 2,787 anchor occurrences
have zero unknown diff updates, exact spawn/train counts, compatible reference events and
lineages, and identical summary/reconstruction first-plant turns.

## Claim verdicts

| claim | verdict | corrected result |
|---|---|---|
| C1 — corpus/cohort provenance | **CORRECTED** | 8,131 does not reproduce B4.4. A unique 8,395 prefix matches all published structural anchors, but the original report/manifest is missing. |
| C2 — resident 191.5 vs every peer 21–29 | **CORRECTED** | Conditional group medians reproduce: resident 191.5 (204/204), strong 29 (1,983/2,019), weak 21 (530/564). The 25 per-agent medians span **3–254**, so “all 25 peers plant by 21–29” is false. Current medians are 177/33/21 and peer medians still span 3–254. |
| C3 — reap 0.93% vs 15–17% for every peer | **CORRECTED** | Pooled generation rates reproduce: resident **0.928%**, strong **15.322%**, weak **17.198%**. “Every peer” is false: yamo, therealbeef and LeRenard are 0%; mehdi_ayari is 0.189%, also below the resident. The same four exceptions remain on the current cut. |
| C4 — score composition / resident most wood-concentrated | **CORRECTED** | Group means nearly reproduce: strong 215.527 vs resident 185.696; strong has +15.03% wood and +30.02% fruit. Resident group mean wood share is 94.69%, but pooled groups cannot establish an every-agent property; H3's controlled quartet has the resident harvesting 2–9× more fruit, reversing the relevant five-agent interpretation. |
| C5 — no sustained loop / one planting purpose | **CORRECTED** | Self-plant→self-chop occurs in 100% resident, 97.62% strong and 93.09% weak games. Resident early crops: 23 created, 18 self-harvested, 2,022 fruit gained. Resident late crops: 1,027 created, all 1,027 self-chopped, 1,060 wood gained, zero self-harvest. Early orchard and late conversion are distinct observed outcomes, not a contradiction. |
| C6 — disabled factory causes field delay | **CORRECTED** | Byte-identified dev source at SHA `fff6669b…` contains tested factory machinery, defaults it and its selector off, makes the selector one-shot at roster ≥2, and contains renewable-harvest and >250 conversion rules. The deployed slim artifact pruned that subsystem, and current source facts do not causally explain historical field timing. |
| C7 — trajectory/survival/suppression ranking | **CORRECTED** | Uncontrolled B4.4 trajectory and scale summaries are descriptive only. H3's exact-opponent controls dissolve the headline survival gap, refute “no loop,” reverse the quartet wood-purity interpretation, and find suppression efficiency indistinguishable. Those later controls remain binding. |

## Purpose result

The outcome audit gives the missing semantic separation.

- Early (turns 1–50) self-plants frequently feed repeated self-harvest. Across strong
  agents, 5,638 early crops include 2,397 self-harvested generations and 23,710 gained
  fruit; weak agents have 882/2,233 and 5,880 fruit.
- Late (>250) self-plants are predominantly wood conversions. Strong agents self-chop
  7,320/8,444 late crops and gain 9,399 wood; weak agents self-chop 1,151/1,923 and gain
  1,774 wood. Resident late conversion is exact in this cut: 1,027/1,027 self-chopped,
  zero self-harvested.
- Outcomes do not prove subjective intent or intervention value. D175a's controlled
  harmful early-plant result remains binding for this resident scheduler.

## Current sensitivity

The full 9,082-record/current-leaderboard cut contains 25 cohort agents, now split
11 strong / 14 weak at resident rank 47, and 2,696 occurrences. The main corrections are
stable:

- conditional group first-plant medians are resident 177, strong 33, weak 21, while
  per-agent medians remain 3–254;
- pooled reap rates are resident 0.841%, strong 14.575%, weak 17.872%, with the same four
  exceptions to “every peer”;
- self-plant→self-chop rates are 100%, 97.40%, and 93.96%;
- early-harvest and late-chop outcome separation remains.

## Reproducibility

Acceptance commands:

```text
python3 -m py_compile cgauto/verify_b4_4_claims.py
python3 cgauto/verify_b4_4_claims.py --self-test
python3 -m pytest -q tests/test_verify_b4_4_claims.py
python3 cgauto/verify_b4_4_claims.py --jobs 12 --output-dir local_codex_1/n2-b4-4-verification
```

Observed: compile pass, `self-test: ok`, four tests passed, empirical exit 0 in 40.28 s.

SHA-256:

- analyzer:
  `4147bf09b29a08126676f0846c9aa4ee61935be3f2ded5490257927204c87cc9`;
- tests:
  `d502b84248c731989fea4936c8ba4c30d4e24ac12e5e6ab2d5db08ec9f17e3b5`;
- machine result:
  `ba7ae0eb9985efafddda0d0a52bb1bf02ab701b4137eca893ca02fee77c0359d`;
- source manifest:
  `690934b7ce3cf12a12d4c4cfb716d298d562dfc4a51fbce40d5d31a1adee6a79`;
- per-agent table:
  `c974630dcb95808f928d025bbfd00021e80f2061e391ce084d8cd853eb755873`;
- generated report:
  `8a8657934666dce082bcd5aa5f59d1fba095d7f602e2f4b6175a06a110a36629`.

Resident SHA remains
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
No raw/processed input, resident, sealed source, submission tool, or Arena state changed.
