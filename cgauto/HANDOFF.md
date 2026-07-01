# Troll Farm — Handoff (2026-06-30/07-01)

## Goal
Rank **above Boss 4** (the **Silver** boss) → promote to **Gold**. Silver, rank ~44–53.

## How to test (WORKS; login recipe in memory `cg-automation.md`)
- `cgauto/` uv venv + Playwright. Login = Yandex UA + `cgSession`/`rememberMe` from `cg_session.txt` each launch.
- **`.venv/bin/python run_games.py N [main.rs]`** → N games vs Boss 4, prints win rate + saves `lastgame.png`. ~35s/game.
- CG sometimes throttles the initial load after heavy use (~150 games/day) — the loader retries 5× with 25s cooldowns; if it still dies, wait and relaunch.

## MEASUREMENT — solved, and validated
The IDE "1ST/2ND" panel is a per-FRAME **live standing**, not the result; the replay plays slowly (~75–110s; games end ~turn 230–293) in a **cross-origin** viewer iframe. Reading mid-replay is wrong (same bot read 36% at turn~1, 60–91% depending on frame). **Correct read (in run_games.py):** after the new replay loads, **scrub to the end with a SINGLE coordinate click on the skip-to-end `>>` button** at `[bbox.x+154, bbox.y+bbox.h-18]` (bbox = `.cg-player-sandbox` rect ≈ [101,43,752,470]), wait ~13s, read the standing. **VALIDATED** by `lastgame.png` (viewer at 233/233, final overlay matched the read).
- ⚠️ Do NOT also click the progress-bar (it scrubs AWAY from the end; broke a run to 33%). Single `>>` click only.
- ⚠️ The `at_end` turn-counter check is BROKEN (the "N/N" text isn't in `body.innerText`), so every read logs `[UNCONFIRMED]` — a FALSE negative. To make the meter fully trustworthy, verify the final frame another way (screenshot OCR, or find the real turn-counter node). Until then, trust it but spot-check with `lastgame.png`.
- ALL pre-scrub variant numbers (v0.9.0=30%, v0.8.4=70%, "v0.8.3=50%") are INVALID mid-replay reads — ignore them.

## KEY FINDING (the real state of the project)
**v0.8.3 beats Boss 4 ~70–77%** (17W/5L over 22 scrub-read games; noisy). We are **behind early** (Boss 4 harvests fruit fast) and **win late** (WOOD scores 4×, and our denial — chopping Boss 4's trees — starves it over the game). We **lose ~25–30%** of maps, where Boss 4's early lead holds to the end. This matches the user: we do NOT beat it on all maps, and that ~25–30% is the promotion blocker.

## Actionable next steps
1. **Fix the meter's verification** (so reads are provably final) — then get a tight rate over 40–60 games.
2. **Study a LOSS** to convert the ~25–30%: run a DEBUG build (`run_game.py` / flip `DEBUG=true`), scrub a losing replay, and see WHY Boss 4's early lead holds — is it out-harvesting us early, fielding more trolls, or a specific map (far-apart shacks? few trees?)? Then strengthen our EARLY economy or the late comeback, and measure with the scrub meter. Prior analysis: Boss 4 fields more, versatile (chop+harvest) trolls and out-harvests early; v0.9.0's attempt to copy that was WORSE — our edge is fast denial, so likely improve WITHIN the denial strategy (deny earlier/harder, or don't fall so far behind early).
3. Sanity-check the live ARENA (leaderboard / Last battles): are we above/below Boss 4 and climbing (rank has read 53→44→49)? If ~75% H2H, we may be close; the field matters too.

## Code state
- `rust/src/main.rs` = **v0.8.3** (compiles `rustc --edition 2021`). Live arena version. IDE editor holds a v0.8.x test build; arena = v0.8.3 (nothing new submitted).
- `cgauto/variants/v084.rs` = v0.8.4 (fruit-denial); unevaluated (its "70%" was a bad read).
- **GIT: HEAD is v0.7.5; all v0.8.x + sim work is UNCOMMITTED working-tree only. NEVER `git checkout rust/src/main.rs`** (→ v0.7.5). 35 files modified, none committed.
