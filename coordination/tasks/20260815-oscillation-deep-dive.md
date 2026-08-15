# 20260815-oscillation-deep-dive: explain every frozen oscillation, adjudicate ideal behaviour with the owner

- Status: open — stage 1 of `docs/PROGRAMME-banana-farm-2026-08-15.md`
- Record owner / integrator: `local_claude_1`
- Code owner: `claude_1` (owner role decision 2026-08-15: "good for writing the code")
- Reviewer: `codex_1` (owner role decision 2026-08-15: "good for tough logical reviews")
- Owner participation: REQUIRED — this is a joint human+agent mini-project by owner design
- Created: 2026-08-15
- Authority: owner directive 2026-08-15, continuing the 2026-08-09 directive
  ("oscillations are our lack of control over the program"). The `CONSTRAINTS.md` value
  closure (+0.045) is about score and does NOT bar this work.

## Objective, in the owner's words

For each oscillation episode: find the precise states of the trolls and the map; analyse
the bot's behaviour; analyse the situation; write down the "ideal" behaviour; compare it
with the bot's. **No cheap ways** — the owner attributes recent stalls to lack of depth in
investigations. "Ideal" means: consider the situation, carefully justify the hierarchy of
goals the trolls have at that moment, optimize the whole picture, and figure out the real
moves the trolls should conduct.

## Subject

`readable__no_orchard`, SHA `98628e98…` — the current resident and the programme's base bot.

## Inputs that already exist (do not rebuild)

- **M3a situation library** — **CORRECTED 2026-08-15: use the SUBJECT-CORRECT tree**
  `claude_1/banana-restoration-r2/oscillation-library-98628e98/library/` — **34 frozen
  situations / 46 episodes** on the exact readable resident `98628e98…` (it is the loader's
  `DEFAULT_DIR`). The sibling `…/oscillation-library/` is PARENT LINEAGE, its own index says
  "MUST NOT BE CITED AS M3a" — an earlier revision of this record cited it with its 33/47
  counts; found by the viewer-scope drafting pass. (loader
  `oscillation_library.py`, 40 tests, `library_sha256 5858d351…`). Its own unknowns table
  (U1–U9) is this task's checklist of what is NOT yet established — notably U1: the
  mechanism classification of 25 situations is transcript-inferred and unverified.
- **Decision Packet frozen contract** — `chatgpt_1/decision-packet-spec-2026-08-10.md`:
  a tool that explains one full turn (candidates considered, rejected, scores, pair
  selection, resolver rewrites) such that an independent verifier can replay the choice.
- **Merged three-agent analysis** — `local_claude_1/oscillation-merged-plan-2026-08-09.md`
  (idle-blocker measurement, `Target::None` bypass, door-pricing asymmetry, idle-yield
  proposal). Treat as HYPOTHESES to verify with traces, not settled truth.

## Deliverables

1. **D1 — Decision Packet implementation** — increment 1 (registry+drift guard) ACCEPTED
   PARTIAL 2026-08-15 by codex_1 review (`155d8dd8`): foundation kept, rollout step 1 OPEN
   (registry incomplete: 22/79 functions, five unbound intents, no packet/event schema;
   semantic wrong-at-freeze not closed). Next increment: complete registry + schema with
   independent pre-freeze check. Original scope: to the frozen spec (claude_1; codex_1 reviews
   conformance). Run it over all 34 frozen subject-correct situations; resolve unknowns U1–U4 (which
   mechanism each situation really is).
2. **D2 — Troll-moves viewer. PHASE 1 DELIVERED 2026-08-15** (claude_1, `423b87a1`,
   merged): 34 pages + index, acceptance machine-checked; REMAINING ITEM: first human
   visual check — owner opens a page before the first live session. Scope as agreed:
   Per `local_claude_1/troll-moves-viewer-scope-proposal-2026-08-15.md` v2, with the
   owner's three rulings: (1) form = self-contained HTML page per situation + index,
   generated via the verifying loader, keyboard step-through; (2) **display-only** —
   NO in-tool ruling capture; `local_claude_1` records rulings separately during
   sessions; (3) sessions are **LIVE** (owner + integrator together). Phase 1 renders
   frozen data only, with the three honesty rules (inferred positions dashed, opponent
   frozen-at-entry labelled, side panels "at entry"); situation kind on every page.
   Phase 2 (Decision Packet overlay incl. blind mode) waits for P-1.
3. **D3 — REDEFINED BY OWNER RULING 2026-08-15: the adjudication template.** The
   doctrine-freeze approach is rejected (it repeated code logic). D3 is now
   `docs/ADJUDICATION-TEMPLATE-2026-08-15.md`: top-down per-situation judgment (L1 game
   state → L2 best course → L3 joint behavior → L4 concrete moves → step-5 deviation
   analysis → step-6 rule candidates). Winning rules are the programme's OUTPUT,
   accumulated in `docs/RULES-LEDGER.md` (owner-approved entries only). The old draft
   survives as `local_claude_1/code-reference-appendix-2026-08-15.md`, step-5 use only.
4. **D4 — Per-situation adjudication record.** For each of the 34 situations: the bot's
   actual line (from D1), the proposed ideal line reasoned through the D3 template levels, and the owner's ruling from a joint session (D2 as the instrument). Easy
   cases batched; hard cases (est. 8–12) individually with the owner.
5. **D5 — Outcome.** Either a verified fix (per-situation regression fixtures from the
   library; test observed failing before the fix, per standing rule) or the owner's
   explicit written ruling "these oscillations are unavoidable and harmless." **Both gates
   are the owner's alone.**
6. **D6 — The −13.6 mystery.** During D4, note per situation whether the game's low margin
   is explained by the oscillation itself or by something else. This is the standing
   unexplained fact (oscillating games ~13.6 below par vs +0.045 fix value).

## What the owner provides (agreed 2026-08-15)

- Corrections to the D3 doctrine draft.
- Joint adjudication sessions over D2 for the hard situations; rulings become D4.
- The final D5 ruling.

## Boundaries

- No bot behaviour change outside D5's fix path; no Arena action from this task.
- The sacred compact file stays byte-exact; all instrumentation is on separate builds.
- No formatters over hash-locked sources.
