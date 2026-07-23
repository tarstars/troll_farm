# D121a D119 retrospective grid audit — result

Date: 2026-07-22  
Decision: **retrospective only; generate a safety/calibration hypothesis, promote nothing**

D121 exactly reproduces all four D119 model hashes, then scores the frozen 24-policy grid on the
consumed 80-map/1,280-task panel and each of its five 16-map blocks. Validation transfers
meaningfully: Pearson correlation is `0.795` for mean margin, `0.801` for worst family, `0.992`
for strict-improvement rate, and `0.995` for intervention rate. The architecture's behavior is
therefore stable enough to improve rather than discard.

The validation-locked seed-11901/offset-0 policy has `+1.845` aggregate mean, 40.47% strict gains,
79.61% activity, `+0.871` own score, `-0.974` opponent score, seven positive families, a `-0.444`
floor, and unchanged workforce. Every block mean is positive (`+1.074`, `+1.934`, `+1.824`,
`+1.699`, `+2.695`; standard deviation `0.519`). It fails the old held policy gates only on mean
(`+1.845 < +2`) and crop creation (1,278/1,280 = 99.844%). It ranks eighth by aggregate mean and
nineteenth by the raw robust order.

No one of the 24 candidates descriptively passes every old held gate. Seed11903/offset-1 has the
best mean and raw robust key at `+2.953`, 45.39% strict gains, six positive families, and a
`-2.663` floor, but acts on 88.75% of tasks and shares the same two crop failures. At offset -0.5
it remains `+2.630` with 87.27% activity; at offset 0 it drops to `+1.913` and 39.77% strict gains.
The grid exposes a coarse calibration gap around the 85% activity boundary.

The evidence points to two concrete D122 targets, not more epochs or a larger generic model:

1. trace and eliminate the two systematic crop-destroying interventions with an observable-state
   safety rule or supervised safety head; and
2. improve act/wait calibration around the useful seed11903 frontier, prospectively on fit data,
   rather than choose a held-derived intermediate offset.

D121 cannot qualify D119 or select seed11903. Its entire panel is now retrospective research data;
future validation/confirmation must use fresh seeds.

Lock SHA-256: `04d7cd158afd70b5e0c14d919ffad275d8c5a64eea041feac4ba5c9ea3f28e07`  
Result SHA-256: `a8dd3842c87fbff226ea26e5b78c1b969689e34785ff3dace78f22a195fc7c6d`
