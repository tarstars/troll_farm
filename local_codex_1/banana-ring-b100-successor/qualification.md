# Bounded banana-ring + b100/e6 qualification

- Final state before Arena: `SMOKE_QUALIFIED`
- Arena source: `banana-ring-b100-e6.arena.rs`
- Bytes: `99,990` (`<100,000`)
- SHA-256: `d2d8f65804991fed5ca8cdaacc1b62fd90ab553ee6952c6286029497e525eecc`
- Fallback SHA-256: `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`
- Sacred parent SHA-256: `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

Mechanical gate (`banana-ring-b100-preflight-20260802T-r5.json`):

- 39/39 semantic tests;
- optimized standalone compile and empty-input zero-stderr exit;
- mutated sacred parent rejected;
- research/Arena equality on 8/8 streams and 2,400/2,400 command lines;
- runtime p95 1.727 ms and maximum 5.402 ms.

Paired consumed-seed smoke (`banana-ring-b100-smoke-20260802T-r5.json`):

- 0 plants outside the eligible ring; maximum own planted-banana Chebyshev distance 1;
- maximum 8 concurrent tracked own ring bananas;
- 727 orthogonal ring chop actions and 910 deposited wood increase;
- 0 pre-release diagonal ordinary chops;
- 330 banana DROP actions after a full ring and 0 full-ring BANANA PICK actions;
- no prespecified severe-tail regression versus the live unbounded factory.

The 16-game value summary is intentionally descriptive, not a fit: fallback mean margin `+24.50`,
live unbounded factory `+7.44`, bounded ring `-18.75`. The owner explicitly directed publication
of the corrected bounded behavior; the small smoke's frozen kill condition was severe-tail or
behavioral-invariant failure, neither of which remains in r5.

Closed intermediates are retained in `data/analysis/live-agent-6553250/`: the uncached build failed
latency, and r4 exposed the starter fallback chopping an unripe diagonal mother. r5 adds the
starter guard and is the only submission artifact.
