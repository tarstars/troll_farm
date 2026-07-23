# Ten-idea training-policy sweep

## Protocol

Each idea changes exactly one field in the recovered live agent's `TUNED_CARRY` constant. Stage 1
uses the same 60 generated seeds, both seats, and eight parallel workers. This paired local gate
is a self-harm screen, not an arena predictor. Apparent positive candidates are rerun over 200
seeds before any platform decision.

No idea qualified for a controlled field panel. There were zero field games and zero arena
submissions in this sweep.

## Results

| idea | isolated change | final n | mean margin | wood | W/T/L | decision |
|---|---|---:|---:|---:|---:|---|
| prefer carry 3 | preferred carry 2 -> 3 | 60 | -0.750 | -0.225 | 6/48/6 | do not advance |
| cap carry 2 | maximum carry 3 -> 2 | 60 | -0.525 | -0.333 | 3/46/11 | reject: wood loss |
| prefer chop 2 | preferred chop 1 -> 2 | 60 | -0.100 | -0.025 | 3/55/2 | park: effectively inert |
| cap chop 2 | maximum chop 3 -> 2 | 200 | +1.025 | -0.040 | 35/112/53 | reject: outlier-driven |
| require carry 2 | require preferred false -> true | 60 | -2.450 | -0.150 | 6/46/8 | do not advance |
| extra ETA 8 | permitted extra ETA 15 -> 8 | 200 | -0.480 | -0.125 | 4/189/7 | reject: confirmation flipped |
| extra ETA 25 | permitted extra ETA 15 -> 25 | 60 | -1.908 | +0.008 | 3/53/4 | do not advance |
| deadline 25 | hard deadline 35 -> 25 | 60 | -0.333 | -0.083 | 1/56/3 | reject: wood loss |
| deadline 45 | hard deadline 35 -> 45 | 60 | -0.200 | -0.050 | 0/59/1 | park: inert/negative only |
| movement ties | movement tie preference false -> true | 60 | -0.033 | -0.008 | 1/58/1 | park: effectively inert |

`extra ETA 8` initially read +1.125 over 60 seeds but fell to -0.480 over 200, reproducing the
known small-sample failure mode. `cap chop 2` retained a +1.025 raw mean at 200 seeds, but its
approximate 95% interval is [-1.73, +3.78], its 5%-trimmed mean is -0.703, and it loses more
activated seeds than it wins (35 versus 53). Two outliers at +213.5 and +160.5 contribute +374
of the total +205 margin. It is not a robust promotion signal.

## Verdict

None of the ten one-field training policies improves both robust paired score and wood. Training
constant tuning is closed for now. Preserve the exact live `TUNED_CARRY` policy. A future change
needs a structural mechanism—renewable supply, worker count economics, or opponent-denial
interaction—not another ungrounded opening-constant sweep.

Machine-readable results:
`data/analysis/live-agent-6553250/training-policy-sweep-summary.json`.
