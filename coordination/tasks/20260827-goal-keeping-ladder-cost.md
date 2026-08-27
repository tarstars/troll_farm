# 20260827-goal-keeping-ladder-cost: why does keeping a goal cost ~3 ladder points when it costs almost nothing on the bench? (owner's hypothesis, read-only)

- Status: **OPEN — CHARTERED 2026-08-27T05:55Z by owner ruling** ("we can open a ticket for analytical investigation, it's my hypothesis"). Board row T-3 (analytics track).
- Record owner: local_claude_1 · Work owner: **codex_1** (it holds the per-turn corpus and the fixture generator) · Reviewer: claude_1 (one round) · Arena: nothing.
- **The owner's hypothesis, in their words:** *fixing the rule lowers the bot's robustness and costs points.*
- **The puzzle, stated with the numbers:** the keep-your-goal rule **reduced** stuck-troll games on the local bench (52 → 40) and cost only **65 fruit over 240 games (≈ 0.27 a game)** — yet on the real ladder it reads **18.4 / 19.2** against the champion's **21.8 / 21.6 / 22.1**, a gap of about **3 points with no overlap**. Something that is nearly free against our fixed local opponents is expensive against real Legend opponents. **Why?**
- **The candidate mechanism to test (the owner's, sharpened):** a troll that will not re-target loses *adaptivity*; adaptivity only pays when the opponent actively contests — takes the tree you wanted, arrives first, or moves the board under you. Our bench opponents are old and passive; Legend opponents are not.
- **Done means:** a file `codex_1/analytics/goal-keeping-ladder-cost-2026-08-2x.md` on `main` that compares the two bots **on their own real ladder games** (both print per-turn diagnostics; ≈ 287 games collected so far, growing nightly), by one script, on: how long goals are held; how often a held goal is invalidated by the opponent (tree taken, cell occupied, plant gone) and what the troll does next; wasted moves (moves that end where they began, or reverse within N turns); time spent walking versus working; contested-tree episodes won and lost; score composition (wood versus fruit) and its timing; and the same measures on the games each bot lost badly versus won. Every number with its game count. **A one-paragraph answer to the owner's hypothesis: supported, refuted, or under-determined — and what would settle it.**
- **Dead means:** the collected games cannot separate the two bots' behaviour (say so with the counts and stop).
- **Budget:** 1 day, 0 ladder, 0 builds, one review round.
- Created UTC: 2026-08-27T05:55:00Z

## Inputs
The annotated games of both bots (raw replays on the host; slices shipped on request — one 212-game slice is already on the VM); `scripts/cut_fixtures.py` and the two bot-tagged libraries; the ladder ledger `local_claude_1/ladder-measure/ledger-2026-08-26.md`; Candidate 3's bench packet `claude_1/cure3/g1-packet-2026-08-26.md` (the 52 → 40 and −65 numbers); the map-61 read `claude_1/cure3/m061-stale-goal-read-2026-08-26.md` (the mechanism that stranded a troll for 171 turns).

## Not in scope
Any repair of the rule; any new candidate; any Arena action. This ticket explains a measurement; it does not fix anything.
