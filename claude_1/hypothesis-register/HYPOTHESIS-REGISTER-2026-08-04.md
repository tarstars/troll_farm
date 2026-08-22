# Score-improvement hypothesis register — 2026-08-04 (owner-approved programme)

Owner directive 2026-08-04: twelve prioritized hypotheses to move the mature score from the
current band (restore 23.56 / rank 32; two exact mature runs median 24.41) toward the goal
≥ 25.40. Gap to close: **≈ +1.0–1.8 points**. All work respects the standing discipline:
paired development panels first, the ≥ +1.0 rating bar before any Arena cycle
(`docs/APPROACH-REGISTER-2026-07-30.md`), mutations only through the controller, and nothing
below re-opens a ledger-closed branch.

Evidence base: the 2026-08-03/04 orchard ablation cycle and postmortem, the 8-leg / 1,280-game
night A/B (`chatgpt_1` audit: orchard +0.585 mean, CI [−0.645, +1.815], **+38 wins and
+22 catastrophes** per 640 games; enemy-arrival-kept activations −52.2 margin vs −10.2
blocked), the r36 coverage panel (79 % region coverage), the top-player phase decomposition
(break-even until opponent worker 3, then opponent scoring multiplies ~12×), and the
2026-07-29 terminal synthesis (policy, not architecture, must close the gap).

Owner-assigned execution model: `claude_1` organizes, delegates to subagents, analyses;
environment-bound runs (closed-loop seeds, 516-task panels, Arena) go to `local_codex_1`.

| # | Hypothesis | Mechanism / key evidence | First test | Status |
|---|---|---|---|---|
| 1 | **Opportunity-cost orchard activation gate** — activate only when projected orchard value exceeds the displaced starter task by a frozen margin | Bad activations are identifiable before they happen: enemy-arrival-kept stratum −52.2 margin vs −10.2 blocked; chatgpt_1's audit names this the next plausible gate; static distance/idle gates rejected | Closed-loop paired panel on fresh common seeds (integrator-run) after a C0-bridge equality proof | **CLAIMED — claude_1 (task 20260804-h1-orchard-opportunity-cost-gate)** |
| 2 | **Catastrophe mechanism census** — classify all 91 orchard-leg catastrophes (oscillation-locked / starter-parked-while-opponent-scales / map class) | Data already collected (sanitized night-A/B corpora); converts H1/H3/H8 from guesses into targeted fixes | Pure analysis of existing corpora; no ladder cost | open — natural chatgpt_1 or subagent task |
| 3 | **Pressured-orchard abandonment** — strategic release of the camped starter when score trajectory crosses against us or opponent fields worker 3 | Orchard polarization: +38 wins / +22 catastrophes; camps hold through −500 blowouts today | Development panel: abandonment arm vs current, catastrophe count and negative-margin mass primary | open — sequenced after H2 census |
| 4 | **H3a pressure-conditioned opponent-crop priority** | Top-ranked in all-agent review (rubric 82); DiD 0.606; the only denial lever with a live statistical signal | Resume the existing task's staged gates (trigger preflight → C0/C1/A1 bridge → three-arm value) | open — task exists, paused for owner priority |
| 5 | **Orchard eligibility relaxation** — distance ≥ 11 → 9/10, Dormant window 100 → 150 | 24/25 packet games never found a qualifying site; camp treatment worth +61 own score; overnight audit rejected *other* gates but never tested eligibility | Paired development panels per relaxation arm | open |
| 6 | **Banana wood-printer restoration (R2)** — separate protected cut/replant plot, not a mother replacement | +162.3 own score development evidence; both live attempts implementation-invalid (unmeasured, not rejected); chatgpt_1 concurs it is a distinct architecture | Restoration on the stable parent → IMPLEMENTATION_VALID verdict → panels | open — already assigned to claude_1 (banana-restoration-r2) |
| 7 | **Roster-conditioned denial intensity** — scale aggression when opponent reaches worker 3+ | Phase decomposition: break-even at opponent worker 3, then ~12× opponent scoring | Development panel with roster-trigger arm | open |
| 8 | **Oscillation episode breaker** — minimal period-2 detector on the full exact source | Live episodes up to 244 turns; half-size no-backtrack candidates failed transfer, full-source minimal breaker untried | Development panel; hard gate on catastrophes/negative mass (previous rejection mode) | open — high risk |
| 9 | **Second mother / camp production scaling** | Camp games: 106 harvests avg, ~10 wood sacrificed | Panel must beat the B3.10 ~4.8/game nearby-harvest ceiling to proceed | open |
| 10 | **Second-troll timing audit** — train-turn distribution vs top-5 t≈106 | Deadline fallback has 0 % coverage while its guard runs 35k times: dead weight or masked late trainings | Replay-corpus audit only | open — audit, not lever |
| 11 | **Mid-game idle harvest extension** | ~139 WAITs in a single game; idle harvest currently endgame-only | Cheap development panel; low expectation (tuning history hints prior rejection) | open |
| 12 | **Port one measured opponent mechanism** (N5 endgame plant-contest) inside the freed 10.4 % byte budget | Readable source + byte headroom exist; imitation is broadly closed, so only a narrow mechanism-level port with its own frozen gate survives | Await N5 re-review, then a single-mechanism protocol | open — last |

## Sequencing note

H2 feeds H1/H3/H8 and costs nothing — it should run concurrently with H1's implementation
phase. H4 and H6 are already-assigned tasks and resume when the owner sequences them. H5's
arms can share H1's panel infrastructure. Nothing above requires an Arena cycle until a
candidate clears +1.0 in development.
