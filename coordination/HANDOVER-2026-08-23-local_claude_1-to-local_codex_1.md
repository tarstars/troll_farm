# Coordinator handover — `local_claude_1` → `local_codex_1`, 2026-08-23

Owner instruction, 2026-08-23: **"give lead position to local_codex_1"**. This returns the role you
held until 2026-08-06 and transferred to me at
`coordination/HANDOVER-2026-08-06-local_codex_1-to-local_claude_1.md`.

**Read this, then `docs/GOALS.md`, then `docs/STATE.md`.** Everything else is downstream.

## 0. What you are taking, and one fact about the gap

You hold **coordinator, integrator, and sole Arena controller** from the moment you acknowledge.
I hold none of them after that.

**Your branch has not moved since 2026-08-06.** Seventeen days ran without you and the project is
not where you left it: the whole cure programme has been measured and largely retired, two peer
agents now run unattended on a VM, transport is schema v2 with lint enforcement, and as of today we
measure behaviour on **real ladder games** rather than a 34-fixture library. Do not act from the
08-06 handover's picture. It is stale in almost every particular.

## 1. The single most important fact

**The 34-fixture library that steered two years of work is a biased sample, and the ladder cannot see
the programme built on it.** Ten pairs, champion against the bot two generations back: **+0.17,
≈0.00**. That measurement re-ranked everything.

As of today we grade **our own real games** instead. `docs/GOALS.md` holds three goals with one
number each. G1 stands at **469 real games**:

- trolls blocking each other: **0 %** — against 23 % for the opponents in the same games and 43 % for
  our own pre-cure bot at matched troll count;
- dancing on the spot: **11 %** of games, replicated exactly across two independent batches;
- a troll wanting real work and being given nothing: **615 of 84,928 troll-turns (0.72 %)**, absent
  in 40 % of games, and over half of it in the worst 10 %.

## 2. Arena state — you are the only one who may touch it

| | |
|---|---|
| resident | NARRATE **v3** instrument, submission `41182608`, agent `6652642`, sha `9a3e8758…` |
| reads | 21.37, rank 41/176 |
| champion of record | door 1, `cgauto/submissions/candidate-door1-pure-deletion.rs`, sha `547fa706…` — **off ladder** |
| restore obligation | **NONE.** Owner 2026-08-23: *"It doesn't really matters, who is on ladder."* Door 1 is documented as the fallback and nothing more. |

- Submissions go through `cgauto/api_submit_once.py` with `--expected-sha256`. **Never**
  `night_runner.py` for a single-arm run: its end-of-block tree opens an unrelated A/B.
- `NIGHT-HALT` stays on the VM; `night-runner.service` stays down.
- **An instrumented bot can never be champion** — it changes the command stream.
- ⚠ `docs/PROMOTION-RUNBOOK.md` must not be followed: its abort path restores a bot retired weeks ago.

## 3. Owner rulings from today — in force, do not reopen

1. **The ladder reopened** for the measuring bot; who sits on it does not need managing.
2. **Archive-wide defect counting: CLOSED**, superseded by fresh-game grading. Standing preference,
   and it governs how you choose measurements: **prefer a fast loop on new games over a slow complete
   pass over the archive.** Not licence for weaker evidence.
3. **The chatgpt_1 publication gateway: CLOSED**, never built.
4. **Autonomous operation: PAUSED** for a session of its own. Do not solve pacing in the margins and
   do not raise it as a decision. The accepted cost is that runs advance only while the owner is present.

## 4. What I owe you, unfinished

- **A ruling on Phase 3b of `20260820-pair-selector-anti-benching`, and it is now YOURS.** I ruled at
  13:14 that Phase 3b was aimed at a class our instrument could not see, and held its cost panel.
  **claude_1 then measured it anyway** and the answer is not zero: **339 turns / 34 occasions** across
  14 of 49 verified games, every one a replanting job the bot would have taken — but 35 of 49 games
  are zero and the worst tenth holds over half of it. **My ruling was too quick and I did not get to
  correct it.** Decide whether that earns a ladder slot.
- **Ack debt: 18 messages unread at transfer**, acks outstanding. I read the two substantive ones
  (the reach measurement and its denominator note) and left the rest.
- **G1 is 469 of a 500 target.** One more collected batch closes it.

## 5. Traps that cost something today — each is in `docs/METHODS-LEDGER.md`

- **`seat-from-the-replay`** — the battle listing's `position` and the replay's frame `agentId` are
  different fields and they disagree. A wrong seat **prints numbers, not errors**. Resolve seat from
  the replay's own `agents` array and assert your telemetry is absent from the other seat.
- **`collect-before-you-resubmit`** — the battle listing is a ~160-game **rolling window**. Submitting
  the next arm makes the previous arm's games unenumerable and therefore unfetchable. Collect first.
  Read 1's games survive only because collection happened to come first.
- **`shared-runners`** — I committed 149 replays carrying other players' account ids past
  `cgauto/export_agent_replays.py`, which exists to strip exactly those. Sanitised. Before writing
  collected external data into the repo, find the existing sanitiser.
- **Detectors return a dict**, not a list. `len()` on it gives 4 every time; the field is `["count"]`.
  I published "596 episodes" from this and caught it only because two unrelated totals were identical.
- **Check exit status on its own line, never behind a pipe.** `lint | tail && commit` gates on
  `tail`. I broke a line budget this way today, having quoted the rule at someone else that morning.

## 6. Standing discipline, non-negotiable

- **No rate without its control.** An "N of N" never tested against a deliberately wrong pairing
  describes the sample, not the world. Two such figures were withdrawn today — mine and claude_1's.
- **A zero is only reported once the detector has been shown able to fire.** A vacuous pass is
  recorded UNMEASURED, never filled with synthesised cases.
- **Charter, do not build.** `claude_1` builds, `codex_1` reviews. Both run unattended on the VM and
  wake on mail from someone else. Neither may submit; neither holds the platform credential.
- Ritual: `python3 scripts/inbox_sweep.py --me local_codex_1 --fetch` → read **every** new message in
  full → `--mark` as its own step. I violated this today and missed a review that had already landed.
- `scripts/lint_outbox.py` must exit 0 before you push. A v2 handoff pins artifacts at a commit that
  actually contains them — verify the full SHA, do not extend a short one from memory.

## 7. Where things live

- Goals: `docs/GOALS.md` (60-line budget, enforced) · live state: `docs/STATE.md` (150, enforced)
- Method rules: `docs/METHODS-LEDGER.md` · winning rules: `docs/RULES-LEDGER.md`
- Autonomous goal driver: `coordination/GOAL.md` — **rewrite its agent identity to yours**
- Today's evidence: `local_claude_1/narrate/` — corpora, identity checks, gradings, block ledger
- Platform credential: `project_host` only, `/home/tarstars/prj/troll_farm/cgauto/cg_session.txt`

## 8. Transfer completion condition

You publish an `ack` naming this file by exact path, and a `policy` announcing yourself as
coordinator, integrator and Arena controller to `claude_1`, `codex_1` and `chatgpt_1`. Until then I
remain responsible and will take no new action beyond answering questions.

Nothing in my namespace is yours to maintain; read it freely, and re-pin anything you rely on.
