# D109a duration-only recurrent q6 PPO — result

Date: 2026-07-22  
Decision: **mechanics/safety pass; signal/value fail; close duration-only recurrent q6**

## Execution

D109a completed the prospectively frozen 64,800 transitions and 54 PPO updates from scratch. It
used untouched seeds `9,835,000--9,835,127`, produced 19,692 paired episodes, and trained in
1,193.97 seconds at 54.27 transitions/s with 12.94 effective CPU cores. All losses and parameters
remained finite; 63/64 noncontrol representatives were explored; paired reward error stayed below
`1.1e-5`; and no illegal action, direct-command failure, provenance failure, or deposit failure
occurred.

The unchanged 10,725-parameter model has actor L2 drift 2.532. It changes 249/256 frozen probe
choices and finishes with 17 distinct probe actions. Training preserves crops on every completed
episode. The aggregate training return is `-3.723` versus exact D40, and the final rollout is
`-2.441`; the temporary update-30 improvement to `-1.213` does not continue.

## Held evaluation

Both complete 1,536-row evaluation matrices are byte-identical with SHA-256
`b130cf46bfdcc10b5472b1c6b8ba12afa62df7108407739ccd8232e4d2bd4e99`. All 512 control,
initialized, and final tasks preserve crops, stay within 0.20 percentage points of D40's 88.67%
worker-three rate, retain exact paired rewards, and have zero mechanical failures.

PPO improves the identically initialized actor by `+5.303` and strictly beats it on 49.80% of
tasks. The final actor nevertheless reaches only `-0.150` versus D40, with 41.21% strict wins. It
intervenes on 461/512 tasks (90.039%, one task beyond the frozen signal ceiling), and repeats on
76.17%.

Five families are positive:

- legend_balanced `+3.125`;
- mybot `+2.969`;
- compact_gold `+2.344`;
- resident `+0.500`; and
- gold_adaptive `+0.297`.

Script_boss is `-0.688`, norx_native_three `-1.875`, and silver_boss `-7.875`. Thus the mean-gain,
six-positive-family, and worst-family gates fail. The policy reduces opponent score by `4.143`,
but reduces own score by `4.293`; it has learned nearly symmetric score suppression rather than
positive-margin production. No checkpoint, action trace, or held decision is a candidate.

## Causal conclusion

Duration is not the missing variable. D109a supplies 4.05 times D108a's transitions with the same
architecture, initialization, optimizer, action representation, and paired-margin objective. It
again learns a large, safe change from initialization but converges near D40 instead of capturing
the large q6 oracle headroom.

The family pattern also rotates rather than stabilizes. Across D108a and D109a's independent held
panels, family means have Pearson correlation `-0.014`, mean absolute change `4.631`, and three sign
flips. Script_boss improves by `+13.031` and resident by `+4.781`, while silver_boss loses
`-11.750`. Because panels differ, these are not paired improvements; they are evidence that the
single mean-margin policy trades opponent families against one another.

Close duration-only recurrent q6. Do not extend, continue, select, or tune either checkpoint on
their consumed held panels. The next experiment should isolate objective interference on new maps:
retain exact D40 fallback and the q6 executor, but train with family-balanced/robust returns and an
own-score protection term, then use explicit family slices only for diagnostics. If opponent style
cannot be inferred reliably from deployable observations, move to counterfactual supervised action
values rather than adding hidden simulator-only opponent identity.

Result JSON: `22ebe0a9bf3f992e0ed88d92cbbbf1e4b7a8fb1ed635e8d8737a804eeb469e1f`  
Checkpoint: `2263936899ced97bfe49cc802666c9876a7849ce806f476819b71cfb301370f6`
