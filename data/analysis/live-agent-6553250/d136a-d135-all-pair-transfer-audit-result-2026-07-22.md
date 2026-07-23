# D136a D135 all-pair transfer audit — result

Date: 2026-07-22  
Decision: **close D135's independent winner-sign BCE gate**

Two four-pair audits are byte-identical (SHA `23b7eccb...`). Each uses about four CPUs and takes
31--32 seconds. No pair passes all consumed-D126 gates:

| Ranker/gate | Held mean | Held floor | D126 mean | Strict | Families | D126 floor | Activity | Outcome |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 13401/13501 | +3.971 | -1.125 | +0.594 | 38.28% | 4 | -5.094 | 81.64% | fail 4 gates |
| 13402/13502 | +3.435 | +0.094 | +1.852 | 39.84% | 3 | -5.125 | 85.55% | fail 5 gates |
| 13403/13503 | +3.908 | +0.828 | +2.473 | 41.80% | 4 | -2.500 | 83.98% | fail family breadth |
| 13404/13504 | +3.596 | +0.141 | +0.355 | 39.45% | 2 | -2.031 | 84.77% | fail 4 gates |

Pair13403/13503 proves another selector miss: it is much better than selected pair13404/13504 and
passes every veto except six-positive-families. It still cannot be rescued because D126 is consumed
and it fails a frozen gate.

Across only four points, held mean is entirely uninformative for D126 mean (`r=0.004`). Held worst
block is weak (`r=0.274`); held family floor (`r=0.684`) and activity (`r=0.694`) are more aligned,
but neither identifies a passing pair. The result therefore diagnoses both selector instability and
an abstraction failure rather than selector failure alone.

The current gate learns each root's selected-winner sign independently, although runtime composes
many roots with first-positive stopping. Its raw balanced accuracy stays near 53%--55%, and it gives
equal classification importance to small and large advantages. The next isolated model hypothesis
should train the same compact winner context at the *task sequence* level: choose one best stopping
boundary (or wait) using exact selected-winner value, suppress earlier/lower roots, and preserve
first-positive runtime. Reuse D133/D126 evidence; do not open final seeds. Result SHA is
`20434c90...`; lock SHA is `ff379ce7...`.
