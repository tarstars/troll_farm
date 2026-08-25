# 20260825-dance-cure-candidate-2-swap: Candidate 2 — the blocked troll and its standing teammate change places once; no lock; the swap back is impossible by construction and PROVED

- Status: **G-0 DESIGN_ACCEPTED 16:56Z (codex_1; accepted pin `agent/claude_1@6eb89209`, Addenda
  A/B at `e1f63adb`/`714935df`); G-1 STOPPED 17:17Z at the pre-committed C-5 counter — OWNER
  QUESTION OPEN.** Build correct: rule-off byte-identical to the champion on 34 fixtures + 240
  panel games (C-1), C-2 240/240, `pz=1` everywhere, C-6 = 0 (Theorem 1 holds); **D-1 27 → 13** on
  the panel, all other detectors flat; 46 exchanges / 28 games; refusals `so=675`, `sn=280`,
  `sf=0`. Findings (diagnosed 18:00Z, `agent/claude_1@85c6647c`): **the loop** = the pair
  selector re-assigns the same goals to the new positions ("goals stay with the cells"), fires
  only when the landing is a work square, costs −5 on 1 of 240 games (identical scores on the
  other 3); **`m061` −75** = the exchange frees a troll that fells the map's last tree, then the
  champion's `idle_regeneration` fallback discards the 7,500-point replant PICKs (R-2 violation,
  reported unanswered 08-21) — both trolls goal-less 131/96 turns; the rule also displaces choppers
  mid-chop. Clause 6 measured on all 66 exchanges: goal ≠ landing 66/66. P3 UNMEASURED on the
  instrument arm (must be read on the candidate arm). Owner page v2
  `local_claude_1/cure2/owner-question-2026-08-25.md` (rec.: Candidate 0 fallback fix → Candidate 3
  "keep your goal" → re-run this panel → ask for the read). Deferred controls (C-10 first, C-11,
  C-13, C-7, C-8, C-16, P3 on the candidate arm, the 11 fixtures, C-12 + P4b) proceed without a
  ruling. No lock/timer/predicate change; no Arena action. Original status follows.
- Status at charter: **OPEN — CHARTERED 2026-08-25T16:05Z by owner ruling** (coordinator session ~15:55Z,
  the coordinator's transcription): *"swap — there should not be a special lock. We are to check
  the algorithm and check that it's impossible to choose the back swap, because the mobile troll
  wants to go through the working one. We should prove this — simple, clear set of rules."*
  Recorded as rule **R-1a** in `docs/RULES-LEDGER.md`. Route-around is **not** chartered.
- Record owner: local_claude_1 · Work owner: **claude_1** (definitions + proof, build, gates) ·
  Reviewer: **codex_1** (G-0 design *and proof* before any code; G-1 execution from a fresh
  archive) · optional second reader of the proof: chatgpt_1 (its r2 pair-level step check,
  `agent/chatgpt_1@a90ff533:chatgpt_1/dance-cure/proposal-r2-correction-2026-08-25.md`) ·
  Arena controller and integrator: local_claude_1 — **each Arena action needs the owner's
  separate go** (none is pre-authorized by this card).
- Area: the dance cure, second build. Inputs: `local_claude_1/dance-geometry/owner-brief-2026-08-25.md`
  and the geometry results (`agent/claude_1@c5727dc6`); `local_claude_1/dance-mechanism-map-2026-08-25.md`;
  `local_claude_1/dance-cure-proposal-2026-08-24.md` §2 A **minus the lock**; `docs/RULES-LEDGER.md`
  R-1 / R-1a; `docs/mechanics.md` §"Move conflict resolution" (circular own-unit swaps are legal);
  the v4 read as baseline (`agent/claude_1@22d6b2bb:claude_1/cure1/results/g2-grade.json`).
- Base: **Candidate 1's source** `claude_1/cure1/cure1-hold-v4.rs` (`cc4b3087…`; owner 2026-08-25:
  code kept) — its two-phase reservation, `prev_cells` memory and v4 telemetry are reused; the
  **hold rule is disabled** (Candidate 1 PARKED); the swap rule is added. Rule-off arm = the base
  loop verbatim = champion `547fa706…` parity by construction, as Candidate 1 proved.
- Branch: agent/claude_1 (work), agent/codex_1 (review), agent/local_claude_1 (record, Arena).
- Progress lease: 15 minutes without concrete evidence (phase markers renew it).
- Created UTC: 2026-08-25T16:05:00Z · Last updated UTC: 2026-08-25T16:05:00Z

## THE QUESTION (owner's, plain words)

When our troll's next step is the square where its own teammate stands still and works, and its
road continues **beyond** that square, the two change places in one tick — the referee allows it.
There is **no lock**: the rule itself must make the reverse exchange impossible, and that must be
shown from the bot's algorithm — after the exchange the mobile troll keeps going forward, and the
working troll steps back onto its square as the other leaves. **Does this remove the long dances in
real games without parking trolls, without swap loops, and without costing score?**

## The rule — the spine; G-0 fixes the exact text

Inside Candidate 1's two-phase resolver pass (hold disabled). For a mover `M` whose landing `L`
(its first step along its own path, `next_cell`) is **reserved by a standing own unit `B`** —
`B` not a mover this pass, on `L` this turn **and** last turn (`prev_cells`) — and whose target
lies **strictly beyond `L`**: `target ≠ L` and `dist(L) < dist(M.cell)` on the arm's own metric
(`bfs_distances` seeded at the target, Manhattan fallback), the resolver emits **`MOVE M → L` and
`MOVE B → M.cell` in the same turn** (the circular exchange), replacing `B`'s command for that
turn; both cells are granted for the pass; the letters are `S` (the mover) and `X` (the displaced
partner) in the telemetry grammar (v5: `r=P|L|R|W|N|S|X`, `H` retired; mutual refusal with v4).
Everything else is today's behaviour: a transient blocker (a mover, or one that arrived this
turn) gets today's detour; a mover whose **target is `L` itself** (the teammate on the goal —
`TARGET_OCCUPIED`, 10 + 15 turns in the reads) does **not** swap (recorded, a planner question);
no re-targeting, no score change, no memory beyond `prev_cells`, **no lock of any kind**.

## The proof obligation — part of G-0; codex_1 accepts or rejects it like a definition

**Claim.** With `M`'s target fixed, the pair `(M, B)` cannot exchange squares twice in succession
by this rule alone. Sketch to be made exact in `claude_1/cure2/definitions-g0-2026-08-2x.md`:

1. After the exchange `M` stands on `L` with its target strictly beyond `L`; its next landing is
   the next cell on its path, never `M`'s old cell (now `B`'s) — so the trigger cannot fire for
   `M` against `B` again.
2. `B`'s next want is its work square (`L`, now `M`'s) or work reachable from where it stands. If
   `B` moves toward `L` while `M` moves on, `L` is not reserved (`M` is a mover) and the base rule
   grants `B`'s move — a plain follow-through, no swap. If `M` is still standing on `L` (blocked
   ahead by something else, `W`), then `B`'s landing `L` **is `B`'s own target**, so "target strictly
   beyond `L`" fails for `B` — no swap; `B` waits or detours as today.
3. Therefore a second exchange of the same pair requires `M`'s target to change to something
   back through `B` — a planner event, **counted in the panel and the read, never prevented**.

**Edge cases the proof must enumerate** (handled, or excluded with a counter): three own trolls
(a third unit wanting `M`'s cell in the same pass; the two-phase fixed point); a mover with
`speed 2` (its landing may be two cells away — define the exchange for the adjacent case only, or
prove the two-cell case); `B` on `M`'s target (no swap, by rule); `B` a mover this pass
(transient — today's rule); `prev_cells` unknown (first turn of the game — treat as standing?
define); the dead `priority_ids` / `forbidden_for_non_priority` machinery; orchard-eligible maps
(P3 whole-game rule — decide scoping at G-0 exactly as Candidate 1's R-B, or show the swap is
P3-neutral); what `B` does on the swap turn (it loses one action — the cost, paid once).

## Gates

- **G-0 — design + proof (codex_1, ack-required, before any code).** claude_1 publishes the exact
  predicate, the proof, the v5 grammar, the parity plan, the panel/read bars below (pre-committed)
  and the controls. codex_1 rules `DESIGN_ACCEPTED` / `REVISION_REQUIRED`; a proof with an open
  edge case is a `REVISION_REQUIRED`.
- **G-1 — build and panel (claude_1; codex_1 reproduces from a fresh archive).** Three arms from one
  source and a flag: instrument (swap + v5 `MSG`), candidate (swap, no `MSG`), rule-off (v5,
  swap off). Rule-off byte-identical in play on the 34 fixtures and the 240 panel. Rule-on panel:
  blocking (D-3) not above the base's 43; P3 clean (whole-game on orchard-eligible views); P4 not
  above base **and the per-troll gate `P4b`** from `20260825-p4-per-troll-stall-gate` when it has
  landed (until then the per-troll idle-with-work share ≤ 1.5 % is the safety net); the 11
  reproduced fixtures with `progress_restored`; a positive control (a fixture where the swap must
  fire and end the dance); a poison arm (swap on every block, no "beyond" test → the loop counter
  must catch it); **the swap-loop counter: the same pair exchanging twice within 6 turns = 0 on the
  panel — any positive count is a *stop and ask* finding about the planner, never a reason for a
  lock**; swap ticks ≤ 1 per 50 turns per game; v5 decode controls; every changed game named.
- **G-2 — one ~160-game instrument read (Arena — the owner's go, surfaced before it starts).**
  Baseline = the v4 read (same telemetry family, 160 games). Pre-committed bars, fixed at G-0:
  D-1 episodes per 1,000 game turns **≤ 0.30** (v4: 0.594); dances of ≥ 12 turns **≤ 4** (v4: 13);
  regressive steps `R_pos` per 1,000 troll-turns **≤ 2.2** (v4: 4.31); dances ending in the
  dancer's own progress **≥ 65 %** (v4: 44 %). Kill: idle-with-work > 1.5 %; D-3 > 0; long-stall
  share above the champion's 1.3 %; any same-pair re-exchange within 6 turns → stop and ask.
- **G-3 — one ABAB block vs the champion (Arena — the owner's go):** floor −1.0; the owner rules
  KEEP on a one-page verdict sheet `local_claude_1/cure2/owner-verdict-sheet-2026-08-2x.md`.

## Deliverables

`claude_1/cure2/definitions-g0-2026-08-2x.md` (+ proof, revisions); `claude_1/cure2/cure2-swap-v5.rs`
and the three arms with `arm-manifest.json`; `claude_1/narrate5/` decoder; G-1 report and results;
`codex_1/reviews/dance-cure-candidate-2-swap-*.md`; the read ledger and packages under
`local_claude_1/cure2/`; the verdict sheet.

## Exclusive write set / read-only / do not touch

claude_1: `claude_1/cure2/**`, `claude_1/narrate5/**` · codex_1: `codex_1/reviews/dance-cure-candidate-2-swap-*.md`
· local_claude_1: `local_claude_1/cure2/**`, `cgauto/submissions/candidate-swap-v2*.rs` (hash-verified
placement), this record, status, STATE §4. Read-only: `claude_1/cure1/**`, `claude_1/geometry1/**`,
`claude_1/dance1/**`. Do not touch: `rust/src/bin/yamo_orchard_live.rs`, the dev copy `fff6669b…`,
`data/raw/games/`, the resident, the cron.

## Arena authority

Read-only platform access: not needed before G-2. **Platform mutation: forbidden until the owner
authorizes each action** (the G-2 read, the G-3 block); the coordinator surfaces each before it
starts; `docs/PROMOTION-RUNBOOK.md` applies.

## Not in scope

Route-around (not chosen); Candidate 3 (score smoothing); any re-targeting; any lock or timer;
any change to `compatible` or `select`; the teammate-on-the-goal case (recorded as a planner
question). Anti-benching r2 stays rejected; Candidate 1 stays PARKED with its code kept.

## Handoff

claude_1 → codex_1 at G-0 (design + proof, ack-required) and G-1 (full commit, paths, digests,
controls); codex_1 → claude_1 + local_claude_1 with rulings (ack-required); local_claude_1 → owner
before each Arena action and with the verdict sheet.
