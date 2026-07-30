# handoff: 20260730-n5-endgame-opponent-plant-contest

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:39:00Z
- Task: 20260730-n5-endgame-opponent-plant-contest
- Branch: agent/local_codex_1
- Requires acknowledgement: yes
- Supersedes: none

## Verdict

**`NO_MATERIAL_CONTEST_OPPORTUNITY`.**

All 382 cohort occurrences decode and all target-integrity checks pass. Exact lineage
reproduces H13: resident 388 generations in 78/170 endgame-reaching games; yamo 205 in
37/103. Opponents extract 1,487 carried score-equivalent units from resident targets
versus 241 for the resident, but the deliberately generous factor-two observed-yield
ceiling is 11.9917 per all 242 resident games, whole-game bootstrap 95% CI
[8.7273, 15.7603], below the frozen 20 threshold.

## Reproduction and hashes

```text
python3 -m py_compile cgauto/endgame_opponent_plant_contest.py
python3 cgauto/endgame_opponent_plant_contest.py --self-test
python3 -m pytest -q tests/test_endgame_opponent_plant_contest.py
python3 cgauto/endgame_opponent_plant_contest.py \
  --corpus-root ../troll_farm \
  --output-dir local_codex_1/n5-endgame-opponent-plant-contest \
  --jobs 4
```

Compile/self-test pass; six tests pass. A second full run is byte-identical:

- `result.json`:
  `7b5cb104df969aaacf1771eb0d86bed49f04b2aa55e481590c215273dc9c275b`;
- `input-manifest.json`:
  `53ee5cf3347fbc72dcd1021369cb2b41ce48eb6c3ca22fc9981f7abf14a2b26f`;
- `targets.csv`:
  `b51e8140e1a78d11aa5be110a6a123485b75754e275a345dbfc3ddd24beacb3f`;
- `report.md`:
  `793d673ddafbf409f850c19760c04241766e5e6ff7b557fdd348cd4dac849222`.

## Requested review

Please check target identity in both lineage orientations, the distinction between
extracted cargo and banked score, factor-two/all-game semantics, whole-game bootstrap,
and the causal wording. This result does not authorize simulation or Arena action.
