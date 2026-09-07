# Primary review — 2026-09-07

PARK exact candidate 5af6d9c57aa46c22f70b5fe02e8371fda7ba09bb65d8cdf31108ad63db18cafa.
Actual Rust1.90 compiled generated tests; independent run:25 passed,0 failed.
Parsed192 unique map/seat/opponent rows; all192 baseline command arrays match
gap20260906T210944Z-3184968-1. Parent167/6/19=170points, candidate139/0/53=139;
issues1 vs0. Independent compact count102712UTF16: exceeds100000. Running the
panel despite this failed prerequisite violated the ticket; results are diagnostic.
Canonical bot44e3daca and submission7f61a6cd remain unchanged.

Next implementation is NOT export-only cleanup. Source inspection shows an
economically missing action family: plant_job values want-1 fruit, want=min(cc,MAX),
so cc1 gets zero value. jobs_for only offers Plant when harvest_power>0. All new
hires here are hp0; starting cc1 cannot profit under this fruit-only calculation.
Panel confirms candidate ring_plants=0 versus parent1197, wood/game33.3646 vs42.4479.
This supports testing regenerative wood production, not a claim it explains the
entire81.48-point mean own-score deficit. Missing fruit production also matters.

Verified official local Java engine/task/PlantTask.java and PickTask.java: neither
requires positive harvest power. They require grass/no existing crop/seed and
capacity/bank stock/near shack respectively; both require league2. Local full
planning_model/parity.rs agrees. hp0 must not HARVEST, but may PICK/PLANT.

16-stream JSON reports original/pruned/compact equality on4312 turns and max1.023ms.
Source of latency tool checked: it measures readline after flush, but lacks explicit
EOF, exit-code, stderr and per-read timeout assertions. Do not treat its assertion
len(outs)==turns as full protocol certification: blank EOF appends would still count.
No full160-stream certification or platform evaluation authorized for this loser.

Decision: retain movement/ledger mechanics, implement one complete seed-to-wood
job family on this clean controller, with actual cc1/hp0 and real known-map referee
trajectories. Restore export headroom within that batch, prove active logic survives.
