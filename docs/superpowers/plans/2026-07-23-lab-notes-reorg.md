# Lab-Notes Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the laboratory notes so a session resumes and legality-checks proposals from ≤50 KB of reading (STATE.md + CONSTRAINTS.md + AGENTS.md + live ledger volume) instead of ~330 KB, with zero loss of historical content.

**Architecture:** Add a small distilled head (`docs/STATE.md` live state, `docs/CONSTRAINTS.md` closed-branch knowledge base), move all 36 superseded docs byte-identical into `docs/archive/{bronze-to-gold,legend}/` with an INDEX, freeze the 292 KB journal as volume 1, and open a capped volume 2 for D167+.

**Tech Stack:** git (mv/rename detection), markdown, five one-line Python string edits, pytest + cargo as regression gates.

**Spec:** `docs/superpowers/specs/2026-07-23-lab-notes-reorg-design.md` — authoritative for any ambiguity.

## Global Constraints

- History is immutable: never rewrite, reformat, or delete an existing note. Moves must be byte-identical (`git mv`; verify with `-M100%` rename detection).
- Volume 1 (`data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md`) receives exactly one appended entry (Task 6) and no other edit, ever.
- `docs/STATE.md` hard budget: ≤150 lines. Resume+legality read (STATE + CONSTRAINTS + AGENTS.md + vol 2) hard budget: ≤50 KB.
- The reproducibility layer (`data/analysis/live-agent-6553250/dNNN-*`) and `docs/plays/` are untouched.
- Do not touch the arena, submissions, or any experiment state. This is a documentation-only change plus five string constants in `cgauto/`.
- Every commit message ends with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` (repo convention for agent commits).
- `$SCRATCH` below means the session scratchpad directory (any writable temp dir outside the repo works).

---

### Task 1: Archive skeleton + Legend-era moves + INDEX (part 1)

**Files:**
- Create: `docs/archive/INDEX.md`
- Move: 8 files `docs/*.md` → `docs/archive/legend/`

**Interfaces:**
- Produces: `docs/archive/legend/` paths that Task 3 (STATE.md pointers) and Tasks 4–5 (CONSTRAINTS evidence pointers) cite verbatim.

- [ ] **Step 1: Create directories and move the 8 Legend-era files**

```bash
mkdir -p docs/archive/legend docs/archive/bronze-to-gold
git mv docs/session-handoff-2026-07-16.md docs/archive/legend/
git mv docs/hierarchical-controller-roadmap-2026-07-17.md docs/archive/legend/
git mv docs/improvement-roadmap-2026-07-16.md docs/archive/legend/
git mv docs/alternative-approaches-roadmap-2026-07-16.md docs/archive/legend/
git mv docs/residual-search-iteration-2026-07-16.md docs/archive/legend/
git mv docs/portfolio-geometry-prospective-gate-2026-07-16.md docs/archive/legend/
git mv docs/portfolio-motion-followup-2026-07-16.md docs/archive/legend/
git mv docs/portfolio-prospective-gate-2026-07-16.md docs/archive/legend/
```

If any `git mv` fails with "not under version control", use `mv <src> <dst> && git add <dst>` for that file and note it in the commit message.

- [ ] **Step 2: Write `docs/archive/INDEX.md` with header + the 8 legend rows**

```markdown
# Archive index — superseded laboratory notes

Moved byte-identical on 2026-07-23 (see spec
`docs/superpowers/specs/2026-07-23-lab-notes-reorg-design.md`). Old paths inside frozen
records resolve via this table; filenames are unchanged, so `rg --glob '**/<name>'` also
finds them.

| Old path | New path | Era | What it was | Superseded by |
|---|---|---|---|---|
| docs/session-handoff-2026-07-16.md | docs/archive/legend/session-handoff-2026-07-16.md | Legend | live-source recovery + Phases 1–16 handoff | docs/STATE.md + journal vol 1 |
| docs/hierarchical-controller-roadmap-2026-07-17.md | docs/archive/legend/hierarchical-controller-roadmap-2026-07-17.md | Legend | controller architecture/protocol/kill rules (phases complete) | journal vol 1 + docs/CONSTRAINTS.md |
| docs/improvement-roadmap-2026-07-16.md | docs/archive/legend/improvement-roadmap-2026-07-16.md | Legend | ten-direction execution record | journal vol 1 |
| docs/alternative-approaches-roadmap-2026-07-16.md | docs/archive/legend/alternative-approaches-roadmap-2026-07-16.md | Legend | alternative-architecture sweep record | journal vol 1 |
| docs/residual-search-iteration-2026-07-16.md | docs/archive/legend/residual-search-iteration-2026-07-16.md | Legend | resident residual search iteration | journal vol 1 (Phase 16 closure) |
| docs/portfolio-geometry-prospective-gate-2026-07-16.md | docs/archive/legend/portfolio-geometry-prospective-gate-2026-07-16.md | Legend | geometry-portfolio gate protocol | journal vol 1 (portfolio closure) |
| docs/portfolio-motion-followup-2026-07-16.md | docs/archive/legend/portfolio-motion-followup-2026-07-16.md | Legend | portfolio motion follow-up protocol | journal vol 1 (portfolio closure) |
| docs/portfolio-prospective-gate-2026-07-16.md | docs/archive/legend/portfolio-prospective-gate-2026-07-16.md | Legend | stack-portfolio prospective gate protocol | journal vol 1 (portfolio closure) |
```

- [ ] **Step 3: Verify byte-identical renames**

Run: `git add docs/archive/INDEX.md && git diff --cached -M100% --stat | tail -12`
Expected: all 8 moved files shown as `{... => docs/archive/legend/...} (100%)` renames (or plain adds only for files that needed the `mv` fallback); INDEX.md as a new file.

- [ ] **Step 4: Commit**

```bash
git commit -m "notes(archive): move 8 superseded Legend-era docs to docs/archive/legend + INDEX

Byte-identical git mv per lab-notes reorg spec; INDEX maps old->new paths.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Bronze-to-Gold moves + INDEX (part 2)

**Files:**
- Move: 27 files from `docs/` + `cgauto/HANDOFF.md` → `docs/archive/bronze-to-gold/`
- Modify: `docs/archive/INDEX.md` (append 28 rows)

**Interfaces:**
- Consumes: `docs/archive/INDEX.md` table from Task 1.
- Produces: `docs/archive/bronze-to-gold/` paths cited by Tasks 4–5 and by the Task 7 `cgauto` string edits.

- [ ] **Step 1: Move the 28 files**

```bash
cd /home/tarstars/prj/troll_farm
for f in ROADMAP.md arena-queue.md BOSS5-FINDINGS.md boss5-game-analysis.md \
  player-loss-analysis.md motion-findings.md refactor-goal.md pressure-aware-farm.md \
  map-value-ownership.md session-handoff-total-map-value-ownership.md conclusions.md \
  session-handoff-2026-07-11.md strategic-rethink-2026-07-11.md \
  discussion-2026-07-11-ceiling-and-expressiveness.md silver-experiment-log.md \
  statement_bronze.md statement_bronze_full.md best-bot-v1.4.5.pdf best-bot-v1.4.5.html \
  best-bot-v1.4.5.rs v1.4.1-algorithm.pdf v1.4.1-algorithm.html v1.4.1-nostarve-readable.rs \
  bot-architecture.html troll-farm-bot.pdf troll_farm_dom_dump.html troll_farm_play.html; do
  git mv "docs/$f" docs/archive/bronze-to-gold/ || { mv "docs/$f" docs/archive/bronze-to-gold/ && git add "docs/archive/bronze-to-gold/$f"; }
done
git mv cgauto/HANDOFF.md docs/archive/bronze-to-gold/HANDOFF.md
```

- [ ] **Step 2: Append 28 rows to `docs/archive/INDEX.md`**

Append to the existing table (same 5 columns):

```markdown
| docs/ROADMAP.md | docs/archive/bronze-to-gold/ROADMAP.md | Gold | Gold→sub-100 recipe book (completed) | legend-era program (journal vol 1) |
| docs/arena-queue.md | docs/archive/bronze-to-gold/arena-queue.md | Gold | measurement policy v2 + arena queue log | docs/CONSTRAINTS.md §arena-measurement |
| docs/BOSS5-FINDINGS.md | docs/archive/bronze-to-gold/BOSS5-FINDINGS.md | Gold | Boss-5 mechanics/playbook | contest over; historical |
| docs/boss5-game-analysis.md | docs/archive/bronze-to-gold/boss5-game-analysis.md | Gold | Boss-5 game analysis | contest over; historical |
| docs/player-loss-analysis.md | docs/archive/bronze-to-gold/player-loss-analysis.md | Gold | loss taxonomy vs players | docs/CONSTRAINTS.md (D159 supersedes) |
| docs/motion-findings.md | docs/archive/bronze-to-gold/motion-findings.md | Gold | motion solver findings (done) | code + historical |
| docs/refactor-goal.md | docs/archive/bronze-to-gold/refactor-goal.md | Gold | R1 equality-refactor goal | completed; historical |
| docs/pressure-aware-farm.md | docs/archive/bronze-to-gold/pressure-aware-farm.md | Gold | pressure-aware farm design | superseded lineage; historical |
| docs/map-value-ownership.md | docs/archive/bronze-to-gold/map-value-ownership.md | Gold | map-value ownership study | historical |
| docs/session-handoff-total-map-value-ownership.md | docs/archive/bronze-to-gold/session-handoff-total-map-value-ownership.md | Gold | ownership-session handoff | historical |
| docs/conclusions.md | docs/archive/bronze-to-gold/conclusions.md | Gold | mid-contest conclusions | docs/CONSTRAINTS.md |
| docs/session-handoff-2026-07-11.md | docs/archive/bronze-to-gold/session-handoff-2026-07-11.md | Gold | 07-11 flush-safe handoff | docs/STATE.md |
| docs/strategic-rethink-2026-07-11.md | docs/archive/bronze-to-gold/strategic-rethink-2026-07-11.md | Gold | ranked roadmap 07-11 | legend-era program (journal vol 1) |
| docs/discussion-2026-07-11-ceiling-and-expressiveness.md | docs/archive/bronze-to-gold/discussion-2026-07-11-ceiling-and-expressiveness.md | Gold | expressiveness/ceiling discussion | legend-era program (journal vol 1) |
| docs/silver-experiment-log.md | docs/archive/bronze-to-gold/silver-experiment-log.md | Silver→Gold | append-only Gold-era ledger (227 KB) | journal vol 1 (Legend ledger) |
| docs/statement_bronze.md | docs/archive/bronze-to-gold/statement_bronze.md | Bronze | Bronze statement | docs/statement.md |
| docs/statement_bronze_full.md | docs/archive/bronze-to-gold/statement_bronze_full.md | Bronze | full Bronze statement | docs/statement.md |
| docs/best-bot-v1.4.5.pdf | docs/archive/bronze-to-gold/best-bot-v1.4.5.pdf | Gold | v1.4.5 bot snapshot (PDF) | cgauto/submissions artifacts |
| docs/best-bot-v1.4.5.html | docs/archive/bronze-to-gold/best-bot-v1.4.5.html | Gold | v1.4.5 bot snapshot (HTML) | cgauto/submissions artifacts |
| docs/best-bot-v1.4.5.rs | docs/archive/bronze-to-gold/best-bot-v1.4.5.rs | Gold | v1.4.5 source snapshot | cgauto/submissions artifacts |
| docs/v1.4.1-algorithm.pdf | docs/archive/bronze-to-gold/v1.4.1-algorithm.pdf | Gold | v1.4.1 algorithm writeup (PDF) | historical |
| docs/v1.4.1-algorithm.html | docs/archive/bronze-to-gold/v1.4.1-algorithm.html | Gold | v1.4.1 algorithm writeup (HTML) | historical |
| docs/v1.4.1-nostarve-readable.rs | docs/archive/bronze-to-gold/v1.4.1-nostarve-readable.rs | Gold | v1.4.1 readable source | historical |
| docs/bot-architecture.html | docs/archive/bronze-to-gold/bot-architecture.html | Bronze→Gold | early architecture notes | historical |
| docs/troll-farm-bot.pdf | docs/archive/bronze-to-gold/troll-farm-bot.pdf | Gold | generated bot PDF (2026-07-09) | regenerate via cgauto/make_bot_pdf.py → outputs/ |
| docs/troll_farm_dom_dump.html | docs/archive/bronze-to-gold/troll_farm_dom_dump.html | Bronze | scraped DOM dump | cgauto collectors |
| docs/troll_farm_play.html | docs/archive/bronze-to-gold/troll_farm_play.html | Bronze | scraped play page | cgauto collectors |
| cgauto/HANDOFF.md | docs/archive/bronze-to-gold/HANDOFF.md | Gold | double-stale handoff (mechanics/lessons background) | docs/STATE.md + docs/CONSTRAINTS.md |
```

- [ ] **Step 3: Verify renames and docs/ root population**

Run: `git add docs/archive/INDEX.md && git diff --cached -M100% --stat | grep -c '=>'`
Expected: `28` (or fewer if fallbacks were needed; each fallback must be listed in the commit message).
Run: `ls docs/`
Expected exactly: `archive  mechanics.md  plays  statement.md  storage-migration-2026-07-23.sha256  storage-policy.md  superpowers` (STATE.md and CONSTRAINTS.md arrive in Tasks 3–4).

- [ ] **Step 4: Commit**

```bash
git commit -m "notes(archive): move 28 Bronze/Silver/Gold-era docs (incl. cgauto/HANDOFF.md) to docs/archive/bronze-to-gold

Byte-identical moves; INDEX rows appended; docs/ root now holds only live references.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Write `docs/STATE.md`

**Files:**
- Create: `docs/STATE.md`

**Interfaces:**
- Consumes: archive paths from Tasks 1–2.
- Produces: the live head that Task 6's vol 2 header, Task 7's README/AGENTS edits, and Task 8's memory repoint refer to as `docs/STATE.md`.

- [ ] **Step 1: Get the resident source checksum**

Run: `cat cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs.sha256 2>/dev/null || sha256sum cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
Expected: one 64-hex-char digest; paste it into the `SHA-256` line below.

- [ ] **Step 2: Write `docs/STATE.md` with exactly this content (fill the one SHA placeholder from Step 1)**

```markdown
# STATE — Troll Farm (single entry point)

Last updated: 2026-07-23. This file is live state, not a record — the ledger volumes are the
record. Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

- Player `tass`, Legend practice ladder (contest ended 2026-05-25 — no deadline).
- Resident: agent `6561795`, submission `41015603`.
- Source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
  (62,725 bytes, slim Yamo/Orchard + pre-seed + orchard coverage).
  SHA-256: `<PASTE-FROM-STEP-1>`
- `cgauto/api_submit.py` default = that exact source. Keep it that way.
- Last ladder read: rank 43/107 @ 21.97 (2026-07-23 ~10:47 MSK, D164 snapshot; earlier same
  day: rank 40/107 @ 22.18 with 197 battles).

## 2. Goal

Legend **rank ≤ 3** on a mature read plus a later confirmation (journal vol 1 "Completion
rule"). Rank-3 bar was 28.11 at Phase 21 — a moving reference, not a frozen target.

## 3. Standing rules

- Arena writes require explicit user authorization. No exceptions.
- Never churn submissions: fresh submissions read 3–4 points below matured ones (proven by
  failed same-code A/A on 2026-07-16). Restores/candidates burn standing.
- Sealed, do not open: maps `9,844,200–9,844,215`; the official-map holdout; the 11 sealed
  field games from the D164 snapshot.
- Substrate rule (D158/D161): every controller uses exact Yamo/Orchard resident
  fallback natively, or first proves same-panel dominance over it. D40/q6 is dead as a
  competition substrate.
- External play bursts ≤ 12 games; stop on HTTP 422 or degenerate results.
- Bulk writes: preflight `python3 cgauto/check_external_storage.py --required-free-gib <N>`
  (see `AGENTS.md` + `docs/storage-policy.md`). YT root:
  `//home/delivery_ml/research/tarstars/troll_farm`.

## 4. Open thread

- **Next experiment — D167** (per D166 decision, 2026-07-23): recover the seed-acquisition
  paths behind the 135 natural local PLANT returns and the field PLANT returns; then freeze
  trajectory-conditioned semantic successor-job value over exact resident KEEP /
  acquire-and-PLANT / current-own-crop HARVEST, evaluated with short resident-backed
  rollouts. Do not force one verb, reopen D87/D89, or train on terminal outcomes.
- Queue after D167 (reorder only from written evidence):
  1. If D167 closes: family-robust closed-loop objective on the resident substrate — the
     explicitly skipped D109 question (see vol 1, D157 audit).
  2. Standing: let the resident mature undisturbed; no arena writes without authorization.

## 5. Reading order & pointers

1. This file.
2. `docs/CONSTRAINTS.md` — check BEFORE proposing any experiment.
3. Live ledger: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md`
   (frozen history: `...-2026-07-18.md` = vol 1, 292 KB, includes Phases 1–21 + D1–D166).
4. `AGENTS.md` (process), `docs/storage-policy.md` (storage/YT), `docs/mechanics.md` (game).
5. Superseded docs: `docs/archive/INDEX.md`. Pre-2026-07-23 doc references resolve via
   `docs/archive/`.

Per-experiment obligations: ledger entry in the live volume; a `docs/CONSTRAINTS.md` bullet
for anything closed; update §4 of this file. First session ending with the live volume over
100 KB freezes it (one appended note) and opens the next.
```

- [ ] **Step 3: Verify budget**

Run: `wc -l docs/STATE.md`
Expected: ≤ 150.

- [ ] **Step 4: Commit**

```bash
git add docs/STATE.md
git commit -m "notes(state): docs/STATE.md — live head (identity, goal, standing rules, open thread, reading order)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Seed `docs/CONSTRAINTS.md` from vol 1 "Knowledge retained"

**Files:**
- Create: `docs/CONSTRAINTS.md`
- Read-only source: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md` lines 2226–2506

**Interfaces:**
- Produces: `docs/CONSTRAINTS.md` with class sections `(a)`–`(h)` that Task 5 appends into and Task 8 audits.

- [ ] **Step 1: Extract the source section to the scratchpad**

Run: `sed -n '2226,2506p' data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md > $SCRATCH/knowledge-src.md && grep -c '^- ' $SCRATCH/knowledge-src.md`
Expected: a bullet count around 85–95. Record the exact number `N_SRC` for the Task 8 audit.

- [ ] **Step 2: Write `docs/CONSTRAINTS.md` header + class skeleton**

```markdown
# CONSTRAINTS — closed branches and binding facts

Check a proposal against the matching section BEFORE freezing a protocol. One bullet =
claim + decisive number + evidence pointer (`Dnnn` / `Phase n` = journal vol 1
`data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md`; archive paths
= `docs/archive/...`). Append-only: never delete a bullet; if overturned, mark it
`[overturned by Dnnn]` and append the new entry.

## (a) Workforce & scaling
## (b) Imitation & offline value learning
## (c) Substrate & evaluation validity
## (d) Denial & opponent-crop
## (e) Renewal & farm grammars
## (f) Wrappers, residuals, online-search latency
## (g) Arena measurement & platform behavior
## (h) Meta-lessons
```

- [ ] **Step 3: Distill every source bullet into a classed bullet**

For each of the `N_SRC` bullets in `$SCRATCH/knowledge-src.md`: write one bullet under the
matching class in the new format, or fold it into an existing bullet when it is the same
closed class (record the fold in Step 4's map either way). Keep the decisive number.
Worked examples of the required format (use these verbatim as the first entries):

```markdown
## (a) Workforce & scaling
- Direct transplantation of a strong bot's three-worker policy loses as a complete policy
  (corrected funded sequence: −28.3 trimmed, negative vs all six opponents). [vol 1
  "Knowledge retained"; archive/legend/session-handoff-2026-07-16.md]
- Worker-3 is a funding-policy effect, never passively affordable: zero affordability windows
  in 195/195 decoded games; cheapest helper ≥2 units short, balanced ≥10. [D160]
- Bounded reserve/commit options cannot fund worker-3 either: best arm 5/128 = 3.91%,
  balanced 0/768; breadth/rate gates fail. Do not retime/lengthen/tune. [D162]

## (b) Imitation & offline value learning
- Hard-argmax imitation of best-pair schedules fails from target entropy: best held rank
  accuracy 9.79% vs 6.43% random; adding state 9.54%. [D149a/b]
- Fitted conditional value does not transfer across map folds: best held +1.82 vs +14–17
  train, 44% harmful, negative fold; confidence contains no rescue (top decile predicts
  +18.07, realizes −1.51). [D153a/b]

## (c) Substrate & evaluation validity
- D40/q6 is dead as a resident-competition substrate: full per-task terminal oracle only
  +3.42 vs resident, CI [−8.70, +15.54], catastrophes 22→43. All controllers must anchor on
  the exact resident or first prove same-panel dominance. [D161; D158]

## (g) Arena measurement & platform behavior
- Fresh submissions read 3–4 points below matured ones; a failed same-code A/A (16.1 → 19.9
  vs prior 26.3) proves the artifact. Never churn submissions; require capacity A/A before
  candidate trials. [vol 1 07-16 arena section; archive/legend/session-handoff-2026-07-16.md]
- Verdicts are deltas against a same-window control, never absolute levels or cross-hour
  comparisons. [archive/bronze-to-gold/arena-queue.md, measurement policy v2]

## (h) Meta-lessons
- Across the whole project, only execution-class changes (waste cuts, geometry, packaging)
  have transferred to the arena; every wrapper, transplant, imitation, offline-value
  selector, and economy re-architecture failed held-out gates or arena. [vol 1; archive
  ledgers]
- Never tune on consumed blocks or reuse consumed seed ranges for selection; reopening a
  closed branch requires a new representation, not a threshold retune. [vol 1, passim]
```

- [ ] **Step 4: Write the audit map**

Create `$SCRATCH/constraints-audit.tsv` with one line per source bullet:
`<first 60 chars of source bullet>\t<class letter>\t<first 60 chars of destination bullet>`.
Run: `wc -l $SCRATCH/constraints-audit.tsv`
Expected: exactly `N_SRC` lines — every source bullet mapped (folds map to their shared
destination bullet).

- [ ] **Step 5: Commit**

```bash
git add docs/CONSTRAINTS.md
git commit -m "notes(constraints): seed docs/CONSTRAINTS.md from vol 1 'Knowledge retained' (classed, deduplicated, evidence-linked)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Sweep remaining closures into CONSTRAINTS + coverage audit

**Files:**
- Modify: `docs/CONSTRAINTS.md` (append bullets)
- Read-only sources: journal vol 1 (all `## ` entries), `docs/archive/legend/session-handoff-2026-07-16.md`, `docs/archive/bronze-to-gold/arena-queue.md`

**Interfaces:**
- Consumes: class sections from Task 4.
- Produces: the complete knowledge base Task 8 measures.

- [ ] **Step 1: Build the entry checklist**

Run: `grep -n '^## ' data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md > $SCRATCH/vol1-entries.txt && wc -l < $SCRATCH/vol1-entries.txt`
Expected: ~159 lines.

- [ ] **Step 2: Sweep vol 1 entries D29–D166 and the "Current iteration" section**

For each entry in `$SCRATCH/vol1-entries.txt`: read it in vol 1; if it closes a branch or
states a binding rule not yet covered by a Task 4 bullet, append one bullet to the matching
class (same format, `[Dnnn]` pointer); then mark the line done by appending ` OK` in
`$SCRATCH/vol1-entries.txt`. Structural sections (Objective, Persistent cycle, Knowledge
retained, queue, Completion rule) are marked ` OK` without new bullets — Task 4 covered them.

- [ ] **Step 3: Sweep Phases 1–21 and Gold-era standing lessons**

Same procedure over `docs/archive/legend/session-handoff-2026-07-16.md` (each `## ` section)
and, from `docs/archive/bronze-to-gold/arena-queue.md`, the "MEASUREMENT POLICY v2" rules
(deltas-only, baseline horizon, decision bands) — distilled into §(g) if not already present.

- [ ] **Step 4: Verify completeness and size**

Run: `grep -vc ' OK$' $SCRATCH/vol1-entries.txt`
Expected: `0`.
Run: `wc -c docs/CONSTRAINTS.md`
Expected: ≤ 35,000 bytes (soft target ~150 bullets; if far over, fold same-class duplicates —
do NOT drop closures).

- [ ] **Step 5: Commit**

```bash
git add docs/CONSTRAINTS.md
git commit -m "notes(constraints): sweep D29-D166, Phases 1-21, and Gold-era standing lessons into the knowledge base

Every vol-1 entry checked off; measurement policy distilled into section (g).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Freeze volume 1, open volume 2

**Files:**
- Modify (append-only): `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md`
- Create: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md`

**Interfaces:**
- Consumes: `docs/STATE.md`, `docs/CONSTRAINTS.md` (referenced by name in both files).
- Produces: the live-volume path named in STATE.md §5 (Task 3 already wrote it — must match exactly).

- [ ] **Step 1: Append the freeze note to vol 1 (exactly this, nothing else)**

```markdown

## 2026-07-23: volume frozen at D166 — continue in legend-top3-experiment-cycle-vol2-2026-07-23.md; distilled state → docs/STATE.md, closed branches → docs/CONSTRAINTS.md
```

Run: `git diff data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md | grep -c '^-[^-]'`
Expected: `0` (append-only — no removed lines).

- [ ] **Step 2: Create vol 2 with exactly this content**

```markdown
# Legend top-3 experiment cycle — volume 2 (opened 2026-07-23)

Objective, persistent cycle, and completion rule: see volume 1
(`legend-top3-experiment-cycle-2026-07-18.md`, frozen at D166). Live state:
`docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` — check before proposing.

Per-experiment obligations: one entry here (same style as volume 1); a CONSTRAINTS bullet
for anything closed; a STATE.md §4 update. The first session ending with this file over
100 KB freezes it with one appended note and opens volume 3.

<!-- entries below -->
```

- [ ] **Step 3: Verify STATE pointer matches**

Run: `grep -c 'legend-top3-experiment-cycle-vol2-2026-07-23.md' docs/STATE.md`
Expected: ≥ 1.

- [ ] **Step 4: Commit**

```bash
git add data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md \
        data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md
git commit -m "notes(ledger): freeze journal as volume 1 at D166 (single appended note); open capped volume 2

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Companion edits (README, AGENTS.md, cgauto strings) + suites

**Files:**
- Modify: `README.md`, `AGENTS.md`, `cgauto/make_bot_pdf.py:12,88`, `cgauto/ramp.py:12`, `cgauto/portfolio_geometry_prospective_gate.py:242`, `cgauto/portfolio_prospective_gate.py:280`, `cgauto/portfolio_motion_followup.py:268`

**Interfaces:**
- Consumes: `docs/STATE.md` (Task 3), archive paths (Tasks 1–2).

- [ ] **Step 1: Replace the stale README banner**

In `README.md`, replace the blockquote that begins `> Current project state (2026-07-17):`
and ends `the Wood-league overview below is historical onboarding.` with:

```markdown
> **Start here: `docs/STATE.md`** — live state (resident, goal, standing rules, open
> thread), then `docs/CONSTRAINTS.md` before proposing any experiment. Superseded docs:
> `docs/archive/INDEX.md`. The Wood-league overview below is historical onboarding.
```

- [ ] **Step 2: Update the AGENTS.md reading order**

Replace:

```markdown
This repository has a long experiment history. Read the current handoff and
the focused protocol/result needed for the task; use `rg` instead of loading
the full experiment ledger unless archaeology is explicitly required.
```

with:

```markdown
This repository has a long experiment history. Reading order: `docs/STATE.md` (live state),
then `docs/CONSTRAINTS.md` before proposing any experiment, then the tail of the live ledger
volume named in STATE §5. Use `rg` and `docs/archive/INDEX.md` instead of loading frozen
ledgers unless archaeology is explicitly required.
```

- [ ] **Step 3: Update the five functional strings in cgauto**

- `cgauto/make_bot_pdf.py` line 12: `Default out: docs/troll-farm-bot.pdf` → `Default out: outputs/troll-farm-bot.pdf`
- `cgauto/make_bot_pdf.py` line 88: `os.path.join(ROOT, "docs/troll-farm-bot.pdf")` → `os.path.join(ROOT, "outputs/troll-farm-bot.pdf")`
- `cgauto/ramp.py` line 12: `See docs/ROADMAP.md.` → `See docs/archive/bronze-to-gold/ROADMAP.md.`
- `cgauto/portfolio_geometry_prospective_gate.py` line 242: `"protocol_document": "docs/portfolio-geometry-prospective-gate-2026-07-16.md",` → `"protocol_document": "docs/archive/legend/portfolio-geometry-prospective-gate-2026-07-16.md",`
- `cgauto/portfolio_prospective_gate.py` line 280: `"protocol_document": "docs/portfolio-prospective-gate-2026-07-16.md",` → `"protocol_document": "docs/archive/legend/portfolio-prospective-gate-2026-07-16.md",`
- `cgauto/portfolio_motion_followup.py` line 268: `"protocol_document": "docs/portfolio-motion-followup-2026-07-16.md",` → `"protocol_document": "docs/archive/legend/portfolio-motion-followup-2026-07-16.md",`

- [ ] **Step 4: Run the regression suites**

Run: `python3 -m pytest tests/ -q 2>&1 | tail -3`
Expected: all tests pass (≈246+ passed, 0 failed).
Run: `cd rust && cargo test --workspace -q 2>&1 | tail -5; cd ..`
Expected: all tests pass (pre-existing ignored tests and warnings are fine — code was not
touched; this confirms no accidental breakage).

- [ ] **Step 5: Commit**

```bash
git add README.md AGENTS.md cgauto/make_bot_pdf.py cgauto/ramp.py \
        cgauto/portfolio_geometry_prospective_gate.py cgauto/portfolio_prospective_gate.py \
        cgauto/portfolio_motion_followup.py
git commit -m "notes(pointers): README/AGENTS point at STATE+CONSTRAINTS; fix 5 functional docs/ path strings in cgauto

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Acceptance verification + memory repoint

**Files:**
- Modify: `/home/tarstars/.claude/projects/-home-tarstars-prj-troll-farm/memory/MEMORY.md`, `.../memory/legend-era-state.md` (outside repo — session-agent memory)

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Spec post-conditions**

Run: `ls docs/ | wc -l`
Expected: ≤ 10 (should be 9: STATE.md, CONSTRAINTS.md, archive, mechanics.md, plays, statement.md, storage-migration sha256, storage-policy.md, superpowers).
Run: `wc -c docs/STATE.md docs/CONSTRAINTS.md AGENTS.md data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md | tail -1`
Expected: total ≤ 50,000 bytes.
Run: `grep -c '^| ' docs/archive/INDEX.md`
Expected: `37` (header row + 36 file rows).
Run: `for f in silver-experiment-log.md HANDOFF.md session-handoff-2026-07-16.md; do rg --files docs/archive | grep -c "$f"; done`
Expected: `1` three times.

- [ ] **Step 2: Rename integrity over the whole reorg**

Run: `git log --oneline -8 && git diff --stat -M100% <commit-before-task-1>..HEAD -- docs cgauto/HANDOFF.md | grep -c '=>'`
(`<commit-before-task-1>` = the parent of Task 1's commit.)
Expected: `36` rename lines (minus any documented `mv` fallbacks, which must appear as
add+delete pairs of identical size).

- [ ] **Step 3: Audit-map sanity**

Run: `wc -l $SCRATCH/constraints-audit.tsv && grep -vc ' OK$' $SCRATCH/vol1-entries.txt`
Expected: `N_SRC` lines and `0` — every knowledge bullet mapped, every vol-1 entry swept.

- [ ] **Step 4: Repoint session memory (outside repo, no commit)**

In `memory/legend-era-state.md`: replace the line
`**Master journal (READ FIRST):**` paragraph's first sentence so it names `docs/STATE.md` as
the entry point and the vol-2 path as the live ledger, with vol 1 as frozen history. In
`memory/MEMORY.md`: in the READ-FIRST block, replace the journal path with
`docs/STATE.md → docs/CONSTRAINTS.md → vol 2 (data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md)`.

- [ ] **Step 5: Final commit (only if verification tweaks touched repo files)**

```bash
git status --short   # expect: empty or only intentional leftovers
git commit -aqm "notes(reorg): acceptance fixes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" || echo "nothing to commit"
```
