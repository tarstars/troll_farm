# HANDOVER 2026-08-27 — the board era: working rules, a ladder measurement, the farm built and stopped, the farm now on the ladder to be watched

Delta since `coordination/HANDOVER-2026-08-26-candidate-0-blocked-candidate-3-corrected.md`
(2026-08-26 10:35Z) through 2026-08-27 06:45Z, written at the owner's request ("prepare for
context flush") by `local_claude_1`. Trunk at writing: `origin/main` == `agent/local_claude_1` ==
the main checkout.

## Resume here

- **Read `coordination/WORKING-RULES.md` first, then `coordination/BOARD.md`.** They are new and
  they are how work moves now: one board, ≤ 2 rows per track, every task born with done/dead/budget,
  **two review rounds then decide-or-kill**, stalls after two days with no evidence, one ladder
  queue, everything lands on `main` at every gate, mail only for handoffs and verdicts, and the
  owner conversation is the word **"board"** → Moved / Stalled / Ladder / Decisions / Corrections.
  Dead tasks get a paragraph in `coordination/GRAVEYARD.md`.
- Ritual unchanged: `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3
  scripts/inbox_sweep.py --me local_claude_1 --fetch` → read every new message whole → `--mark` as
  its own step → commit the seen state. **Every shell command carries its own `cd`** — see the
  wrong-tree guard below.
- `coordination/GOAL.md` is the live mission; a session cron fires hourly and runs one wake of it.

## The owner's rulings, 2026-08-26 → 08-27

1. **Candidate 3 bounded**, then closed on its own gate; **Candidate 3b** chartered and closed the
   same night. Both obituaries are in `GRAVEYARD.md`.
2. **The ladder measures again.** The champion was restored, then replaced by the champion **plus
   per-turn diagnostics** (`41198581`), which is identical in play — so its readings are the
   champion's and its games come home annotated.
3. **Goals: score ≥ 25.40 *and* control over the code / its cleanliness.** A change the owner
   cannot read is not finished; diffs live in `readable/diffs/`.
4. **Old fixtures retired; evidence base = real instrumented games.** `scripts/cut_fixtures.py`
   generates test situations from collected games, tagged by bot hash.
5. **Board organisation adopted**, then the working rules written down (`WORKING-RULES.md`).
6. **Branch hygiene + integration:** three dead branches deleted, an archive branch became a tag,
   and all peer branches were merged into `main` (`main` wins on shared paths). **Retired agents'
   `agent/*` refs must stay** — deleting two broke every sweep.
7. **The banana farm:** the owner's outline consolidated into
   `docs/BANANA-FARM-CONTRACT-2026-08-26.md` with three owner decisions (the **hut ring**; a
   **one-way latch**; **mothers-only planting during denial**). Built, contained, and **stopped by
   its own validity gate**; then, on the owner's ruling, **put on the ladder to be watched**.
8. **The keep-your-goal measurement** was stopped at six readings; verdict **under-determined**.

## Where the ladder stands (06:45Z)

| | what | readings |
|---|---|---|
| resident | **the banana farm (watching)**, submission `41201668`, sha `443a196e…`, parity 240/240 | first reading ~07:35Z; **one-hour rounds** (owner) |
| off | champion + diagnostics `41198581`/`41200776`/`41201060` | **21.8, 21.6, 22.1** (mean 21.83, flat) |
| off | champion + keep-your-goal + diagnostics | **18.4, 19.2, 21.0** (mean 19.53, **climbing**) |

Ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`. **The farm is expected to score
badly** — it failed its validity gate — and this is viewing, not a measurement: no promotion, no
verdict, champion of record unchanged. The champion returns when the viewing ends.

## What is proven, and what is not

- **Proven:** the platform carries our long diagnostic line intact (287 collected games, 78,424
  lines, 242–295 characters, 0 decode failures). The parked-troll gate reads every dialect. The
  fixture generator works and produced two bot-tagged libraries.
- **Proven about the farm:** with the farm off it is byte-identical in play to the champion
  (240/240 + 34/34); with it on, **stuck-troll games rise 52 → 96**, the dominant cause being the
  opponent harvesting our ring crop (35 of 50 new ones); **the stop-latch fired 0/240 because it
  counts enemy chops while the theft is harvests**; bench own-score +3,100 (meaningless under a
  failed gate). Reproduced by codex_1.
- **Not proven:** that keeping goals costs ~3 ladder points (the third reading climbed to 21.0);
  the owner's robustness hypothesis (the slice held 4 keep-rule games, all heavy losses — stopped
  honestly). The one surviving trace: the keep bot reverses direction 16.10 times per 100 moves
  against the champion's 11.95, and the champion's rate is flat across wins and bad losses.

## Owner's queue

1. **The farm:** bounded repair (the latch must count harvests; the placement must not hand the
   enemy a standing crop) or close the line — informed by what the ladder shows this hour.
2. **The keep rule:** two more readings (~4 h of the slot) or leave it under-determined.
3. **The analytics:** charter a balanced slice of keep-rule games plus three missing telemetry
   fields, or leave it.

## Operational notes

- **Wrong-tree guard installed** (`.githooks/pre-commit`): commits made in the main checkout
  `/home/tarstars/prj/troll_farm` are refused. The shell resets there between commands and four
  commits landed in the wrong tree on the night of 08-26/27. Override: `TROLL_ALLOW_MAIN_COMMIT=1`.
- **Publish artifacts before the messages that pin them.** Two peer handoffs and two of my own hit
  unreachable pins after rebases; two are quarantined. Rule: rebase first, publish after.
- **No wildcards in destructive commands** — a `2026082*-ack.md` delete removed dozens of tracked
  files from a working tree (restored in the minute).
- The collector cron (05:17 local / 02:17Z) writes `data/processed/stats.json` in the main
  checkout; never commit it, and never `reset --hard` there without copying it aside first.
- Peer VM: `ssh troll-vm`; the raw replays live only on the host; slices ≤ 10 MB are shipped on
  request (one 212-game slice is on the VM).
