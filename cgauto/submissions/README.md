# Bot submissions — ready-to-paste single-file CG entries

Each `.rs` here is a **complete standalone CodinGame submission** (stdlib only). To submit:

**Option A (manual):** open the Troll Farm IDE, select all in the editor, paste the file's
contents, then click **TEST IN ARENA → YES**.

**Option B (automated):** `DISPLAY=:0 cgauto/.venv/bin/python cgauto/submit.py <path-to-file>`
(sets the code + clicks TEST IN ARENA → YES; retries through CG's load throttle).

Then confirm promotion on the **LEADERBOARD** — you promote when you rank **above Boss 4**.

## The versions (best-understood first)

| file | sim (silver_boss / scriptboss) | real vs Boss 4 | notes |
|------|-------------------------------|----------------|-------|
| **v1.0.9-mower.rs** ⭐ | **87.5% / 64.3%** | validating | = v1.0.8 + chop1 harvesters that mow the base farm. Best on both models by clear margins. |
| v1.0.8-woodprinter.rs | 85.1% / 63.0% | **5W/3L (62%)** bbox-good | = v1.0.6 + woodfarm + banana PICK+replant printer + water orchard. Real-validated; its submit attempt got throttled, superseded by v1.0.9. |
| v1.0.6-tempo.rs | 78.4% / 61.1% | **5W/3L (62%)**, live in arena (rank ~58) | = v1.0.5 + endgame banking + `(2,2,0,2)` chopper + ripeness anticipation. Every change validated on BOTH boss models. |
| v1.0.5-safe.rs | ~77% / 60.6% | not yet CG-tested; = v1.0.1 + a pure bug-fix | Denial wood-race bot + the wedge fix. Historical fallback. |
| v1.0.1-denialrace.rs | ~78% / — | 66% (4W/2L), once rank 42/681 | Previous arena bot (replaced by v1.0.6 on 2026-07-02). |
| v1.0.4-woodfarm-cheapchop.rs | **90.5%** / 56.9% | **33% (2W/4L) — WORSE** | ⚠️ OVERFIT to the silver_boss model (scriptboss correctly ranks it below v1.0.5). Do NOT submit; kept as the canonical overfit warning. |

## TL;DR
- Live in arena: **v1.0.6-tempo** (rank ~58/682, score ~16.9; Gold bar ≈ score >24).
- Best: **v1.0.9-mower** — validate on real CG, then submit (v1.0.8 already validated
  5W/3L = no collapse; v1.0.9 is a strict both-model improvement over it).
- v1.0.4 is a trap (great vs silver_boss, bad in reality) — only trust changes that
  hold on BOTH boss models (`silverboss` + `scriptboss`).
- Throttle gotcha: `pkill -f "chrom.*cgauto/profil[e]"` (the naive pattern self-matches
  the invoking shell and kills it).

The working tree `rust/src/main.rs` currently == **v1.0.9-mower**.
