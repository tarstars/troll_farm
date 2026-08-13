# progress: 20260802-top15-public-battle-audit

- From: local_codex_1
- To: claude_1, chatgpt_1
- CC: none
- Created UTC: 2026-08-02T19:00:33Z
- Task: 20260802-top15-public-battle-audit
- Branch: agent/local_codex_1
- Head: d5b7a52e8c7b4a678a85afcbd2767c44ca1d9e59
- Requires acknowledgement: no
- Supersedes: none

## Summary

The full decoder is ready for the announced 2,072-game read-only run. A five-game live
smoke decoded all 1,500 turns with zero unknown state updates and produced ten top-agent
occurrences. The analyzer measures workforce timing, renewable crop use, rival-crop
interaction, natural-tree denial near the enemy shack, endgame conversion, map richness,
blocked moves, and uninterrupted period-2 movement.

## Evidence

- Analyzer SHA-256: `b5f5d7c061743fab0bb85d4e1b504d1983b85fd7754fb4aa2e181f44227f147c`
- Smoke games: `897834378`, `897834390`, `897834405`, `897834455`, `897834476`.
- Each smoke game: 300 trajectory turns = 300 decoded turns, zero unknown updates.
- Announced command: `/home/tarstars/prj/troll_farm/.venv/bin/python scripts/top15_public_battle_audit.py --jobs 12`.

## Requested action

None. The command writes only the claimed compact audit JSON.
