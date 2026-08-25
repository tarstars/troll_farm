# GOAL (archived at close, 2026-08-25T23:15Z; was the live mission 16:39Z–23:15Z) — drive Candidate 2 (the swap, no lock, proved) to its gates, with the per-troll stall gate and the quarantine move beside it

You are `local_claude_1`: coordinator, integrator, and the **sole** Arena controller (owner,
2026-08-24). Work this goal one wake at a time when the owner runs it (`/goal coordination/GOAL.md`
or a recurring wake); otherwise act when prompted. Decide, act, record; do not ask the owner what
to do next between gates. Under `/goal` pace with foreground `sleep 540` + a sweep; publish every
ruling `requires_ack: true` toward the ruled party; stamps from `date -u` in the command that
writes the file.

Owner rulings 2026-08-25 ~15:55Z (coordinator session; the coordinator's transcription, recorded
in `docs/RULES-LEDGER.md` R-1a and the task cards): **(1) Candidate 2 = swap, with no special lock
— check the algorithm and prove that the back-swap cannot be chosen, because the mobile troll
wants to go through the working one; "simple, clear set of rules"; (2) Candidate 1: keep the
code (parked); (3) charter the per-troll stall gate; (4) the message-quarantine list lives on
`main`.** No Arena action is authorized by these rulings or by this file: the Candidate 2 read
(G-2) and block (G-3) each need the owner's separate go, surfaced before they start.

## Done when ALL of these hold

1. `20260825-dance-cure-candidate-2-swap`: G-0 **DESIGN_ACCEPTED** by codex_1 — the exact swap
   predicate, the **proof** that the same pair cannot exchange twice with a fixed target (every
   edge case enumerated: three trolls, speed 2, teammate on the goal, transient blocker, unknown
   previous cell, orchard scoping), the v5 telemetry grammar, the parity plan, the pre-committed
   panel and read bars. Then G-1 delivered by claude_1 and reproduced by codex_1 from a fresh
   archive (rule-off byte-identical; panel bounds; positive control; poison arm caught by the
   swap-loop counter; **swap loops = 0, any positive count = stop and ask, never a lock**).
2. G-2 is **ready to submit** — the instrument arm hash-verified under `cgauto/submissions/`, the
   read ledger opened — and the owner has been asked, in one plain-words message, for the Arena
   go. If the go comes while the goal is live: submit, collect ≥ 160 games before any resubmission,
   grade against the pre-committed bars (baseline = the v4 read), codex_1 checks; then ask for G-3.
3. `20260825-p4-per-troll-stall-gate`: G-0 accepted by claude_1, G-1 delivered by codex_1 and
   reproduced by claude_1 — the Candidate 1 poison arm (a troll parked 194 turns) **fails** the new
   gate; Candidate 2's G-1 uses it once accepted.
4. `20260825-quarantine-on-main`: patch delivered by codex_1 (after its P4b build), tests green,
   dry-run sweeps for every agent id report today's 12 quarantined paths and 0 errors, protocol
   §10.2 updated; integrated by you, every agent's sweep copy (launcher clone included) updated
   from `main`.
5. Transport clean, `origin/main` == your branch head, worktree clean, STATE §4 one line per task,
   this mission archived under `coordination/goals/` and `coordination/GOAL.md` returned to "no
   active mission"; the owner's queue = the Arena go(s) for Candidate 2 and, later, its verdict
   sheet.

**Time box:** 2026-08-27T12:00Z; then write what is and is not done and stop.

## Every wake — the ritual

`python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`; read every new message whole from
the peer's remote ref; `--mark` as its own step and commit the seen-state. **Unblock peers first**
(rulings owed, questions, acks). Verify peer claims by execution before integrating — re-derive
every headline count from published rows before any owner text. Publish via `lint_outbox.py
--staged` → commit explicit paths → push → verify → sweep. A peer silent past its 15-minute lease
after an ack-required message: `ssh troll-vm`, read the launcher wake log and the agent's
`session.log` tail, check `df -h`, before assuming it is thinking. Nothing owed → say `idle —
nothing owed` and stop.

## Authority — may / may not

**May:** charter, rule and amend on the three tasks; run read-only measurements; place claude_1's
delivered arms under `cgauto/submissions/` hash-verified; write in `local_claude_1/**`, the task
records, status, STATE §4, `docs/RULES-LEDGER.md` (owner rulings only, transcribed); integrate
the quarantine change into `main`; clean stale scratch on the VM when a gate is blocked by it
(record what was removed); fast-forward `origin/main` when nothing foreign is on it; spawn a local
subagent for a build a peer cannot deliver.

**May not:** any Arena action without the owner's go for that exact action; touching the
resident, the dev copy `fff6669b…`, `data/raw/games/`, the cron; merging peer branches (pin their
commits); chartering route-around, Candidate 3, or the structural step; adding a lock or timer to
the swap in any form; changing a definition after counting has begun (a change = a new revision,
re-accepted, re-counted); ruling KEEP yourself.

## Stop and ask the owner if

- the proof fails — codex_1 or claude_1 finds a case where the same pair can exchange twice with a
  fixed target and no rule text without a lock closes it;
- the panel shows swap loops (planner churn) — the owner decides whether Candidate 3 (score
  smoothing) is chartered first;
- G-1 cannot make the rule inert-by-construction (rule-off parity fails);
- the read shows a pathology the card's kill rules do not name; a measurement contradicts a
  standing ruling; the ladder slot is needed for anything else; an Arena error occurs.

## Standing rulings still in force

Candidate 1 PARKED, code kept; swap cure (the old R-1 α revision) retired — Candidate 2 is its
successor under R-1a, not its revival; anti-benching r2 rejected; replant option unimplemented;
archive-wide defect counting closed; publication gateway closed; D-1 off replays is an upper
bound; plain words in owner text; fresh-archive extracts are scratch removed by `trap`; a dying
session's last act is a `blocker`.
