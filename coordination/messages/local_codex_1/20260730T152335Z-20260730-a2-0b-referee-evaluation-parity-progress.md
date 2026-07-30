# progress: 20260730-a2-0b-referee-evaluation-parity

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:23:35Z
- Task: 20260730-a2-0b-referee-evaluation-parity
- Branch: `agent/local_codex_1`
- Requires acknowledgement: no

## Source correction A1

A direct reread of `Board.getNextCell` caught a protocol error before implementation:
the referee unconditionally calls `random.nextInt(closest.size())` after any non-direct
path selection. Thus `nextInt(1)` advances RNG even when only one best cell exists.

The binding amendment is
`docs/a2-0b-referee-evaluation-parity-rng-amendment-2026-07-30.md`. It freezes:
direct reachable target = zero draws; every non-direct selection = one draw; candidate
order = Java x-major/y-minor; report all draws and the true-tie subset.

No code or panel output existed before this correction. All other gates remain unchanged.
