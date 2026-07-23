# D47b persistent-producer development — result (2026-07-21)

## Verdict

**Reject persistent producer roles and keep confirmation sealed.** The candidate remains
deterministic, mechanically clean, and strongly active, but it loses **12.016 paired margin** to
D40 on 512 fresh tasks. It lowers own score by 7.832, raises opponent score by 4.184, improves only
one of eight opponent families, and worsens both tail measures.

Do not exempt one producer, add a phase cutoff, weaken the role, reverse the rule, or inspect the
confirmation bank. Seeds 9,784,000--9,784,031 remain untouched.

## Development result

- candidate A/B are byte-identical across all 512 tasks;
- zero mechanical or arithmetic integrity failures;
- 17,263 eligible decisions and 4,718 overrides;
- 407/512 changed action hashes (79.49%);
- paired mean / 5%-trimmed margin delta: **-12.016 / -11.615**;
- 32-map normal 95% lower bound: **-16.863**;
- own/opponent score delta: **-7.832 / +4.184**;
- positive opponent families: **1/8**, worst family `mybot` at **-32.203**;
- worker two / worker three / crop: 97.66% / 90.23% / 100%;
- catastrophes: 79 candidate versus 74 D40;
- negative-margin mass: 17,776 candidate versus 15,162 D40.

Nine value, breadth, and downside gates fail. The workforce and renewable-crop mechanisms remain
intact, so the loss is not a failure to activate or fund. Persistent renewable ownership itself
discards useful state-dependent rate choices.

## Interpretation

D46 and D47 jointly reject hard role overrides as the missing D40 improvement:

1. the designated chopper already chooses `FELL_BANK` whenever it can, so forcing that role is an
   exact no-op; and
2. forcing the complementary workers onto `RENEW` is broad but harmful to both production and
   suppression.

D40's action vocabulary and adaptive rate comparison are useful. The remaining tunable mechanism
is its literal economic calibration: base predicted reward per ETA plus fixed 20,000/10,000
opponent/ambiguous provenance bonuses, 15,000 renewable bonus, and 8,000 bank bonus. D45a perturbed
normalized post-ranks and contained dead coordinates; it did not change these actual formula
constants. D48a should test a new three-scale formula surface—linked provenance, renewable, and bank
bonuses—anchored exactly at D40 on consumed maps. Only an active, bidirectionally outcome-sensitive
surface may open whole-game cross-entropy search on fresh maps.

## Evidence

- protocol SHA-256:
  `d26bcdcaada549fd904090611f1ee358f1ce4934ca8e3c5932c6c6db4e1af3b2`;
- activation result SHA-256:
  `59e9f49b58d80b4592d84d113b4a5eb25f536a91a195cbcb6e36a772c60383b5`;
- control TSV SHA-256:
  `7003a60b2fad16a7130a35e4c3b60fc450f504bc0222b8fb26d7032996f41898`;
- candidate A/B TSV SHA-256:
  `b223cfb8b6a8e6e4fe955a32b01ac8c2bb4c5f4985635a745194cf46d4380a74`;
- result JSON SHA-256:
  `9c2aade6ad3705b6ef6f1e39f0ffee782d814aab377b710eb5d855a233333e01`;
- runner SHA-256:
  `aea0248247d8ebffd38a4d1d168f66b1c6455db63224f0f8d1157d73528deed9`;
- analyzer SHA-256:
  `57c923e193e275d320688d69611a3381f8cdff463b3072841333b6d9c2ed1cd6`;
- focused verification: two Rust runner tests and six D47 analyzer tests pass.
