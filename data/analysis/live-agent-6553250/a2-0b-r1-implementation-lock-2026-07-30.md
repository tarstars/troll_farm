# A2-0b r1 implementation lock

Status: **LOCKED BEFORE CONFIRMATION**
Locked UTC: 2026-07-30T16:04:00Z

The exact remotely verified implementation commit is
`cd424a19a1f746d72afcfc8b7c824284cdda4012` on both
`agent/local_codex_1` and `session-2026-07-01`.

The fixed 16-map development gate passed before this lock:

- 256/256 terminal tasks;
- zero critical and zero unclassified issues in both modes;
- all issue ownership/reason/phase partitions exact;
- 18/18 focused referee-parity tests and 2/2 official-map tests passed;
- analyzer compile and self-test passed;
- a 16+16-task trajectory probe decoded exactly and ran all six standing detectors
  without error.

The binding machine-readable lock is
`data/analysis/live-agent-6553250/a2-0b-r1-implementation-lock.json`. It freezes the
three protocol documents, Rust crate manifests, isolated A2 sources, historical engine
and generator, resident copies, all eight-family runner dependencies, analyzer, detector
library and its decode dependencies, the implementation commit, toolchain, development
evidence, and release binary.

Notable immutable anchors:

- A2 referee layer:
  `518c222881ac23f8548cc13c858bacc93577ea920ecfbdbf0fd0e588cad1bf83`;
- A2 runner:
  `1054a047a410b23ca952e3ed6b96df12662615bb630597f68b1d551b9b056a3f`;
- A2 analyzer:
  `f7cfc60df0c67ca001140e9c31df3807421178dead0c6d249b8ead551dc84681`;
- release binary:
  `ba1e0ec98a5530f1c75177963b4616cda0e3213e3eeb50573a0c5523182f604b`;
- historical engine:
  `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`;
- historical official map generator:
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`;
- both resident copies:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- standing detector library:
  `cb5c813d591f3defd3809f97b25b61f6c7cdf67f039836d7b43c0544d29cad02`.

Any change to a locked source or dependency invalidates the confirmation. The only
authorized next execution is the consumed 128-map calibration at one and 20 threads,
with the 20-thread run dumping 2,048 legacy and 2,048 referee trajectories after the
external-storage preflight. No Arena, TestSession, submission, sealed-range, raw-game, or
collection-cron action is authorized.
