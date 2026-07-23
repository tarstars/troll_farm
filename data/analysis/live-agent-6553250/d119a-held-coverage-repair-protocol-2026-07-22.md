# D119a held coverage repair — frozen protocol

Date: 2026-07-22  
Status: frozen after the first held mechanics failure and before any repair collection

## Observed mechanical failure

The locked held panel on seeds `9,843,700--9,843,715` produced 256 baselines, 18,659 arms, and
1,165 roots with zero mechanical failures at 33.832 arms/s. It failed only the prospective
coverage gate: 220/256 tasks (85.94%) had a usable forced-control boundary versus the required
90%. The locked policy was not scored, so no policy outcome is available for tuning or selection.

## Fixed sequential repair

Keep checkpoint seed `11901`, gate offset `0.0`, model hash, runtime semantics, held gates, and all
collector settings unchanged. Collect at most four contiguous 16-map/256-task coverage blocks:

1. `9,843,716--9,843,731`;
2. `9,843,732--9,843,747`;
3. `9,843,748--9,843,763`;
4. `9,843,764--9,843,779`.

After each block, combine it with the original held panel and every earlier block. Inspect only
mechanics. Stop collection at the first aggregate panel with at least 90% support and all other
mechanics gates passing. Do not compute teacher or locked-policy metrics before that stop. If
coverage alone still fails after block four, close D119. Any non-coverage mechanics failure also
closes the repair rather than authorizing broader changes.

At the first mechanics pass, evaluate the single locked controller exactly once on the aggregate
panel under the original held gates: mean `+2`, strict 40%, floor `-3`, six positive families,
directional score safety, activity 10%--85%, crops 100%, and workforce within five percentage
points of control. A policy failure closes D119 without tuning. A full pass opens quantized Rust
parity/integration and a separately frozen final untouched confirmation, not submission or Arena.
