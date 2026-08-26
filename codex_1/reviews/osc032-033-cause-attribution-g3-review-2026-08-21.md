# OSC-032/033 cause attribution — G-3 review

Verdict: **ACCEPTED**.

I reviewed all three declared artifacts at exact handoff commit
`e8034b7991e207040d4a328f8c8823174bd508ac` and independently ran, from a detached worktree:

```text
python3 claude_1/cause1/g3_finding.py
python3 claude_1/cause1/cause_attribution.py
python3 claude_1/cause1/g2_controls.py
git status --short
```

All programs passed, and all three regenerated JSON artifacts were byte-identical to the pinned
commit. The stall control exercised both outcomes in four constructed cases. Per-turn adapter
fidelity covers the complete plant record, unit identity/player/cell/speed/carry, and both
inventories before the frozen `sim.engine.has_stalled` predicate is called.

The amended G-3 questions are answered with appropriate limits:

- The last plants disappeared after directly evidenced own-side `CHOP 0` commands on turns 81
  and 12; attribution does not infer an opponent action from position alone.
- The frozen full referee rule first stalls on turns 82 and 13. Because this is the mercy clause
  and therefore opponent-profile-dependent, the report also gives the opponent-independent
  grace-only bounds, turns 96 and 26. The owner brief preserves that distinction: all 110/143
  window turns are absent under the fixture-specific full rule, while the conservative bound
  permits at most 5/110 and 0/143.
- The minimum second-worker cost is source-derived. OSC-032 never has an apple source; OSC-033
  never has plum or lemon sources. No opponent occupies any available source in the 34-turn
  pre-deadline interval. Thus the "absent" half of H-A is confirmed and the measured "denied"
  half refuted for these fixtures only.
- `c5_own_units_ge_2` is false on every replant row and is the sole false conjunct on 101 rows
  per fixture; the note separately enumerates all co-false conjuncts on the remaining rows.
- H-C is not projected onto the empty windows. Outside them, every observed plant is accepted;
  OSC-032's 52 generator-unentered plant turns remain explicitly unobserved, and the eleven
  unexercised clauses remain outside positive claims.

The disclosed OSC-032 plum ambiguity is handled correctly: a reachable live source existed but
the shack never banked it, and the report does not explain why. This does not affect the
fixture-specific impossibility result because apple was absent throughout.

Scope is compliant: measurement only; no bug/caution judgment, fix, candidate, class-wide claim,
behaviour change, resident/dev-copy touch, or Arena action.

No revision and no successor card are required from this review.
