# D105b fresh-map proposal readout — result

Date: 2026-07-22  
Decision: **support fail; stop before terminal value or fitting**

## Outcome-blind result

The unchanged D97 generator finds 233 eligible roots on fresh seeds 9,826,000--9,826,015, above
the frozen 220 minimum. The locked q4 bank yields 14,912 expert/root proposals and a deduplicated
4,264-arm manifest including one exact control per root.

The union itself transfers broadly:

- 17.300 unique noncontrol proposals per root on average, minimum eight and maximum 28;
- a joint proposal at all 233 roots;
- 2,720 joint, 787 first-only, and 524 second-only selected arms;
- all four jobs, natural/own/opponent/ambiguous provenance, both seats, all eight families, and
  reversed worker-role order.

One frozen support gate fails: only 47 experts, versus 48 required, emit a noncontrol proposal in
at least 25% of the 233 roots. The exact threshold is 59 roots. The 48th most active expert reaches
52 roots, so this is not a rounding-boundary ambiguity.

## Measurement amendment

The fresh panel contains 233 rather than the original D97 panel's accidental 240-root count. The
frozen D104 runner aborts on that historical assertion before writing output. A preregistered
measurement-only adapter clones seven ignored replay roots, runs the unchanged binary at 240, and
then strips every clone. The retained matrix is exactly 233 x 64; clones cannot enter support,
terminal arms, or fitting. All adapter, grid, source-hash, and union-lock integrity gates pass.

## Decision

Per protocol, no D105b terminal continuation was executed and no outcome or readout was opened.
This result says nothing about fresh-map value. It says the four-bit bank sits exactly on its old
individual-activity boundary and does not reproduce that boundary prospectively, despite retaining
excellent union-level diversity.

Do not weaken the 48-expert gate or evaluate the locked q4 union after this result. The next
eligible discriminator is a new-map, outcome-blind six-bit precision adjudication. Six bits still
pack into only 9,180 base85 bytes and should distinguish whether four-bit rounding caused the lost
individual activity. Only if q6 prospectively passes the unchanged support gates may its terminal
headroom and held proposal readout be opened.

No candidate, platform action, submission, or resident change occurred.
