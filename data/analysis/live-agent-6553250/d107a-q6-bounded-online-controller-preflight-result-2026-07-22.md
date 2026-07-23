# D107a q6 bounded online controller preflight — result

Date: 2026-07-22  
Decision: **full pass; open D108a recurrent masked whole-game controller**

## Integrity and reproducibility

The two independent 20-worker runs each contain 128 D40 baselines and all 16,512 controller/task
rows. Population outputs are byte-identical with SHA-256 `115d820e9f79efb80d794211a4e1a1aea740bfdf8656dbf6322c6f78601d26dd`;
baselines are byte-identical with `513a5f47b386993d34a6e4005891043b8eac2b9f2711515c994c34e64d3cee7c`.

All zero-controller terminal fields and action-plane counts exactly reproduce D40. Every episode
has zero reward-identity error, invalid direct commands, provenance failures, and deposit failures.
All proposal, endorsement, intervention, job, and budget counters reconcile. Crop creation is 100%
for D40, one-use, and four-use populations; all three have the same 89.844% worker-three rate.

The original runner omitted only the per-boundary minimum support counter. The frozen zero-only
measurement amendment adds it and reproduces every shared zero-row field and the baseline file
exactly. Its 128-row audit hash is `06d53fd74fb6d602d02874e6d9ddab0b99e663051e6de855cff02247ef21ba69`.

## Online action support and activity

- 119/128 exact-D40 trajectories expose eligible two-worker boundaries, totaling 647 boundaries.
- Q6 supplies 15.910 unique noncontrol proposals per boundary on average, never fewer than six;
  all 64 expert endorsements reconcile at every boundary.
- 63/64 four-use controllers intervene somewhere; 44 lie in the frozen 10%--90% task-activity
  band.
- 50 controllers use two or more interventions on at least 10% of tasks.
- 62/64 matched pairs have more total interventions under budget four than budget one.
- Selected trajectories span joint actions, all four jobs, natural/own/opponent provenance, both
  seats, and all eight opponent families.

Every frozen activity gate passes. The abstaining score interface is neither inert nor saturated,
and the four-use authority produces genuine repeated decisions rather than merely relabeling the
one-use controller.

## Conditional population headroom

The unselectable four-use population oracle gains `+35.227` mean margin over D40 and strictly
improves 116/128 tasks (90.625%). Every opponent family is positive; the worst is resident at
`+17.625`, followed by mybot at `+20.688`. The oracle adds `+21.586` own score while removing
`13.641` opponent score.

The matched one-use oracle gains `+31.469`. Four uses add another `+3.758` mean margin and strictly
beat one use on 58/128 tasks (45.313%), passing both prospective repeated-value gates. Winners span
49 controllers, all four jobs, three provenance classes, both seats, every family, and 203 joint
interventions. Crop creation and worker-three reach remain exactly at D40 levels.

These are population-oracle diagnostics, not a new policy. No random controller or per-task winner
is eligible for deployment or imitation.

## Interpretation and next move

At the mechanics level, the compact q6 bank can be reconstructed repeatedly inside complete games
with exact D40 fallback and deterministic action traces. At the representation level, the 379-field
proposal ABI provides broad, graded authority without collapsing to always-act or never-act. At the
strategic level, repeated closed-loop interventions add prospective value beyond the already strong
one-deviation basis.

Freeze this executor and proposal ABI. D108a should train a small recurrent masked controller
directly from whole-episode paired margin: action zero is exact D40; nonzero actions select one
representative expert per deduplicated live proposal; authority is capped at four noncontrol
batches. Use new training and validation maps, keep D107a entirely diagnostic, and require held
improvement and safety before candidate construction or platform action.

Analyzer: `b055959dd97ccde2fa85f4477b8b761f22a649300ed8b00b69e87d0b92641a93`  
Result JSON: `8ab7ca603686cf4bf26e6026429f7df57fc395242bdb4d8606a10c1b28c989c2`
