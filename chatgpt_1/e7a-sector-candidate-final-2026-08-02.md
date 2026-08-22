# E7a sector-conditioned candidate — final packet

- Task: `20260802-e7a-sector-candidate`
- Owner request: incorporate the initial-sector result into the strongest established bot and
  produce one more candidate for submission
- Work owner: `chatgpt_1`
- Host validator/integrator: `local_codex_1`
- Date: 2026-08-02 UTC

## Candidate

Parent — strongest established source:

```text
cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs
62,725 bytes
SHA-256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55
```

Materialized candidate:

```text
cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs
62,820 bytes
SHA-256 97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595
```

Canonical integration commit:

```text
fc77657b42a61ca5f18a749178758c66432f4df4
```

## Exact behavior change

The parent chooses one persistent LEMON/PLUM `typeToCut` species from the initial map by
summing BFS distance from the resident shack doors to all trees of each species. It chooses
the lower sum, with LEMON winning ties.

The candidate returns PLUM only in the frozen exploratory sector:

```text
parent choice == LEMON
AND
plum distance sum - lemon distance sum <= 8
```

Outside that sector it returns the exact parent choice. The change is confined to the complete
`MoisanBot::focus_type` function. Inverse replacement restores the parent byte-for-byte; no
other scheduler, opening, orchard, movement, banking, training, scoring, target grammar,
endgame, announcement, or denial parameter changes.

## Construction and semantic validation

Host materialization results:

- parent SHA and unique source anchor exact;
- candidate delta: +95 source bytes;
- inverse source transform exact;
- frozen census: 13/60 roots selected, 10/13 positive original FLIP signs;
- standalone compilation: pass under `rustc 1.75.0`;
- focused construction suite: 4/4 pass;
- exact bridge: `EXACT_CONTROL_OR_FLIP_BRIDGE`;
- bridge coverage: 8 representative roots × both seats = 16 games;
- inside sector: complete candidate result equals the original full-FLIP arm;
- outside sector: complete candidate result equals unchanged control;
- zero command, stderr, identity, or runtime faults.

Machine evidence:

```text
chatgpt_1/e7a-sector-candidate-manifest-2026-08-02.json
SHA-256 8ec00737776e1a3125c5e50003712c9493ce429390e5b1d4a077e31e98be0cdb

chatgpt_1/e7a-sector-candidate-bridge-2026-08-02.json
SHA-256 4353345b3ef37725263e295fc94d7853d02ce20abc3a3ac92babe41c9c347bc7
```

## Frozen no-fit developmental pricing

After the rule was frozen, the original locked E7 payload was recovered as a trace-free exact
360-row delta table. No threshold, feature, label, or source was changed before pricing.

The pricing reproduces the original E7 anchors:

```text
always-FLIP vs control: -12.173611 terminal margin
positive FLIP roots: 24/60
perfect root hindsight ceiling: +10.509722 terminal margin
```

For the conditioned candidate C1:

```text
C1 - unchanged control:        +4.008333 mean terminal margin
root-cluster 95% interval:     [-1.587500, +13.101458]
bootstrap probability <= 0:    0.16086

C1 - always-FLIP:              +16.181944 mean terminal margin
root-cluster 95% interval:     [+4.729132, +28.668090]
bootstrap probability <= 0:    0.00196

selected-root conditional:     +18.500000
hindsight-oracle captured:     38.14%
```

Breadth:

```text
seat 0: +5.791667
seat 1: +2.225000

chopharvest: +1.325000
motion:      +5.466667
race:        +6.933333
ringfix3:    +0.666667
taskplan:    +6.383333
yield:       +3.275000
```

All six leave-one-family-out means are positive, from +3.423333 to +4.676667.

Score decomposition:

```text
own score:       +0.211111
opponent score:  -3.797222
margin:          +4.008333
wood edge:       +1.068056
```

The candidate therefore appears to work mainly through opponent-score suppression rather than
resident-score sacrifice.

Canonical pricing evidence:

```text
chatgpt_1/e7a-sector-candidate-pricing-2026-08-02.json
integration commit 61d929c7e0dcd3e6a9ad5bf029429d3d64b60bca
```

## Disposition

```text
MATERIALIZED_EXACT_BRIDGE
POSITIVE_CONSUMED_PANEL_HEADROOM
NOT_QUALIFIED
```

The candidate is a complete single-file Rust artifact that can technically be submitted. It
is not scientifically qualified because:

- the sector was discovered on the same consumed 60-root E7 evidence;
- the broad preregistered ridge model failed;
- C1 beats control by +4.01, but the clustered interval crosses zero;
- absolute catastrophe, negative-margin-mass, and win/tie/loss changes are unavailable from
  the compact delta table;
- no fresh root, official-map, capacity A/A, or Arena transfer test has passed.

No TestSession or Arena mutation was performed. Submission remains serialized through
`local_codex_1`; the current live banana experiment prevents an automatic second mutation.
