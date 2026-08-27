# The floor — independent reproduction verdict

Verdict: **REPRODUCED** on the fixed generator at integrated commit
`63532a526d329fd5cd781f62d3567d8720731139` or later.

Commands run exactly once each:

```text
python3 local_claude_1/the-floor/make_the_floor.py
python3 local_claude_1/the-floor/fixtures_diff.py
python3 local_claude_1/the-floor/smoke.py --records local_claude_1/the-floor/smoke-maps-seed0.jsonl
```

Build and regeneration:

- diagnostics arm SHA-256: `75afaf8bd1d380fc3a0178d9c3002e1cd9d224fdc96fd6ab30346bc72d4b8c04`
- compacted submission SHA-256: `31cd23c021f184b0cc39aa7f38d4bfb099d56a9f815ce892bee1f3dada10d420`
- compacted size: 63,791 bytes
- readable diff: +17 / -23
- round trip: exact
- tracked generated outputs after regeneration: byte-identical; only the inbox seen-state was modified before the run

Fixture bed:

- plays: 34/34
- differs from champion: 2/34
- first divergence: OSC-010 turn 13; OSC-032 turn 49
- deterministic: 34/34
- compacted equals arm: 34/34
- telemetry errors: 0
- arm trained below the floor: none

Smoke on the supplied 24-map record slice:

- mechanics: PASS 24/24
- arm trained in every game and never below speed 2 / carry 2 / chop 2
- resident trained below the floor: 11/24
- training-turn median: arm 30 vs resident 11
- own-score sum, arm minus resident: +149 over 24 games (+149 on the 11 changed maps)

Diff reading: nothing in the diff can train a troll weaker than speed 2 / carry 2 / chop 2,
or stop the bot from ever training; every generated and fallback specification respects the
floor, and the deadline path retains a floored desired troll instead of abandoning training.

No Arena action was taken.
