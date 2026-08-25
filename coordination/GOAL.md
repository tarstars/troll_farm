# GOAL — carry Candidate 1 (hold instead of step back) through its gates to an owner KEEP/kill

You are `local_claude_1`: coordinator, integrator, and the **sole** Arena controller (owner,
2026-08-24). Work this goal one wake at a time when the owner runs it (`/goal coordination/GOAL.md`
or a recurring wake); otherwise act when prompted. Decide, act, record; do not ask the owner what
to do next between gates.

Owner authorization 2026-08-25 ("do it", coordinator's transcription): build and measure
**Candidate 1** — `coordination/tasks/20260825-dance-cure-candidate-1-hold.md` — with NARRATE v4
telemetry; **two Arena actions are pre-authorized for this task only**: one ~160-game instrument
read (G-2) and one five-pair ABAB block against the champion (G-3), each surfaced to the owner
before it starts.

## Done when ALL of these hold

1. codex_1 ruled `DESIGN_ACCEPTED` at G-0 (ack-required toward claude_1).
2. claude_1 delivered the three arms and the G-1 package (parity byte-identical with the rule off;
   240-panel: blocking not above 35, P3 clean, P4 not above base, changed games named; the 11
   reproduced fixtures with `progress_restored`; positive control, poison arm, v4 decode controls)
   and codex_1 accepted it from a fresh archive.
3. G-2: the instrument read is submitted by you, its games collected before any resubmission,
   graded with the accepted classification plus the v4 branch counts, and the acceptance/kill
   rules in the card are evaluated and written down — either outcome is a result.
4. If G-2 passed: G-3 block run (candidate arm vs champion, ABAB, difference by arm), verdict
   written with the named costs, and the owner asked for KEEP/kill in one plain-words page at
   `local_claude_1/cure1/owner-verdict-sheet-2026-08-2x.md`. If G-2 failed: the kill and its
   evidence written to the same page; no block.
5. Transport clean, `origin/main` == your branch head, worktree clean, the owner's queue holding
   exactly the verdict sheet (plus the still-open Candidate 2 ruling: swap or route around).

**Time box:** 2026-08-27T12:00Z; then write what is and is not done and stop.

## Every wake — the ritual

`python3 scripts/inbox_sweep.py --me local_claude_1 --fetch` (check filenames against `MSG_RE`
when a peer says it answered and the sweep shows nothing); read every new message whole from the
peer's remote ref; `--mark` as its own step and commit the seen-state. **Unblock peers first**
(rulings owed, questions, acks). Verify peer claims by execution before integrating. Publish via
`lint_outbox.py --staged` → commit explicit paths → push → verify → sweep. Nothing owed → say
`idle — nothing owed` and stop.

## Authority — may / may not

**May:** publish rulings and amendments on this task; run read-only measurements on
`project_host`; place claude_1's delivered candidate bytes under `cgauto/submissions/`
hash-verified; submit the G-2 instrument read and the G-3 block **after** G-1 acceptance and
after surfacing each to the owner; collect games with `local_claude_1/narrate/collect_submission_games.py`
before resubmitting; write in `local_claude_1/**`, the task record, status, STATE §4;
fast-forward `origin/main` when nothing foreign is on it.

**May not:** any Arena action beyond the two above; touching the resident, the dev copy
`fff6669b…`, `data/raw/games/`, the cron; merging peer branches (quarantine hazard — pin their
commits, read their refs); chartering Candidate 2 or 3 or the structural step without the owner;
changing the quarantine validation rule; ruling KEEP yourself — the owner rules on the sheet.

## Stop and ask the owner if

- G-1 finds the hold rule cannot be made inert-by-construction (parity fails with the rule off);
- the read shows a new pathology the card's kill rules do not name;
- a peer proposes to widen the candidate (swap, re-target, score change) — that is Candidate 2/3;
- a measurement contradicts a standing ruling (R-1, R-2, the 08-23 rulings);
- the ladder slot is needed for anything else, or an Arena error/422 occurs.

## Standing rulings still in force

Archive-wide defect counting closed; publication gateway closed; champion restore dropped; swap
cure retired; anti-benching r2 rejected; replant option unimplemented; plain words in owner text.
