# D127a D126 tail attribution — frozen retrospective protocol

Date: 2026-07-22  
Status: frozen after D126 failure and before any D127 threshold score or trace

## Scope

D126 passes every fresh gate except the family floor: norx is `-4.281` and script is `-3.719`.
The 16-map panel is consumed and may now be used only to choose the abstraction of a later repair.
D127 has no qualification authority and collects no new simulation.

Reproduce exact seed11903 and its D126 calibrated offset. On the consumed D126 panel, trace every
chosen intervention with its observable root state, gate logit, ranked proposal, exact terminal
delta, exact best proposal at the same root, and the policy outcome if that chosen root alone is
skipped and scanning continues. Classify negative interventions as proposal-ranking errors when a
positive same-root proposal exists, timing errors when the root has no positive proposal but a
later eligible intervention is positive, or abstention errors when exact D40 control is the best
available fallback. Terminal labels are diagnostic only.

Separately score seed11903 at offsets `-0.10--0.50` inclusive in fixed `0.05` steps on both the
original fit panel and consumed D126 panel. Apply the unchanged D126 validation gates. Do not
extend or refine the sweep. Report any descriptive pass and its fit activity, but do not select it.

Require two complete result artifacts to be byte-identical. If the sweep contains a stable-looking
full pass, design one new training-only activity calibration and test it on untouched maps. If no
global threshold passes, use the loss attribution to define one observable state/action shield.
Neither branch may reuse D126 for qualification, create a checkpoint, integrate code, or interact
with the platform.
