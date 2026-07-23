# D98a bounded joint-assignment population lock

Date: 2026-07-21  
Status: locked before any D98 policy reached terminal state on the frozen outcome maps

The D98 protocol, random population, generator, and evaluator implementation are frozen before
opening official-map seeds `9,821,000--9,821,007`. The population contains one exact-zero control
and 64 matched weight vectors, each instantiated once with intervention budget one and once with
budget four. No outcome, terminal score, policy rank, oracle winner, or favorable task was used to
construct, reject, reorder, or alter a vector.

Pre-outcome checks completed:

- the population reconstructs exactly from NumPy PCG64 seed 9801;
- all one/four pairs have identical 153-value weight vectors and exact budgets one/four;
- the evaluator's 153-feature layout test passes with every slot finite and populated; and
- its zero-policy unit test reproduces exact D40 terminal and action behavior.

Reproducibility anchors:

- protocol SHA-256:
  `6573a30310a55db9808568b3f2f0d8e03eb8c9baafe3b54aea91a7d6d4c8bad7`;
- population generator SHA-256:
  `1594ac5b049aec68fdee3b7b43ab05a838c21f6c22d41a49a86cfb1358d083fe`;
- population SHA-256:
  `3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e`;
- evaluator SHA-256 after `rustfmt`:
  `49a2c204ec1df3aaf79facdcd39e44cd250458535494a8cf4b6b8de1ff077dfd`.

The four artifacts are now immutable for D98. A mechanics or integrity defect may be repaired only
under the unchanged protocol, population, and outcome-map set, with the repair explicitly logged.
