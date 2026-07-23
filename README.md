# Troll Farm

Bot for the CodinGame Spring Challenge 2026 — *Troll Farm*.

> Current project state (2026-07-17): the promoted practice-ladder policy is Legend agent
> `6557204`, submitted from the behavior-identical 62,725-byte
> `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`. Its slim A/A
> closed at rank 24/104 and 24.2 versus the full-size source's frozen 24.5 bracket. Start with
> `docs/session-handoff-2026-07-16.md` and the 2026-07-17 retry report linked there; the
> Wood-league overview below is historical onboarding.

- `bot/main.py` — the bot. **Single-file submission**: paste the whole file into the
  CodinGame IDE. Pure logic is module-level (unit-tested); the game loop runs only under
  `if __name__ == "__main__"`.
- `tests/` — pytest suite for the pure logic + a `sample_input.txt` for smoke tests.
- `docs/statement.md` — parsed puzzle statement.
- `docs/mechanics.md` — game mechanics verified against the referee source (authoritative).

## Bulk storage

Large datasets, simulation matrices, checkpoints, raw telemetry, and YT staging
belong on the filesystem labeled `medium_data`, exposed through verified
repo-relative symlinks. Run
`python3 cgauto/check_external_storage.py --required-free-gib <GiB>` before a
bulk write and stop if it fails; never replace a missing external link with a
real directory on the system disk. See `AGENTS.md` and
`docs/storage-policy.md` for the layout, migration protocol, and YT policy.

## Historical starter strategy (Wood league)

Wood gives a single troll with `movementSpeed=1, carryCapacity=1, harvestPower=1`, so the
game is single-agent routing with fruit-ripeness timing. The bot:

1. If carrying a fruit → return to the shack and `DROP` (capacity is 1).
2. Else if standing on a fruited tree → `HARVEST`.
3. Else pick the tree with the cheapest round trip — BFS walk distance + turns until it
   ripens (predicted via the referee's growth rules) + BFS distance back to the shack —
   and `MOVE` toward it (camp with `WAIT` if already on a not-yet-ripe target).

## Dev

```sh
uv sync          # set up .venv
uv run pytest    # run tests
uv run python bot/main.py < tests/sample_input.txt   # smoke test
```
