# D116a repair 1 — validation task support

Date: 2026-07-22  
Status: frozen before repaired validation collection or validation candidate scoring

The original fresh ten-map validation panel on seeds `9,843,630--9,843,639` produced 160
baselines, 793 roots, and 12,969 arms in 612.468 seconds. It supported 141/160 tasks (88.125%),
below the frozen 90% floor by three tasks. Every other frozen mechanic passed, including the
600-root and 6,000-arm floors, exact features and counterfactual accounting, zero failures, and
21.175 arms/s.

The failed mechanics result has SHA-256
`dd8fff9fbf3f041ec2d2b9e9bf8565cdf43ee96cc8e7e3a4f89367a616e0b536`; its arm and baseline
hashes are `999bc3988efce31ea5df0c9a2086fce53452b3c724e4f60f7bf07c82ddcf660e` and
`85e7c9d01604ac335923084f89dc2bcf15d19c89cb4b964651ba92fd54e0c4a5`. The generic panel decoder
computed teacher summaries, but the mechanics gate produced zero validation candidates, no
selection, and no checkpoint. Training-only D116 smoke fits existed before collection, but no
D116 model was evaluated on this failed panel. Quarantine its teacher summaries from the repair.

Do not lower the support floor or append tasks to the failed panel. Collect a wholly fresh
balanced 16-map panel on unused seeds `9,843,650--9,843,665`, both seats and all eight opponents:
256 tasks. The larger independent panel reduces ordinary map-level support-rate fluctuation.
Keep the collector, mechanics, model architecture, fixed WAIT formulation, root-wise loss,
training seeds and epochs, offset grid, admission gates, selection order, and conditional held
range unchanged.

No branch opens held data, TestSession, Arena, submission, or resident mutation.
