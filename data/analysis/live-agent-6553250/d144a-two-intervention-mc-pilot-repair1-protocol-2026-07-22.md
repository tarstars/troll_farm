# D144a two-intervention MC pilot — infrastructure repair 1

Date: 2026-07-22  
Status: frozen after failed operation `ada44f3b-2c9a7e95-42e03e8-501288eb` and before creating the
repair YT namespace or operation

The original frozen operation allocated `mc-b`, then exited in 0.057 seconds because the Jammy
worker's `/usr/bin/python3.10` does not contain NumPy. It produced zero YT records. The scheduler
retried once and stopped at the frozen failed-job limit. No simulation ran and no target outcome
was observed, so this is an infrastructure-only repair under the original protocol.

Package the already-tested NumPy 2.2.6 Python 3.10 runtime (`numpy` plus `numpy.libs`) as the
deterministic 19,101,908-byte archive
`data/analysis/live-agent-6553250/yt/d144a-numpy-2.2.6-py310-runtime.tar.gz`, SHA-256
`7ef9f486b6824ef3f46c7f88bec9f033575c86f0f3f2ba37dc6943f46f8678d8`. Upload it as one local
file, path-check and extract it inside each worker layout, and prepend only that extracted
directory to the child `PYTHONPATH`.

An isolated no-site import check returns NumPy `2.2.6` and a working native array. The complete
repaired worker layout repeats the excluded one-map MC output byte-exactly at the original
`2dda090c...` SHA. Thus the package repair changes availability only, not schedules, actions,
environment state, terminal bytes, target panel, replicas, thresholds, or decisions.

Use the same corrected root `//home/delivery_ml/research/tarstars/troll_farm` and a new build
`d144a_two_intervention_mc_9844128_9844135_repair1_20260722`. Retain exactly the original four
specs, resources, reconstruction, mechanics, value, and safety gates. The original failed build is
immutable provenance and must not be reused or removed.
