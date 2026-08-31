# GOAL — Track N, the neural-network bot: the recovery programme after the second opinion (owner 2026-08-31 ~07:0xZ: "let's write down your 'What I'll do now' as goal file and set it in action")

**THE STANDING TARGET (owner 2026-08-29 14:4xZ, unchanged):** *a neural-network candidate that beats
the champion of record and orchard 6 on the local bench — at least 60 % wins over 400 games against
each, a positive mean margin, three gates in a row — exported as one Rust file under 100,000
characters (counted in UTF-16 units) at ≤ 15 ms a turn on this host, its bed passed and a second
agent's reproduction in hand: ready for the ladder.* **Budget:** the target by 2026-10-17; if the
target date passes with no candidate through Phase 3's gate, the programme stops and reports. The
clone milestone was reached 2026-08-30, two weeks early; Phase 4 (the one-file export with the CPU
fallback) is complete and reproduced twice. **The one message the owner gets:** "the candidate is
ready — your prediction, and the platform's hour."

**Where the experiment stands (2026-08-31 morning):** no self-play run has beaten the clone
(9 of 48 vs the champion's file). Full-parameter PPO collapses the clone by update 1,500 in every
configuration; the staged scope (movement frozen, plan + value learn) holds the bar then drifts.
chatgpt_1's adversarial review (`chatgpt_1/nn-way-b/experiment-second-opinion-2026-08-31.md`,
verified by the coordinator against the code) corrected the frame: the real credit horizon is the
32-mini-step rollout buffer (~8–11 game turns), not 300 turns; run I's anchor never faded (0.099 →
0.095), so the leash-decay story is unsupported; the 48-game bench is a ±5-win scout, not a
selector; and the entropy bonus over a 400-way plan space (only 106 targets teacher-supported) is
the best-fitting explanation of the staged drift. The full dossier:
`local_claude_1/nn-bot/EXPERIMENT-2026-08-31.md`; the reviewer's staged recovery plan:
`chatgpt_1/nn-way-b/self-play-training-recovery-review-and-staged-plan-2026-08-31.md`.

## THE PLAN NOW (in order; each step lands on `main` before the next starts)

1. **Errata into the dossier** (`EXPERIMENT-2026-08-31.md`): the four corrected claims, marked in
   place — the rollout-truncated credit horizon; the anchor that never faded; ±5.3 (95 %), not ±2,
   for a 48-game read; the "wins ~2 %" sentence (run I's champion-only telemetry was 18–21 %).
   Update the published artifact page the same way. *Done when:* the corrections are on `main` and
   the artifact republished.
2. **Acks and protocol adoptions**: acknowledge both review handoffs (05:59Z, 06:44Z), adopting —
   the paired per-cell bench protocol (48-game panel = scout; a locked ≥ 144-game panel =
   confirmation; paired margin deltas with a bootstrap interval; 400 + 400 stays the promotion
   gate); the target-KL repair (aggregate PLAN-row KL over the epoch, mean and max logged, the
   early-stop rule on the aggregate — a small trainer change, tests included); and the recovery
   plan's gate discipline (the cluster arms stay exploratory evidence, no gate-skipping).
   *Done when:* the acks are pushed and the target-KL repair is merged with its tests.
3. **Gate 0 — measurement before any new run** (charter claude_1; chatgpt_1 reviews):
   the corrected gradient instrument run on fixed common observations for the clone / G@500 /
   H@500 with resumed optimizer state; the rollout telemetry added to the trainer — per update:
   terminal-bearing rows, the fraction of rows whose trace contains a real terminal before the
   buffer cut, raw advantage mean/std before normalization, bootstrap share of the return target;
   and one independent critic calibration (a frozen checkpoint, complete held-out episodes,
   realized return-to-go vs the value head). *Done when:* the three reports are on `main` and say
   whether the value-gradient path and the bootstrap-noise mechanism are convicted or acquitted.
4. **The entropy falsifier — two fresh arms under one post-Gate-0 pin** (the reviewer's 08:57Z
   amendment, adopted: comparing a new arm against *historical* run I would be confounded by
   Gate 0's own trainer repairs): from the same clone, same seed, same everything on the merged
   post-Gate-0 trainer — **E01** (control, `entropy_coef = 0.01`) and **E00** (treatment,
   `entropy_coef = 0`); **both arms on the cluster, same payload, same resource class** (the
   reviewer's 09:47Z platform-confound blocker, upheld: one-arm-per-platform would make entropy
   collinear with the machine), the host staying the evaluation machine; every arm's environment,
   source hashes and exact command pinned in the card; benched at the same fixed updates on the
   scout panel with the paired protocol, the treatment effect read as E00 − E01 on paired cells.
   *Done when:* both curves are on the card **and the frozen Gate 1 verdict is computed.** The
   gate of record is the reviewer's 10:36Z definition as corrected by its 11:45Z panel note
   (adopted): 144 cells are sufficient — the two confirmed ages are *repeated measures of the
   same 144 map-seat units*, so the interval is the 144-unit clustered/repeated-measure bootstrap
   of the per-cell two-age mean delta, never a 288-row pool; the mean effect must also be
   positive at each age separately; the clone non-inferiority allows at most 6 net cells lost (of
   144). Scouts at updates 500–2,500 on the 48 cells; the four frozen outcomes:
   `ENTROPY_CONFIRMED` / `ENTROPY_PARTIAL` / `ENTROPY_NOT_CONFIRMED` / `INCONCLUSIVE` (the gate
   returns INCONCLUSIVE on incomplete identity, population, execution or evaluation evidence —
   underpowered is a verdict, not a license). No arm launches before Gate 0 closes.
5. **The cluster reads** (as they land, ~19:00–20:00Z): retrieve a2 / e2 / i2, bench each final
   snapshot on the scout panel — exploratory evidence only; i2 is read as "constant vs nearly
   constant anchor", not a fade test. *Then the decision*, on the evidence of 3–5: the next lever
   in the reviewer's ranking (diagnostics-first; entropy ablation; true long-horizon credit via
   longer/episodic rollouts — never a bare λ=1 under the 32-step buffer; value-trunk separation if
   convicted; target commitment / previous-target memory as a design change; a tiny-rate joint
   fine-tune with a replay-cloning retention loss, last). A design change to the plan semantics
   (the reviewer's stages 2–3) is spec'd on the card and reviewed before any build.

**Standing authorizations (unchanged):** build, charter, review and reproduce on the VM; train on
this host at low priority with at most 14 threads; downloads under 50 MB; the cluster within the
already-authorized pool ("gpu"), with consistent budgets (either `--hours` or
`--total-turn-steps`, never an inconsistent pair) and the salvage uploads on. **Never without the
owner's word:** any platform action, deleting or moving data, cloud spend beyond the pool in use,
any submission. **Reporting:** one plain-words line per milestone in the board's owner's queue;
the report PDF re-issued at the owner's request or at a phase boundary.

## Each wake (self-paced /loop; also on ack-required mail and finished background jobs)

1. `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`;
   read every new message whole before publishing anything; `--mark` only after reading; quarantine
   by adjudication what blocks the sweep.
2. Advance the lowest-numbered step of THE PLAN NOW that is not done; record results on the card
   (`coordination/tasks/20260829-nn-bot-way-b.md`) as they land.
3. Rule on anything that blocks a peer; land artifacts on `main` at each gate; mark stalls by the
   cards' dead conditions.
4. Keep the board truthful in the same push (`git push origin agent/local_claude_1:main`); pull the
   checkout `/home/tarstars/prj/troll_farm` in a separate call.

## Not allowed
Any platform action (the ladder is codex's until the owner says otherwise); deletions or moves of
data; new cluster trees/pools; unfreezing a joint fine-tune before Gate 0's instrument and the
critic calibration are read (the reviewer's rule, adopted).

## Done when
Either a candidate passes the standing target's gates (then the one message to the owner), or the
programme's stop condition fires (2026-10-17, or the card's dead conditions) and the final report
says what was learned. Each wake ends with the board truthful and `origin/main` ==
`agent/local_claude_1` == the checkout.

*(The third-troll experiment, the floor and the apple farm — the pre-freeze ladder work — are on
hold while the platform is codex's; their state is in git history of this file and on the board.
The champion of record: `41202036`, sha `0e92f8fa…` — the restore target for any revert.)*
