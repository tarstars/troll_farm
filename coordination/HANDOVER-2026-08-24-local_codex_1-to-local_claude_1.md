# Coordinator handover — `local_codex_1` → `local_claude_1`, 2026-08-24

Owner instruction, 2026-08-24: continue using `local_claude_1` as project coordinator and transfer
the role back now.

Read this brief, then `docs/GOALS.md`, `docs/STATE.md`, and your inbox. Do not resume from your old
status snapshot; it predates the 2026-08-23 transfer and is stale.

## 1. Authority and the exact boundary

`local_claude_1` is the coordinator, integrator, and sole Arena controller when the roster commit
containing this brief reaches `origin/main`. `local_codex_1` holds none of those roles after that
publication and becomes an idle contributor. There is no shared-control interval.

The incoming coordinator owns the shared coordination tree and live project documents from that
point. It must publish its own acknowledgement and refresh its own status; the outgoing agent does
not edit either artifact on its behalf.

## 2. What changed during the one-day local_codex_1 term

The anti-benching revision r2 is decisively rejected. On the locked 240-game named-cost panel it
produced **115 blocking games versus 35** for the exact base: 80 new blocked games, zero healed,
five direct orchard-inertness failures, and 73 new long-stall labels. The complete rerun reproduced
all 240 rows. The later progress gate was correctly not run after the first hard cost falsifier.

`chatgpt_1` then performed a fresh causal rereview. Its correction stands beside the rejection:
the measured 35-to-115 result is valid, but the broad claim that persistent commitment caused most
of the damage was not proved. At least one long-stall interval ends before the first command
divergence, because that classifier uses later trajectory information.

A final read-only design memo concludes **`ISOLATABLE`**: the discarded replant option can be
specified separately from new persistent memory and duplicate bank candidates. This is a design
fact, not a cure verdict. Progress, closed-loop safety, score, qualification, and Arena value remain
unmeasured. No implementation is authorized.

The complete 16-page account is:
`local_codex_1/reports/anti-benching-complete-story-2026-08-24.pdf`.

## 3. Arena identity and mutation boundary

The latest verified resident identity inherited on 2026-08-23 remains unchanged by
`local_codex_1`:

| field | value |
|---|---|
| live resident | NARRATE v3 measuring instrument |
| submission / agent | `41182608` / `6652642` |
| source | `local_claude_1/narrate/instrument-swap-r1-narrate-v3-SUBMITTED-2026-08-23.rs` |
| SHA-256 | `9a3e875823f3fc26bb7be04f67d872d5c5590f4479f771cae4402ed1e3281239` |
| last recorded read | 21.37, rank 41/176 |
| champion of record | door 1, `547fa706…`, off ladder |
| restore obligation | none, by owner ruling 2026-08-23 |

An instrumented bot changes the command stream and cannot become champion. Single-arm submissions
use `cgauto/api_submit_once.py` with an expected source hash, never `night_runner.py`; its completion
tree opens an unrelated A/B run. `NIGHT-HALT` stays in place and `night-runner.service` stays down.
`docs/PROMOTION-RUNBOOK.md` remains unsafe because its abort path restores an obsolete bot.

No Arena, TestSession, API, submission, service, or source mutation occurred during the outgoing
coordinator's work.

## 4. Current research posture

- The original real-game problem remains measured: work was discarded on **615 of 84,928
  troll-turns (0.72%)** in 160 real games. This proves a problem exists; it does not qualify r2.
- The swap/yield cure is retired. Its target occurred zero times in 469 current real games, with
  controls proving the detector can fire. It reopens only if the target reappears in new grading.
- Anti-benching r2 is stopped and Arena-closed. The option-only memo is the smallest possible
  future design, but this transfer does not activate it.
- The real-game NARRATE work produced the data needed for both rulings. Its former autonomous goal
  is complete; `coordination/GOAL.md` now records that no autonomous mission is active.
- `chatgpt_1` is reachable for review but may require the owner to wake its interactive session.
  `chatgpt_2` remains unreachable. `claude_1` and `codex_1` remain contributors with no Arena
  authority.

## 5. Standing owner rulings and hazards

- The ladder is open, but who sits on it does not need managing; there is no automatic champion
  restore duty.
- Prefer fast grading on newly collected games over archive-wide defect recounts. This is not
  permission to weaken controls.
- The abandoned `chatgpt_1` publication gateway stays closed.
- Autonomous operation remains paused pending its own owner session. Do not restart it implicitly.
- One mutation cycle at a time; only the Arena controller may submit.
- Resolve our seat from a replay's `agents` array, never from the battle listing's `position`.
- Collect a resident's rolling-window games before replacing it.
- Never touch `data/raw/games/` or the collection cron, open sealed map ranges, format locked source
  trees, or alter the sacred resident source.

The sacred source must remain SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## 6. First actions for local_claude_1

1. Fetch `origin/main` and verify `coordination/roster.json` names `local_claude_1`.
2. Run `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`; read every new addressed
   message in full before marking anything.
3. Acknowledge the exact transfer handoff from your own message namespace and publish a fresh
   `coordination/status/local_claude_1.md` snapshot.
4. Verify no Arena mutation or service cycle is in flight before any platform action.
5. Treat the project as awaiting the owner's next priority. Do not activate the option-only design,
   a panel, a score test, or an Arena run from this transfer alone.

## 7. Completion condition

Authority changes with the roster on `origin/main`. Operational handoff completes when
`local_claude_1` acknowledges the exact handoff message, confirms the no-mutation boundary, and
publishes its current status. Until that acknowledgement arrives, the transfer is effective but
recorded as awaiting operational receipt.
