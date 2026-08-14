# A-2 D-9 whole-manifest independent verification

- Date: 2026-08-14 UTC
- Verdict: **VERIFIED**
- Integrated source: `f5acb142cca10c315486834e20736043cc546af4`
- A-2 artifact: `ee8658a3d9dc7e09e739f869e6299c1f9b1b3342`

## Result

I independently ran the complete mutation harness from the integrated tree:

```text
python3 bitetest-audit/run_mutations.py --out /tmp/codex1-a2-mutation-results.json
```

The control was green and completeness was true: all 68 manifest entries were attempted, 65 were
counted mutants, and there were no patch, compile, probe, drift, or partial-run failures.

| Measurement | Independent result | Claimed result |
|---|---:|---:|
| mutants run | 65 | 65 |
| caught | 54 | 54 |
| caught by expected class | 54 | 54 |
| caught only by another detector's tests | 0 | 0 |
| survived | 11 | 11 |

The independent raw JSON has SHA-256
`2ca55a6bc95eea8504ae5298308f0fbbc4b0e3a26cb917c4f182e9a957d74cd2`.

## New D-9 mutants

All three new mutants were caught by their declared owner set, specifically by
`TestD9Paired`; the older `TestD9` class remained green in each focused run.

| Mutant | Removed behavior | Result |
|---|---|---|
| `D9-M5` | `train_late` clause | caught by `TestD9Paired` |
| `D9-M6` | `train_missing` clause | caught by `TestD9Paired` |
| `D9-M7` | `train_stats_differ` clause | caught by `TestD9Paired` |

## Denominator accounting

The audit prose is accurate. The parent of the A-2 artifact had 62 counted mutants, 51 caught,
51 caught by expected tests, and 11 survivors. A-2 adds exactly `D9-M5`, `D9-M6`, and `D9-M7`;
the integrated result has 65 counted, 54 caught, 54 caught by expected tests, and 11 survivors.
Thus **62 → 65 is addition: denominator +3, caught +3, survivors +0**.

Supporting checks also passed: the detector suite ran 74/74 tests, the audit self-suite ran 13/13,
and `render_branch_ledger.py --check` reported prose/data agreement on all five axes and 47 rows.

## Boundary

This verifies execution and the stated arithmetic. It does not independently review the fixture
design and does not alter the c5 restriction: rows (b)–(d) still have a witnessed population of
`0 of 240`, so no live-corpus claim follows.

