# Bot submissions — ready-to-paste single-file CG entries

Each `.rs` here is a **complete standalone CodinGame submission** (stdlib only). To submit:

**Option A (manual):** open the Troll Farm IDE, select all in the editor, paste the file's
contents, then click **TEST IN ARENA → YES**.

**Option B (automated):** `DISPLAY=:0 cgauto/.venv/bin/python cgauto/submit.py <path-to-file>`
(sets the code + clicks TEST IN ARENA → YES; retries through CG's load throttle).

Then confirm promotion on the **LEADERBOARD** — you promote when you rank **above Boss 4**.

## The versions (best-understood first)

| file | sim vs silver_boss | real vs Boss 4 | notes |
|------|--------------------|----------------|-------|
| **v1.0.5-safe.rs** ⭐ | ~77% | not yet CG-tested; = v1.0.1 + a pure bug-fix, so ≥ v1.0.1 | **RECOMMENDED.** Robust denial wood-race bot + the wedge fix (a full troll stuck ON the shack cell after mining turn-1 iron). Strictly safer than what's live. |
| v1.0.1-denialrace.rs | ~78% | **66% (4W/2L), climbed us to rank 42/681** | This is what's **currently live in the arena**. Known-good baseline. |
| v1.0.4-woodfarm-cheapchop.rs | **90.5%** | **33% (2W/4L) — WORSE** | ⚠️ OVERFIT to the sim model. Cheap slow chopper + fruit→wood woodfarm crush `silver_boss` but fail on the real (bigger/watery) maps. Do NOT submit; kept only as a cautionary A/B reference. |

## TL;DR
- Live now: **v1.0.1** (rank 42). 
- Best safe upgrade: **v1.0.5-safe** (adds the wedge bug-fix; low risk).
- v1.0.4 is a trap (great in sim, bad in reality) — evidence that sim gains past ~78%
  overfit; validate on real CG before trusting them.

The working tree `rust/src/main.rs` currently == **v1.0.5-safe**.
