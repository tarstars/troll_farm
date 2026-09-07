# Primary review — 2026-09-07

Exact eb14e6cbe1d86e1896be67e1127fe84b89f5b56811b3dfc47758170ba903f9f8
PARKED as competitive candidate. Independent actualRust1.90 tests39/39 pass.
192 unique pairs and all192 baseline command arrays independently verified against
gap20260906T210944Z-3184968-1. Baseline170points, candidate142.5; issues1 vs0.
Mean candidate own score180.0417, but competitive result fell4points versus prior.
Canonical hashes remain44e3daca/7f61a6cd; no publication.

Independent command parsing (slash separates turns, pipe commands) corrects report:
prior candidate WAIT6564, not3091 (that was BASELINE), current8376. HARVEST754->6124,
MOVE61498->64748, CHOP28126->22072, DROP5637->10583, TRAIN234->251.
Higher fruit/own score does not establish a better bot when outcomes deteriorate.

Aggregate verbs are real-map observations, NOT a state-level causal reproducer.
The requested known-map decision/ablation fixture was again not delivered. Synthetic
ablation is now correctly labeled; do not imply that a real trajectory established
why a particular decision lost. The next batch must supply that evidence first.

Source review: jobs_for still requires plant.fruits>0 before offering Harvest,
despite the stated arrival-time feature. fruit_service predicts a first load from
free capacity and lifetime supply, without checking fruit availability at first
arrival/harvest or carrying the plant's actual cooldown. Therefore bill_units and
bill_busy can promise fruit earlier than it physically exists. service_reservations
returns only(cell,value), drops its chosen worker identity, and deducts a whole
lifetime harvest value from CHOP without committing an executable service schedule.
These are concrete model/implementation gaps; their competitive effect requires
actual state reproduction. Do not just add an exhaustion coefficient to this model.

Next bounded repair: event-timed real fruit delivery and explicit service ownership,
validated on an actual unmodified known-map trajectory. Preserve net timber and
quantity ledger. Do not bless another disconnected pricing-only retention mechanism.
