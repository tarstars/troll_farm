# Opponent-crop commitment diagnostic — result, 2026-07-19

## Verdict

**Close short opponent-crop target commitment.  Do not build the prototype.**

All 160 consumed candidate replays parsed without failure.  Six of seven material-signature checks
pass, but the predeclared abandonment-rate check fails: only 8.48% of crops already selected by our
commands are never contacted, below the required 15%.  The threshold is not relaxed after seeing
the absolute count or value.

## Result

| Measure | Result | Gate | Check |
|---|---:|---:|---|
| Distinct selected crops | 2,323 | >=80 | pass |
| Games selecting a crop | 150 | >=20 | pass |
| Abandoned selected crops | 197 (8.48%) | >=15% | **fail** |
| Games with abandonment | 85 | >=10 | pass |
| Opponents with abandonment | 38 | >=8 | pass |
| Opponent wood on abandoned / all selected crops | 349/1,529 (22.83%) | >=10% | pass |
| Catastrophic-game abandoned crops | 82 | >=20 | pass |

Abandoned crops also yield 945 opponent fruit.  The absolute residual is real and concentrated in
valuable trees, especially APPLE (70) and BANANA (66), but a persistence layer would target the
minority 8.5% failure mode while risking overcommitment on the much larger set that already
completes normally.

## Analysis by level

1. **Command execution:** the candidate emits an opponent-crop target in 150/160 games, so the live
   mechanism is highly active rather than inert.
2. **Task persistence:** 91.5% of distinct selected crops receive official contact.  Transient
   switching is not the main reason overall interception remains near 51.5%.
3. **Scheduling capacity:** the larger residual is crops never selected at all, or opponent crop
   creation outpacing two-worker capacity.  Stronger/broader bonuses were already locally harmful;
   this does not reopen them.
4. **Economy:** catastrophic opponents still field about 3.7 workers and create about 50 crops.
   Completing an additional narrow commitment cannot substitute for a productive renewable
   workforce and role policy.
5. **Statistics:** selecting the idea because 197 sounds large after freezing a 15% rate gate would
   be outcome-driven threshold relaxation.  The prospective rate gate controls the decision.

## Hypothesis update

- Retain provenance-aware target scoring as a useful architectural component, but close this
  six-turn commitment amplification.
- Do not increase the crop bonus/ETA or resubmit `b100_e6`; those exact transfer and tuning paths
  are consumed and closed.
- Advance the genuinely different open direction: **closed-loop outcome optimization of a compact
  complete economy controller**.  It must co-design workforce, renewable supply, roles, and target
  policy and must include exact resident as a baseline genotype.
- Before expensive search, require a bounded smoke discriminator showing that the proposed policy
  representation can reproduce the resident exactly and express at least one locally positive,
  opponent-robust complete policy on reused data.

## Evidence

- `opponent-crop-commitment-diagnostic-protocol-2026-07-19.md`;
- `opponent-crop-commitment-diagnostic-2026-07-19.json`;
- `cgauto/opponent_crop_commitment_diagnostic.py`.
