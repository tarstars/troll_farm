# D120a policy-sealed absolute-information diagnostic — frozen protocol

Date: 2026-07-22  
Status: frozen after D119 mechanics closure and before any D119 checkpoint score on the 80-map panel

## Scope and isolation

D119 exhausted its predeclared coverage repair at 1,139/1,280 supported tasks (88.984%), thirteen
tasks below a 90% fraction, while every other mechanics gate passed. No D119 checkpoint metrics
were computed on the aggregate panel. D120 is a new post-mechanics diagnostic, not a retroactive
D119 held pass. It changes only the definition of sufficient information and uses no new games.

Keep exactly locked:

- seed `11901`, gate offset `0.0`, 6,626-parameter checkpoint, and canonical model hash
  `a2a79d842732acf746225723754ebd3c54d7d95d3eefa43557c10f0f3002903f`;
- first-positive one-intervention semantics;
- all D119 held policy gates; and
- the fixed 80-map panel on seeds `9,843,700--9,843,779`, including valid zero-boundary controls.

Do not inspect teacher or checkpoint-policy outcomes before the absolute-information gate passes.

## Absolute information gate

Retain every exact mechanics gate except the failed fractional support gate. Require all of:

- at least 1,024 supported tasks overall;
- at least 128 supported tasks in each of eight opponent families;
- at least 512 supported tasks in each seat and each interleaved map fold;
- at least 5,000 roots overall and 500 roots per opponent family; and
- at least 80,000 arms overall and 8,000 arms per opponent family.

These floors guarantee large absolute samples and stratum balance without requiring the random
availability rate to cross 90%. Failure closes D120 without policy scoring.

## Single policy diagnostic

If information passes, score the one locked checkpoint exactly once on all 1,280 tasks, treating
zero-boundary tasks as forced control. Require the unchanged held gates: mean at least `+2`, strict
improvement at least 40%, worst family at least `-3`, at least six positive families, directional
score safety, activity 10%--85%, crops 100%, and worker-three reach within five percentage points
of control.

A policy failure closes the branch without tuning. A full diagnostic pass opens quantized Rust
parity/integration and a genuinely fresh final confirmation protocol. It does not itself authorize
TestSession, Arena, submission, or resident mutation.
