# D100a D98-anchored pair-residual implementation lock

Date: 2026-07-22  
Status: locked before any D100 policy reached terminal state on the frozen outcome maps

The D100 evaluator preserves each frozen D98 policy as its exact parent and permits a random
residual policy to replace at most one same-turn two-worker assignment. A candidate pair is scored
from its 342-feature embedding minus the exact parent's pair embedding; the parent has residual
score zero and remains selected unless an alternative has a strictly positive score. Parent and
zero-residual rows execute the exact parent path directly.

Pre-outcome validation completed:

- `rustfmt --check` passes for the D100 evaluator source;
- all 153 parent and 342 pair-feature slots are finite and match their frozen layouts;
- previewed first assignments match real same-turn environment state and action catalogs;
- the D40 control reproduces exact D40 terminal behavior;
- a zero residual chooses the exact parent pair; and
- a complete zero-residual episode reproduces its exact D98 parent.

All six release-mode unit tests pass. A 3,088-row old-map smoke test completed at 52.006 episodes/s
and showed exact D40/baseline parity, zero parent/zero terminal parity failures, and zero accounting
failures. This smoke set is outside the frozen D100 outcome maps.

The independent frozen D98 reference run on maps `9,823,000--9,823,007` completed after the
implementation was fixed. Its files were hashed but its terminal values were not opened before
this lock was written.

Reproducibility anchors:

- outcome-blind population lock SHA-256:
  `2abb732a5fb4283600241f7d6936cdfa89bda6598ed102e24223ebe8db2b6cb6`;
- evaluator source SHA-256 after `rustfmt`:
  `1e262d68dcda93bf0b6a8ce14272cb5c492274ae20aa8645b915e1d82c1a7447`;
- D100 release binary SHA-256:
  `3f1f2a3e2917d01a8c4d8b63525320e112e57eaa6711d403dc458303fdcf2b92`;
- pair-preview environment SHA-256:
  `1e3af47fe25184790763a7dbf11818944c583794303bb986f1db28708179a2e5`;
- exact-prior kernel SHA-256:
  `632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`;
- frozen D98 release binary SHA-256:
  `1e660c8c4615b646f0cc3a190746b2af0e821dea309a34f748f88901249493eb`;
- frozen D98 reference population output SHA-256:
  `d741d502f8105af88c7495eb25c99d890fe213f5c17eaef942c9260a365ad335`;
- frozen D98 reference baseline output SHA-256:
  `b9cf5ffda4f853efe0441f5d72f75876dac8497bbb610bd730ce2994d828b01d`.

The implementation is immutable for D100. A mechanics or integrity defect may be repaired only
under the unchanged protocol, population, reference binary, and outcome maps, with the repair
explicitly logged before repeating all affected rows.
