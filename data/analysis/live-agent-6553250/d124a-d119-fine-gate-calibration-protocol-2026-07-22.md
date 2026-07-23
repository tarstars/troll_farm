# D124a D119 fine gate calibration — frozen retrospective protocol

Date: 2026-07-22  
Status: frozen before fine-offset scoring

## Hypothesis

D121 brackets a possible calibration interval for the structurally valid D119 models. Offset
`-0.5` is generally valuable but exceeds the 85% activity ceiling, while offset `0.0` is within
the activity band but lies near the `+2` mean and 40% strict gates. The original `0.5` offset
spacing may skip a useful fixed threshold rather than expose a model-capacity failure.

Reproduce the four exact D119 seed `11901--11904` models and score offsets from `-0.50` through
`0.00`, inclusive, at a fixed `0.05` step. Do not extend or refine the range after seeing results.
Use only the already-consumed 80-map D121 panel and its five fixed 16-map blocks; collect no fresh
simulation.

## Descriptive feasibility gates

A grid point is descriptively feasible only if:

- all unchanged D119 structural model gates pass;
- all unchanged D118 fit-policy gates pass on the original training panel;
- the D123 relative held gates pass on the 80-map aggregate, including crop performance no worse
  than control; and
- mean margin is nonnegative in every one of the five fixed blocks.

Require two complete result artifacts to be byte-identical. A feasible point establishes only that
a calibration band exists in the retired data. It has no qualification authority and cannot select
a checkpoint, justify integration, or authorize Arena/submission. If a stable band exists, the next
experiment must freeze a threshold-calibration rule that uses training data only and evaluate that
rule on genuinely fresh maps. If no point is feasible, close fixed-offset calibration for D119.
