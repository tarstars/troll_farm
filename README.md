# Troll Farm

Bot for the CodinGame Spring Challenge 2026 — *Troll Farm*.

- `bot/main.py` — the bot. **Single-file submission**: paste the whole file into the
  CodinGame IDE. Pure logic is module-level (unit-tested); the game loop runs only under
  `if __name__ == "__main__"`.
- `tests/` — pytest suite for the pure logic + a `sample_input.txt` for smoke tests.
- `docs/statement.md` — parsed puzzle statement.
- `docs/mechanics.md` — game mechanics verified against the referee source (authoritative).

## Current strategy (Wood league)

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
