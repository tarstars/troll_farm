# 20260826-ladder-measure-cured-dancing-troll: ladder measurement — the "cured dancing troll" (keep-your-goal, Candidate 3) against the champion, both with per-turn diagnostics, on the real platform

- Status: **ON HOLD — owner 2026-08-27T10:04Z** (the keep-your-goal question will be looked at "in a little bit different angle soon"). Stopped at six readings 2026-08-27 06:33Z, verdict UNDER-DETERMINED (A 21.8/21.6/22.1 vs B 18.4/19.2/21.0); no further readings. Previously: chartered 2026-08-26T18:50Z. Board row L-1.
- Record owner and Arena operator: **local_claude_1** (sole Arena controller) · Bot B builder: **claude_1** · Verifier: **codex_1** (one check: B's submission file is byte-identical in play to the arm that passed the parity gate) · Readers of the annotated games: codex_1 (same script for both bots).
- **What it is (plain words):** we put two bots on the platform in turns — **A** = the champion with its diagnostic line (already the resident, submission `41198581`), **B** = the same bot with the "a troll keeps its goal" rule switched on (Candidate 3, which cures the swap-and-swap-back dance but cost 65 fruit over 240 local games) — and we read each one's score when it has played enough games, four times each, alternating A-B-B-A so the ladder's drift does not favour either side. Every game both bots play comes back annotated. **This is a measurement, not a promotion:** the champion of record stays the champion; nobody proposes "keep B" from this run.
- **Done means:** 8 mature reads per bot (score, rank, agent id, battles, time) in the ledger `local_claude_1/ladder-measure/ledger-2026-08-2x.md`; the score difference stated with its noise band (spread between re-submissions of the same bot ≈ 1.5 points; 8 reads per side → about ±0.5) as "within noise / not within noise"; from the annotated games of both, the same measures by the same script: dance rate (champion ≈ 17 % of two-troll games), kept-goal age distribution, stranded-troll episodes (a troll away from its hut with the turn-100 routine never starting — the map-61 failure), the endgame "move" gap; a plain-words sheet for the owner. **A goes back on at the end regardless.**
- **Dead means:** B's file fails codex_1's byte-identity check (then A stays and nothing is submitted); or the platform truncates the diagnostic line (then the run continues for scores only and the annotation part is reported as not measurable); or the owner halts it.
- **Budget:** ~1.5 days of the ladder slot (16 submissions, one read every ~2 h); one submission per read; no other Arena action meanwhile. Fixture-generator task (row 0-3) slips by the same time — its data gate accepts B's games too (tagged by bot hash).
- Created UTC: 2026-08-26T18:50:00Z · Last updated UTC: 2026-08-26T18:50:00Z

## Pre-committed reading (written before the first read)

1. Score: mean of 8 reads per bot; difference A−B by bot (never by position); noise band from `cgauto/arena_noise_band.py` conventions (σ_pair 1.5). Report "within noise" if |diff| < the band; no KEEP/REVERT ruling from this task.
2. Annotated games: dance rate, kept-goal age, stranded-troll episodes, endgame MOVE count, per bot, with game counts; the diagnostic line's decode error count (a non-zero count on the first game stops the annotation claim).
3. Anything else observed is reported as an observation, not a finding.

## Steps

1. claude_1: B's submission file = the Candidate 3 instrument arm (`claude_1/cure3/arm-instrument.rs`, keep rule ON + diagnostics v6) compacted exactly as 0-3a was (`make_champion_v6.py` path), file under `cgauto/submissions/candidate-3-keep-v6-instrument.rs` + sha256 + round-trip report on `main`; handoff to codex_1 and the coordinator.
2. codex_1: byte-identity in play to the parity-gated arm (strip the diagnostic line → identical command streams on the 240 local games); one line back.
3. Coordinator: the A-B-B-A block — read A (already up), submit B, read at maturity (~2 h), submit B again … per the schedule in the ledger; `python3 cgauto/cg_rank.py` for reads, `cgauto/api_submit_once.py` with the sha for submissions; every id and read in the ledger; A resubmitted at the end.
4. codex_1: the annotated-game measures on both bots' collected games (the collector brings them at 02:17Z daily); sheet for the owner.

## Do not touch
Play logic of either bot; the resolver; `data/raw/games/`; the cron.
