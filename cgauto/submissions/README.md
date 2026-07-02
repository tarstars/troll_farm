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
| **v1.0.6-tempo.rs** ⭐ | 78.4% / 61.1% | pending real batch (see experiment log) | = v1.0.5 + endgame banking (DROP partial carries before t=300) + `(2,2,0,2)` chopper (hp1→0 saves apple) + ripeness anticipation. Every change validated on BOTH boss models (`silver_boss` AND the real-script `scriptboss`). |
| v1.0.5-safe.rs | ~77% / 60.6% | not yet CG-tested; = v1.0.1 + a pure bug-fix, so ≥ v1.0.1 | Robust denial wood-race bot + the wedge fix (a full troll stuck ON the shack cell after mining turn-1 iron). **Fallback** if v1.0.6's real batch disappoints. |
| v1.0.1-denialrace.rs | ~78% / — | **66% (4W/2L), climbed us to rank 42/681** | This is what's **currently live in the arena**. Known-good baseline. |
| v1.0.4-woodfarm-cheapchop.rs | **90.5%** / 56.9% | **33% (2W/4L) — WORSE** | ⚠️ OVERFIT to the silver_boss model (scriptboss correctly ranks it below v1.0.5). Do NOT submit; kept as the canonical overfit warning. |

## TL;DR
- Live now: **v1.0.1** (rank 42).
- Best candidate: **v1.0.6-tempo** — real-CG validate first, then submit; fallback **v1.0.5-safe**.
- v1.0.4 is a trap (great vs silver_boss, bad in reality) — sim gains past ~78% vs
  silver_boss overfit. The second model (`scriptboss`, the real boss's script) now
  catches this class of trap: only trust changes that hold on BOTH models.

The working tree `rust/src/main.rs` currently == **v1.0.6-tempo**.
