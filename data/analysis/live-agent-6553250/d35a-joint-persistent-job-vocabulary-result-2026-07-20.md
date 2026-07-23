# D35a joint persistent-job vocabulary audit — result (2026-07-20)

## Verdict

**Reject a flat categorical joint-signature policy; retain the unit-job vocabulary and advance a
centralized factorized assignment interface.**  Discovery misses the frozen top-32 signature
coverage gate at 86.56% versus 90.00%.  The boundary is not waived: D35a does not authorize the
planned flat joint executor.

The failure is combinatorial, not semantic.  Every direct productive command is covered, 98.14%
of discovery and 99.51% of confirmation unit-turns receive a job, MOVE resolution is 96.44% and
99.01%, and median job runs persist six and seven turns.  A scheduler should therefore choose one
role per worker under a shared assignment state instead of classifying the whole variable-size
team into one of 32 signatures.

No new game or seed was opened.  The 21 already-consumed replays were read only; no candidate,
TestSession call, Arena submission, or resident change occurred.

## Frozen gate

| Gate | Discovery, 12 games | Confirmation, 9 games |
|---|---:|---:|
| Replay integrity | pass | pass |
| Direct productive-command coverage | **100.00%** | **100.00%** |
| All unit-turn coverage | **98.14%** | **99.51%** |
| MOVE resolution within 12 active turns | **96.44%** | **99.01%** |
| Median non-idle run | **6 turns** | **7 turns** |
| Top-32 joint-signature coverage | **86.56% — fail** | **95.07% — pass** |
| RENEW share | 61.95% | 62.46% |
| FELL_BANK share | 31.52% | 32.58% |
| PRESSURE or MINE share | 6.36% | 4.88% |
| Multi-worker turns with distinct roles | 62.70% | 63.48% |

Discovery passes nine of ten checks; confirmation passes all ten.  The formal conjunction fails.

## Analysis at different abstraction levels

### Commands

The decoder covers all 9,536 direct productive commands across the two partitions.  Only MOVE
tails remain unknown: 214/11,480 discovery unit-turns and 39/8,011 confirmation unit-turns.  This
is much smaller than the primitive-policy disagreement seen in D11/D21 and shows that job labels
remove most waypoint noise.

### Temporal abstraction

Jobs are genuinely persistent rather than relabeled primitive actions.  Discovery contains 625
non-idle runs with mean length 18.0 and median six; confirmation contains 349 with mean 22.84 and
median seven.  Maximum runs are 299 and 293 turns.  This is long enough for a macro action to
represent location and continuation value that one-action PPO and short residual Monte Carlo
could not retain.

### Joint scheduling

Distinct roles coexist in 62.70% and 63.48% of multi-worker turns.  The dominant signatures are
not all-workers copies: `RENEW/RENEW`, `RENEW/RENEW/FELL_BANK`, and
`RENEW/FELL_BANK/FELL_BANK`.  This reproduces the field archaeology's producer-producer-chopper
structure without hard-coding one fixed workforce size.

### Why the flat catalog fails

Discovery has 176 exact joint signatures.  It includes games with one through seven workers:
weighted turns are 27 / 931 / 1,582 / 661 / 146 / 97 / 127 by worker count.  Merely appending or
removing a worker changes a flat categorical label even when every existing worker retains the
same role.  The outlier seven-worker trajectories make the discovery tail broader; confirmation
has 78 signatures and therefore happens to clear the top-32 gate.

Changing 32 to a larger post-hoc catalog would encode workforce cardinality into class identity,
waste data across equivalent assignments, and fail the next unseen team size.  The gate correctly
rejects that design.

### Role semantics

RENEW and FELL_BANK account for roughly 94% of non-idle work in both partitions.  MINE_BANK is
4.63--5.13%.  Explicit opponent-crop PRESSURE is rare (1.23% discovery, 0.25% confirmation), so it
should be a target-ownership attribute of a fell job rather than a separately learned role class.
MIXED_BANK is also rare and mechanically forced.  Banking should remain executor state, not a
policy decision.

## Next representation

D35b must freeze a **centralized factorized job assignment**:

1. a shared encoder sees all workers, inventory, crop provenance, opponent renewable momentum,
   current assignments, and job ages;
2. an autoregressive or masked assignment head selects `KEEP`, `RENEW`, `FELL`, or `MINE` for each
   worker in stable ordinal order;
3. target selection is separate and collision-aware; opponent-created lineage is a FELL target
   attribute, not a fifth role;
4. BANK, DROP, and continuation to job completion are deterministic executor states;
5. global TRAIN is a separate decision conditioned on accumulated resources and current role
   coverage; and
6. the exact resident remains an explicit full-policy fallback.

Before PPO, D35b must implement the executor and a closed-loop upper-bound/teacher study on fresh
official maps.  It must demonstrate both productivity retention and opponent-score reduction; high
replay coverage alone is not value evidence.

## Reproducibility anchors

- protocol SHA-256:
  `05f282842b6b0e24b771a640a5d10cb96956d9647a5331c81997f78e151a25f8`;
- analyzer/fetcher SHA-256:
  `52b1813380439d4edf447f534faa3c418c8cd3ad7289eaee45e7122f050609e8`;
- machine result SHA-256:
  `c0cdfebaa19ee0ec584b6ebc1a3bdeeac38a6e9003aef13fb81f4b0083b64830`;
- focused tests: four passed.

