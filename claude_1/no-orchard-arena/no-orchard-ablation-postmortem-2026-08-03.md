# No-orchard ablation postmortem — why the rating dropped, and where the upside is

Data: terminal 160-game checkpoint of ablation `6592097`/`41085842` (23.27, rank 34/137) vs
the exact-E7a predecessor's 160-game audit record (`6590141`, 25.30, rank 11/131; rows from
`top15-public-battle-audit-2026-08-02.json`, SHA `8c29f433…`). Outcome: **−2.03 score,
−22 ranks; ablation rejected; orchard confirmed causally load-bearing.**

## Mechanism

1. **The ablation only changes orchard-eligible games.** Everything else is byte-identical
   (24/25 packet games replayed identically pre-submission). So the whole −2.03 must come
   from games where the orchard would have run.

2. **True orchard camps are rare but concentrated exactly where rating is won.** Separating
   the resident's games by harvest intensity (YamoBot's own endgame idle-harvest causes 1–9
   incidental harvests and is NOT touched by the ablation):
   - none: 84 games (52%), own score 191.6;
   - incidental 1–9: 65 games (41%) — unaffected by the ablation;
   - **orchard camp (≥10 harvests): 11 games (7%), avg 106 apple harvests, own score 252.6
     (+61 vs baseline)** — all eleven are 300-turn games against top-tier opponents
     (delineate, yamo, gaha, putibuzu, Astrobytes, XSpace, viewlagoon, skotz, therealbeef).

3. **The orchard converts top-tier games.** Of the 11 camp games: 3 wins — and removing the
   apple-harvest score flips **2 of 3 to losses** (gaha +105 with 143 harvests; yamo +51
   with 58 harvests; only therealbeef +83 survives). Two more were near-flips the orchard
   almost won (delineate −12, skotz −15). Losing ~2 wins per 160 against the strongest
   opponents, plus the score cushion in every long top-tier game, moves a TrueSkill-style
   rating by about the observed 2 points, and the ablation's equilibrium confirms it:
   winrate 0.57 with +10.6 mean margin against the *weaker* rank-34 field — it settled
   where it belongs.

4. **This matches the ledger's standing diagnosis** (`docs/STATE.md` §4, 2026-07-29
   terminal synthesis): the resident's architectural gap is production persistence during
   long scale-asymmetric games. The orchard is the bot's only production-persistence
   mechanism; the ablation removed it and the deficit appeared exactly in those games.

## Where the effect can be made stronger (all local-panel-first; no arena until QUALIFIED)

- **S1 — activation frequency.** Only 7% of ladder games get a camp; activation needs a
  mother site ≥11 from the enemy door, plus a pre-turn-100 alignment (starter empty on a
  door, second worker, `can_activate`). Candidate relaxations to measure by paired 516-task
  panels: distance 11→9/10; Dormant window 100→150; a widened checkpoint. Each panel is
  free; each directly scales the +61-score treatment to more games.
- **S2 — production while active.** Camp games average 106 harvests but sacrifice ~10 wood
  (37.1 vs 47.6) to the starter reservation. Candidates: a second mother, a banking relay
  for the harvested fruit, partial starter release during mother cooldowns.
- **S3 — banana restoration (already owner-assigned as `20260802-banana-restoration-r2`).**
  The self-reproducing banana orchard is this same mechanism at larger scale, with
  development-panel evidence of +162.3 own score in the closed architectural study. It is
  the largest known upside and is queued behind the simplification task.

## Costs recorded

The experiment spent the matured leg: the restored exact E7a (`6592131`/`41086057`) reads
18.57 at rank 84 cold and needs days to re-mature toward ~25.3. Future strengthening
experiments should qualify locally and, per the no-churn rule, only a bundled,
noise-band-exceeding winner should be submitted.
