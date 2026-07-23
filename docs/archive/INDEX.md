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
