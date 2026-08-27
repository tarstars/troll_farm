# HANDOVER 2026-08-27 (second) — the simplified champion: the farm viewed and closed, a one-variable ablation that became the champion, three owner rulings, steady state

Delta since `coordination/HANDOVER-2026-08-27-board-era-ladder-and-farm.md` (06:45Z) through
2026-08-27 ~11:45Z, written at the owner's request ("prepare to context flush") by `local_claude_1`.
Trunk at writing: `origin/main` == `agent/local_claude_1` == the checkout `/home/tarstars/prj/troll_farm`.

## Resume here

- **The champion of record is the simplified bot** — the previous champion minus its four-line
  plum/lemon denial bonus. Owner ruling 09:05Z: *"One point is not enough to make a decisive
  conclusion. But I like simplification of the algorithm, so let's name the current approach the
  champion."* Resident: submission **`41202036`** (08:21:51Z), agent `6667789`, file
  `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa1e9097dd…d57c`
  (the diagnostics variant; its games come home annotated on the v6 line). **Readable source of
  record `readable/denial-off-champion.rs`** (= `door1-champion.rs` minus the hunk; diff
  `readable/diffs/denial-bonus-off.diff`, −4/+0). `docs/STATE.md` §1 says so. The old champion
  (`547fa706…` bare / `72673124…` with diagnostics) is history; **do not resubmit anything**.
- **`coordination/GOAL.md` is the steady state:** hourly reading of the champion, mail, the board;
  no submission, build or charter without the owner's word. Read `WORKING-RULES.md` then `BOARD.md`.
- Ritual unchanged: `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3
  scripts/inbox_sweep.py --me local_claude_1 --fetch` → read every new message whole → `--mark`
  as its own step → commit the seen state. Every shell command carries its own `cd`.
- The hourly session cron `a956cd82` (at :37) survives a context flush but **dies with the
  session**; recreate it in a new session. Its "in short" text is stale by design — GOAL.md governs.
- **Nothing is waiting on the owner.** The next experiment is theirs to name; they said the
  goal-keeping question will be looked at "in a little bit different angle soon".

## The owner's rulings today, in order (all dated in `BOARD.md` → Decisions)

1. ~06:06Z — the farm goes on the ladder to be *watched*, one-hour rounds; the keep-your-goal
   measurement stops at six readings, under-determined (previous handover).
2. 07:10Z — *"denial logic matters … chop plum or lemon first, banana farm next … of course (a)"*:
   a denial-first repair of the farm (hard-priority chopping of the opponent's plums/lemons, nothing
   planted until denial ends, farm afterwards) was designed and discussed. My assessment, given
   and accepted as discussion: the opponent's second troll is paid from the starting shack
   (2–10 of every fruit), the four leaders never train a third and train the second at turns
   18–28, so early denial rarely *prevents* a power troll; a full-size plum/lemon has 12 health.
3. 08:05Z — *"we conducted a dirty experiment — we changed several variables in one turn"*: the
   repair is parked; instead **one variable**: the champion with its plum/lemon denial logic
   switched off, one hour on the ladder, rating; predicted a drastic drop. 08:20Z: yes.
4. 09:05Z — the ablated bot **is the champion** (quoted above).
5. 10:04Z — three board decisions: **the farm line closed** (obituary in `GRAVEYARD.md`; the
   repair design is on file in `coordination/tasks/20260826-banana-farm-candidate.md`); **the
   inert code in the champion stays** ("probably it'll be convenient for the nearest
   experiments"); **the keep-your-goal question on hold** (L-1 and T-3 on hold; no readings, no
   analytics slice).

## Where the ladder stands (10:57Z)

| | bot | readings |
|---|---|---|
| resident = champion | the simplified bot `41202036` (sha `0e92f8fa…`) | **21.2 / rank 42** at 09:25 (one hour), 09:57, 10:57 — batch complete |
| history | the previous champion + diagnostics | 21.8, 21.6, 22.1 (mean 21.83) |
| history | the farm `41201668` (viewed one hour) | 10.8 / rank 172 |
| on hold | the keep-your-goal bot | 18.4, 19.2, 21.0 — under-determined |

Ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md` (rows FARM, FARM-1h, ABL, ABL-1h/2h/3h).

## What is proven, and what is not

- **Proven:** removing the champion's only active targeted denial — the bonus of 900 ÷ (1 + distance
  to the opponent's shack) for chopping a plum/lemon of the "focus" species while the opponent has
  ≤ 2 trolls (`chop_candidates`, `readable/door1-champion.rs:888`) — shows **no drop in one ladder
  reading** (21.2 vs 21.83 mean, noise ±1.5). The July bench had said the opposite (rule off: 0
  wins–6 losses, −150.7 a game; `docs/CONSTRAINTS.md` "focus-bonus-off failed promotion") — a
  bench-versus-ladder disagreement of the first order, worth remembering before trusting any
  bench verdict on denial. The build is reproduced independently (codex_1, row 0-4: both hashes,
  all five bed counts; the four lines are the whole active denial; a second "opponent-arrival"
  penalty exists but is set to zero).
- **Proven about the farm on the ladder:** 160 games, 81–79, mean margin −26, 24 losses by 150+;
  **its denial stage ran ~65 turns a game in every game** (ended: aim trees felled 66, regrowth
  35, opponent's third troll 31, deadline 14, still denying 14) — the local panel had said
  "instantly over" in 141/240 games. The panel's maps and opponents are not the ladder's.
- **Not proven:** any effect of the denial bonus of 1–2 points either way (one reading cannot);
  the keep-your-goal cost (on hold).
- **The champion's algorithm, read from the code for the owner** (their summary was close):
  opening — the second troll is the most talents (speed/carry/chop; never harvest) collectable
  within ~15 turns, carry ≥ 2 preferred, deadline turn 35; then two trolls chop the tree with the
  best **wood per troll-turn** (size on arrival ÷ (walk + hits + walk back)), banking as they go,
  **never harvesting fruit** mid-game (only the idle fallback when no tree is reachable); then
  **fruit → wood conversion** (PICK from the shack → PLANT near the shack → CHOP) from turn 100
  when ≤ 2 trees remain, and in the endgame (turn > 250, or ≤ 4 trees and behind). Nothing looks
  at the opponent now except predicting whether a tree we walk to will still stand.

## Artifacts landed today (all on `main`)

- `local_claude_1/denial-ablation/`: `make_denial_off.py` (the generator — the template for every
  one-variable experiment: regenerate the base byte-identically, one edit, compile, compact, round
  trip, distinct-from-every-bot check, readable diff), `fixtures_diff.py` (the 34-situation
  differential bed), the arm + sha, `results/build.json`, `results/fixtures.json`,
  `games-41202036/` (160 games, 6.3 MB, sha `3fe5dc49…`).
- `readable/denial-off-champion.rs` (+ `.sha256`), `readable/diffs/denial-bonus-off.diff`,
  `readable/reports/candidate-champion-denial-off-v6-instrument.round-trip.json`.
- `local_claude_1/farm-watch/games-41201668/` (160 games, 6.6 MB) and `farm_decode.py` (reads
  the farm's v8 tokens out of a collected package — the pattern for reading any package).
- Cards: `20260827-denial-ablation-verify.md` (0-4, DONE); the farm card (CLOSED, repair design
  appended); T-3 and L-1 cards (ON HOLD). `GRAVEYARD.md`: the farm's closing paragraph.
- Messages of mine: `082536Z` handoff (0-4 charter), `090026Z` quarantine policy, `100409Z`
  rulings policy, acks. Both peers' queues are drained (their acks 10:09Z / 10:12Z).

## Operational notes

- **Collect before you resubmit:** the platform keeps a rolling window of ~160 battles; the next
  submission evicts the previous bot's games. `local_claude_1/narrate/collect_submission_games.py
  --agent-id <id> --submission-id <id> --scratch <scratchpad>/… --output-dir <repo dir>
  --observed-at-utc <date -u>` (raw outside the repo, sanitised package inside; ~6 MB per 160).
- **Stale pins, fourth time in two days** (codex_1's 06:25Z handoffs): quarantine = an entry in
  `coordination/quarantine.json` (`path`, `reason`, `adjudicated_by`, `target_blob` = the blob at
  the sender's ref) + a `type: policy` message with `quarantines: [...]`; the sweep reads the list
  from `origin/main`, so push before telling anyone. claude_1's rule, worth keeping: bring `main`
  into a published branch by **merge, not rebase**.
- **Building instruments myself:** for a one-line ablation with the owner waiting I built and
  submitted it myself (25 min) and had codex_1 reproduce it afterwards; the owner accepted the
  pattern. Memory: `owner-one-variable-ladder-loop`.
- A one-shot session cron is a good way to take a timed reading; cancel it if you take the
  reading by hand. `git rev-parse --short A B` fails with "Needed a single revision" — one ref per
  call. Set the board's "Last updated" line by pattern (`^Last updated:`), not by exact string.
- The collector cron (05:17 local / 02:17Z) still writes `data/processed/stats.json` in the main
  checkout — never commit it; the wrong-tree guard `.githooks/pre-commit` is in force.
