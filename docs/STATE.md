# STATE — Troll Farm (single entry point)

Last updated: 2026-08-23 (§4 re-ranked: NARRATE is P0); earlier 08-22 (§1), 08-10 (doc diet, text
at `docs/archive/STATE-2026-08-10-pre-diet.md`). Live state, not a record. Hard budget: 150 lines.

## 1. Live identity

### ★★★ The Arena is RUNNING again (owner, 2026-08-23). Live: the **NARRATE instrument**. Champion of record: **door 1** `547fa706…`, off-ladder, restore target.

Door 1 is cure C minus the fictional-decay hunk — a pure deletion, owner-ruled KEEP 2026-08-21 at
+0.220 IMMATERIAL: at equal score the smaller program wins. Cure C `ad3bfefe…` retired.

| field | live now | champion of record |
|---|---|---|
| submission / agent | **`41182039`** / **`6652424`**, submitted 2026-08-23T09:44Z | `41178858` / `6650438` |
| source | `local_claude_1/narrate/instrument-swap-r1-narrate-v2-SUBMITTED-2026-08-23.rs` | `cgauto/submissions/candidate-door1-pure-deletion.rs` |
| SHA-256 | `aaebc503cc2660e920d45858767c6932575324085c93ef9345906f683b5a9271` | `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0` |
| what it is | **a measuring instrument**: swap R-1 plus per-turn intention telemetry. It can **never** be champion — it changes the command stream. Run, read, retire. | champion; restore target |
| reads | AAAAA, 5 reads of one arm, no pairing. Read 1 live, immature (23.8 at 50 min). | 22.6, rank 36/176, 2026-08-23T06:40Z, one unpaired read |

**Owner reopened the ladder 2026-08-23** for the instrument. Submissions go through
`cgauto/api_submit_once.py`, **not** `night_runner.py` (its end-of-block tree opens an unrelated
A/B); `NIGHT-HALT` stays in place on the VM and `night-runner.service` stays down.

★ **Telemetry proven through the Arena path** — 20 games, 5,257 turns, 0 decode errors, 0 leakage to
the opponent's seat; 149 replays at `local_claude_1/narrate/games/`. **Seat comes from the replay's
`agents` array, never the battle listing's `position`** — METHODS-LEDGER `seat-from-the-replay`.

★ **The direct two-generation measurement is IMMATERIAL.** Ten pairs, champion against the
very-old resident `98628e98…`: **mean +0.17, ≈0.00 once the pairing bias is removed**, against
a composed estimate of +1.24 (`local_claude_1/door1-vs-old-pooled-verdict-2026-08-22.md`). Two
generations of fixture-driven cures are not visible on the ladder — the central planning fact.

⚠ **`docs/PROMOTION-RUNBOOK.md` MUST NOT be followed as it stands.** Its gate is scoped to
candidate D171a and its "fixed identities" name a resident retired weeks ago, so **its abort
path would restore the wrong bot.** Use the restore target above.

- Corpus (re-counted **by parsing**, 2026-08-22): **21,496 games**, raw and processed agreeing,
  21,496 trajectories, `sha256(games.jsonl) a882e527…`; **8,590 are ours** across 86 agent ids
  (`6536359`–`6648254`), complete through today. `local_claude_1/corpus-identity-2026-08-22.md`.
  **Never count corpus membership with a text match** — JSON spacing varies and greps undercount.

## 2. Goal (RE-SCOPED 2026-07-30 by owner decision)

**Primary: a mature score ≥ 25.40** — the top-10 boundary (Escdemon 25.37), i.e. **+3.64** from
our frozen 21.76. **Interim: 24.70**, yamo's score — the design this bot reproduces, so passing
it means the reproduction beat its original (+2.94). Completion needs a mature read **plus a
later confirmation**, never a single spike.

Superseded: Legend rank ≤ 3 (bar 28.22), set when passive maturity looked like a live lever —
an assumption N1 killed (uplift −0.161, CI [−0.753, +0.457]); rank targets also move the
goalpost the wrong way as the pool strengthens. ≥25.40 is the right *kind* of target because
**25 Legend agents reach ranks 7–54 on our exact two-worker roster** — demonstrated, not
hypothetical. **Read §1's two-generation measurement beside this:** the cure programme is not
moving the ladder, so +3.64 will not come from more of it.

## 3. Standing rules

- ★★ **STANDING ARENA AUTHORIZATION, granted by the owner 2026-07-30.** The per-candidate
  permission gate is **lifted**: *"I want to lift this rule about my authorization of
  interaction with arena. Submit anything worth trying."* Scope, as recorded and confirmed
  by the integrator:
  - **Without asking:** submit a candidate that passed its frozen gates; the full promotion
    protocol including the capacity A/A phase; timed reads; reverts and exact-resident restore.
  - **Surfaced BEFORE acting** (a notification, not a permission request — these are outside
    what was authorized): submitting anything that has NOT passed frozen gates; abandoning a
    matured score with no qualified candidate in hand; more than one cycle in flight; anything
    that could forfeit the ladder slot.
- ★★ **OWNER 2026-08-12 (real date 2026-08-09): the noise-band gate is REMOVED.** The ladder
  is an information channel; submissions are the cheap instrument. QUALIFIED-verdict
  correctness bar stands; magnitude bar is gone; runbook in full; owner told before and
  after each cycle; every id and terminal response logged.
- ★ **σ = 1.501** (CI [1.049, 2.634]; 4 families / 14 observations / 10 d.o.f.;
  `cgauto/arena_noise_band.py`), superseding 1.098 — the new CI's lower bound sits *above* the
  old point estimate, so that figure was optimistic, not merely imprecise. Difference SD at
  n=1/arm = **2.123**; SE 1.0 needs **5** runs/arm, SE 0.5 needs **19**, SE 0.3 needs **51**.
  A mature 160-game read takes **~2 h**. Paired blocks use **σ_pair 1.5** (bar 1.315 at n=5,
  0.930 at n=10; materiality floor 1.0).
  - What the number is and is not, the runs-per-arm caveats, and the n=6 evidence:
    task record `20260810-arena-noise-band-measurement`. Two clauses that must travel with
    it: it estimates **combined** operational variability and does **not** separate
    re-submission variance from ladder drift; and the runs-per-arm figures assume stationary
    observations, so persistent drift can defeat the nominal `1/√n`.
  - **Pairing (amended 2026-08-22, owner):** blocks run **ABBA** and the difference is taken
    **A minus B by arm, never by position**. A fixed A-then-B order put arm A in the earlier
    slot of every pair, so drift entered every difference with a fixed sign.
    `docs/METHODS-LEDGER.md`, `paired-order-carries-the-drift`.
  - **Read scores only from an agent-validated block.** The room serves a persistent
    stale row — agent 6604529 / field 140 / score 22.46 — that camouflages as a plausible
    value; the registry faults any checkpoint whose arena block names a foreign agent.
  - **Unchanged:** mutations are serialized through the single arena controller
    (`local_claude_1`); no peer agent or subagent may submit; one cycle in flight at a time,
    so higher throughput means *shorter cycles*, never parallel ones. The controller may run a
    deterministic service (`night-runner`) under a pre-registered plan — it is not a peer.
- **B0.3 no-churn — WEAKENED 2026-08-12 by measurement, restated 2026-08-22.** "Fresh reads sit
  3–4 points below matured ones" holds. "Every failed trial costs days of standing" does not: a
  mature 160-game read takes ~2 h, and the ladder was swapped every 2 h for several nights
  without loss. What churn costs is the **slot** — while a block runs nothing else can be
  measured — so queue order is the scarce thing. Never *abandon* a run before it matures.
- Sealed, do not open: maps `9,844,200–9,844,215`; the official-map holdout; the 11 sealed
  D164 field games; D170's confirmation block `9,852,000–063`.
- Substrate rule (D158/D161): controllers use the exact Yamo/Orchard resident fallback natively
  or first prove same-panel dominance. D40/q6 is dead as a substrate.
- External play bursts ≤ 12 games; stop on HTTP 422 or degenerate results. Bulk writes:
  preflight `cgauto/check_external_storage.py --required-free-gib N` (`docs/storage-policy.md`).
- **`coordination/multi-agent-protocol.md` is in force** (control-plane migration parked; spec
  `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md`).
  Coordinator/integrator/Arena controller = `local_claude_1`. §7 hazards bind everyone:
  byte-sacred `fff6669b` dev copy, no formatters over hash-locked sources, `data/raw/games/`
  and the 02:17 UTC cron untouchable. **§5.1: an agent is woken only by mail from someone
  else** — its own cards are obligations, not signals.
- **History rewrite: DECLINED by owner 2026-07-30, closed. Do not reopen.** (12.9 MB against
  invalidating ~380 published commit hashes, four cited in experiment records.)
- The integrated branch is **`main`**; `session-2026-07-01` has not moved since 2026-08-17 and
  is not kept in step. Full-history bundle on `medium_data`.

## 4. Open thread

- **P0 is the INSTRUMENT, not another cure** (backlog re-ranked 2026-08-23). **NARRATE** — the bot
  prints each troll's target every turn via `MSG`, so we grade real games instead of 34 hand-picked
  fixtures from a retired bot; audit done (`coordination/tasks/20260823-narrate-real-game-telemetry.md`).
  Also P0: the replay→`Trace` adapter, needed by NARRATE step 4 **and** the prevalence card — one
  trap, 301 states against 300 command rows, silently truncated. Why: §1, and §5's reading order.
- **Parked behind NARRATE:** PEEK (rev 3 inert corpus-wide; supplying the missing intention makes
  displacement **refuse** — confirmed on the champion, 989 of 989, **0** wanting a third square,
  `claude_1@c85ee672`), PEEK branch 2, and the swap cure (α instrument accepted, 32 of 34 healed
  *with progress*; "healed" means with progress from now on; residual-13 and the cure-arm basket
  criterion stay mine). **Authorized:** anti-benching Phase 3b **build**, strictly after the adapter
  — and no fixture-only result promotes it. Extend-versus-replace: scope 101 turns, one game.
- **Withdrawn 2026-08-23:** my "235 of 2,245 wanted the partner's square" as evidence of contention
  — the wrong-pairing control was never run, and claude_1's analogous 323/323 died to it. The
  **zeros** stand; a zero needs no pairing. **`chatgpt_1` revived**, architecture only, no verdict
  authority; its gateway is backlogged. **Unowned defect:** the night runner erases its ledger and
  re-opens an identical block at every completion — twice on 08-21/22.
- **★ Needs the owner: ONE item — NARRATE step 1's go**, one submission of an instrumented bot on
  a stopped ladder. History: 07-29 closed all eight resident levers; A2 died at K1; N1 at maturity.

## 5. Reading order & pointers

1. **`docs/GOALS.md` (the three goals + where we stand)** → this file → `docs/CONSTRAINTS.md`
   (before any experiment) → `docs/BACKLOG.md` → `coordination/README.md` + the inbox sweep.
2. `docs/DISCUSSION-architecture-over-score-2026-08-22.md` — what we are optimising, and why.
3. `docs/METHODS-LEDGER.md` (how we measure) · `docs/RULES-LEDGER.md` (how we win) ·
   `docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`.
4. Live ledger `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol4-2026-08-04.md`;
   prior volumes frozen. Atlas `docs/D-series-atlas.pdf`. `AGENTS.md`, `docs/mechanics.md`,
   `docs/archive/INDEX.md`.

Per-experiment obligations: ledger entry; CONSTRAINTS bullet for anything closed; §4 update here.
First session ending with the live volume over 100 KB freezes it and opens the next.
