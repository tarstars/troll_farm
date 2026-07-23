# D64i worker-two tail audit result (2026-07-21)

## Verdict

**All four D64 safety failures are uniformly `source_availability`.** They are not TRAIN execution,
shack evacuation, carried-stock materialization, or transaction failures. Exact D40 never reaches
a state where bank plus carried stock plus all currently ripe board fruit can cover the worker-two
producer bill.

The only eligible repair is missing-resource source access before worker two. Do not change TRAIN
execution or retune late capitalization from this audit.

## Integrity

- Two 440-row traces are byte-identical, SHA-256
  `c136875412132f45f903bbe1e5ffdbbc448a894b06dc41d81d63c43c525ab7a3`.
- All four target and four matched-control tasks are present.
- Decision indices, state/turn chains, and cumulative action hashes are exact.
- Mechanical, provenance, and deposit-prediction failures are zero.
- All targets reproduce terminal one-worker failure; all same-map `gold_adaptive` controls create
  worker two at turns 65--86.

## Exact blocker by map

### Seed 9,830,002: LEMON disappears from the feasible stock set

Both seats start three PLUM and one LEMON short. Exact deficit work banks the missing PLUM by turn
46, but LEMON remains one short for the entire game:

- maximum deposited LEMON is 4 against a required 5;
- maximum carried LEMON is zero at decision boundaries;
- two LEMON plants exist, but maximum ripe LEMON is zero;
- bank + carry + ripe minimum LEMON deficit remains one; and
- D40 executes 44/45 BANANA renew jobs after the missing LEMON becomes the sole blocker.

The matched controls see ripe LEMON, execute LEMON/PLUM harvest-bank work, and reach deposited
`PLUM=5, LEMON=5` before worker two at turns 71 and 65.

### Seed 9,830,014: contested PLUM vanishes while LEMON compounds

Both seats start two PLUM short. Under `resident`:

- maximum deposited PLUM remains 3 against a required 5;
- maximum carried PLUM is zero;
- one seat briefly sees one ripe PLUM and its harvest job is invalidated; the other sees none;
- bank + carry + ripe minimum PLUM deficit remains one/two; and
- D40 executes 31/35 RENEW jobs, overwhelmingly on LEMON, while the PLUM bill remains open.

The matched controls harvest PLUM successfully and train at turns 70 and 86.

## Why the existing scheduler stalls

D40 can only create a source by `HARVEST -> PLANT`: its `RENEW` job requires already-ripe fruit.
When the opponent removes or wins the only missing-species fruit, the candidate set contains no job
whose predicted deposit reduces that bill coordinate. The work-conserving fallback then renews an
abundant different species forever. It creates 31--45 crops but cannot manufacture the missing
training currency.

This explains why crop count is not renewable sufficiency. The controller has a productive-looking
orchard while one exact currency coordinate is extinct.

## Decision

Freeze D65a as one coefficient-free source-access repair on the complete D40 substrate:

1. only with exactly one worker and a pending producer bill;
2. only when bank + carry + ripe board stock cannot cover a positive fruit deficit;
3. choose the largest uncovered fruit coordinate, breaking ties PLUM, LEMON, APPLE, BANANA;
4. invest one deposited seed of that species into a player-favored empty source cell;
5. return immediately to unchanged D40 after the source is planted; and
6. never activate when the bill is executable or an existing ripe acquisition can cover it.

First require exact D40 parity when inactive and recovery of all four consumed target failures.
Then test safety on fresh maps with a universal worker-two/crop gate before reading value. Do not
reuse D64 outcomes for selection, add source-count weights, alter the worker spec, or modify late
scale.

## Reproducibility

```text
6e90ab0955e9c3404900ed02832ca9452206e9cef351cac7a388a4d1437ea24f  d64i-worker-two-tail-audit-protocol-2026-07-21.md
3f79e8c31a98859fa991a1a23fd60159b64f9f66eb23a6a4868597ff359075ae  rust/src/bin/d64_worker_two_tail_audit.rs
08154b22ef6fc8a22129e83a276144b6498578f5026f7b6199e70a8c617d02fb  cgauto/analyze_d64i_worker_two_tail.py
c136875412132f45f903bbe1e5ffdbbc448a894b06dc41d81d63c43c525ab7a3  each repeated trace
7bec01c91230fd02373e22d02391ec57ec9bfce77bbfcf72a6b3ea223e44c606  d64i-worker-two-tail-result.json
```

