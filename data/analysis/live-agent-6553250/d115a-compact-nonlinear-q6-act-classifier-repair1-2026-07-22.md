# D115a repair 1 — validation root coverage

Date: 2026-07-22  
Status: frozen before repaired validation collection or first D115 fit

The original untouched validation collection on seeds `9,843,600--9,843,607` produced 128
baselines, 582 roots, and 9,541 arms in 334.154 seconds. Every integrity, support, throughput, and
safety mechanic passed except the prospectively frozen minimum of 600 roots. The exact failure
result has SHA-256 `b862a1c5eccbd920a46a1aa2e9432e3a6184d917f3262414ca3cf7e6d5a695b6`;
its arm and baseline hashes are `8861dffaba780745c2d43be3ec87fded18d8eeab45a8e57dff32db5d8d07844c`
and `6b385d2134c9dbdb13d478a2ca9157d847f32ea441b80c6a2c08474284c9265b`.

The generic panel decoder computed teacher summaries while checking mechanics, but the failed gate
prevented all D115 training and candidate evaluation: the result contains zero trained models,
zero grid candidates, no selection, and no checkpoint. Those teacher summaries are quarantined
and do not influence this repair.

Do not waive or lower the 600-root gate. Discard the failed panel for selection and collect a new,
independent balanced ten-map panel on unused seeds `9,843,610--9,843,619`, both seats and all eight
opponents (160 tasks). Ten maps preserve equal interleaved folds and add coverage margin against
ordinary root-count variation. Keep the collector, 12 arms/s floor, 90% support floor, all
mechanics, architecture, four training seeds, 40 epochs, objective, six logit offsets, validation
admission gates, selection order, and conditional held range exactly unchanged.

No branch opens held data, TestSession, Arena, submission, or resident mutation.
