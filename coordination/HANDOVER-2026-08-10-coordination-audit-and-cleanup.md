# Handover — coordination audit, hygiene cleanup, and the open protocol question

**Written 2026-08-10** (host clock, verified: `date -u` and the newest commit agree; see the
date hazard in §8). Author: `local_claude_1`. Owner-directed work, started from the request
*"analyse the project… create a stable protocol and a plan for cleaning up."*

## 0. Scope — read this before treating this file as authoritative

This document covers **one thread only**: the audit of the coordination system, the hygiene
cleanup executed on 2026-08-10, and the protocol redesign that has *not* been started.

**It supersedes nothing.** It does not replace `HANDOVER-2026-08-10-local_claude_1-session-close.md`
or any other handover, and it says nothing about the bot, the Arena cycle, the experiment
programme, or `docs/STATE.md` §1–§4. Those remain governed by whatever they were governed by
before. **This is not an entry point.** The project already has six documents claiming to be
the entry point, which is one of the findings below; this file deliberately does not become
a seventh.

If you only need the cleanup facts, read §2 and stop. If you are picking up the protocol work,
read all of it.

## 1. Verified state right now

Every number here is reproducible with the command beside it. Re-run them rather than trusting
the value — they will drift, and a stored constant that must be hand-updated is the single most
common failure in this repository.

| fact | value at writing | how to re-derive |
|---|---|---|
| trunk | `main` == `session-2026-07-01` == both origins, all at `e62d845f` | `git rev-parse main session-2026-07-01 origin/main origin/session-2026-07-01 \| sort -u \| wc -l` → 1 |
| worktrees | 2 (main + `troll_farm-local_claude_1`) | `git worktree list` |
| branches | 4 local, 9 remote | `git branch \| wc -l; git branch -r \| wc -l` |
| archive tags | 17, all pushed | `git tag -l 'archive/*' \| wc -l` |
| tests | 1626 passed, 3 failed | `.venv/bin/python3 -m pytest -q -p no:randomly` |
| transport | exit 1; delivery errors 0, quarantine errors 0, collisions 0, quarantined 9, unacked 80 | `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch` |
| byte-sacred invariant | holds on **both** pinned paths | `.venv/bin/python3 -m pytest tests/test_resident_source_invariant.py` |
| working tree | clean except untracked `local_claude_1/inbox-seen.json` | `git status --short` |

The 3 test failures are **pre-existing and unrelated** to this work — they were failing before
the cleanup at exactly the same count. See §5 (B7).

## 2. What was done, and how to undo it

Two commits: `71410605` (archive and remove) and `e62d845f` (close the traps).

**Nothing was discarded except cargo build cache.** Restore anything with
`git fetch origin --tags` then `git branch <name> archive/<tag>`.
The full inventory — every tag, what it holds, and what was salvaged from where — is
`docs/archive/worktree-salvage-20260810/README.md`. Highlights:

- 11 worktrees removed (10 in `/tmp`, plus the abandoned `troll_farm-local_codex_1`).
- 18 dead refs deleted, each preserved as a pushed `archive/*` tag. Several held real work:
  `archive/abgate-selfplay-gate` is an entire alternative bot (20 commits, measured REJECT);
  `archive/worktree-agent-a3371ee579c908bb9` carries two CRITICAL funding-loop fixes.
- 222 files stranded uncommitted in the abandoned worktree are on branch
  `archive/local_codex_1-stranded-20260810` (`2bfc462a`).
- ~10 GB reclaimed (`rust/target/debug`, `cgauto/profile`, `target/`, 64 `__pycache__`,
  4 GB of `/tmp/troll-*`). `rust/target/release/libtroll_farm.so` was **kept** — the Python
  ctypes tests need it.

Fixes in `e62d845f`: the `api_submit.py` ambiguity gate (§5), a real byte-sacred guard
(`tests/test_resident_source_invariant.py`), the `CONSTRAINTS.md` no-churn overturn marker,
both `coordination/templates/*` files, `coordination/README.md` dead links, and the
`peer-prompt.md` digest pin.

**Deliberately NOT deleted: any `origin/agent/<id>` canonical ref**, including dormant agents.
The transport validates that a v2 handoff is present on its sender's canonical branch, so
deleting one would permanently invalidate that sender's published messages. Verified after:
remote refs went 15 → 9 and delivery errors stayed 0. **Do not delete these.**

## 3. The diagnosis, condensed

The coordination system is not badly designed. **Nothing executes it.** Of ~20 operational
rules, 2 are enforced by code, both on the receiving side, after a violation is already
immutable. `docs/CONSTRAINTS.md`'s 185 bullets are enforced by nothing at all. Everything else
is prose a language model must recall across 3,229 lines of governing documents.

Measured consequence: **724 of the last 1,000 commits changed nothing but prose** (72%). The
multi-agent era produced 1,769 commits, 926 messages and 3,457 lines of transport tooling, and
moved the score 21.30 → 22.46 against a 25.40 target.

Root causes, in causal order:

1. **The transport is versioned inside the thing it transports.** `scripts/inbox_sweep.py`
   lives on the same branch-per-agent structure whose purpose is isolating agents, so isolation
   *causes* tool skew. At audit time four different versions were live (30,795–54,162 bytes).
   `chatgpt_1` saw zero messages for ten days, correctly reported having no work, and was
   disbelieved.
2. **Messages are immutable *and* strictly validated, so every mistake is permanent.** A
   correction does not clear a delivery error. That forced `quarantine.json` — a suppression
   primitive with one writer and, by design, no check that the target is invalid. Three
   adversarial review rounds each found real authorization holes in it.
3. **The ack graph has no terminating condition.** ACKs may require ACKs, `requires_ack()` is a
   pure OR with no override, and the template hardcoded `true` (now fixed). 239 files are named
   `*-ack.md`; only 76 have a populated `ack_for`. 163 acknowledgements discharge nothing.
4. **Truth is per-agent.** Same commit, same fetch: `local_claude_1` exits 1, `claude_1` and
   `codex_1` exit 2. The coordinator's own ACK is invalid and shows as a *warning* to its author
   but a *delivery error* to both recipients.
5. **Work has no queryable state.** `Status:` is free text with ~100 distinct values across 112
   task records; the documented query `grep -l 'Status: active'` returns 2 of them. 292 task-ids
   appear in messages with no task record — only 22% of discussed work is registered. Claims
   outnumber releases 91 to 7.
6. **The deepest cause: the instrument cannot resolve the effect sizes being chased.** Arena
   within-source σ = 1.098; difference SD at one run per arm = 1.552, so nothing below ~1.5
   points is detectable, while the goal needs +3.64. One mature read costs ~2 h. 247 candidates
   staged against 41 lifetime submissions. **When you cannot measure, you deliberate** — that is
   where the prose commits come from. The 491-line protocol is carrying epistemic weight that
   measurement should carry.

## 4. What is working — do not throw this away

- **Immutability holds**: 1 of 925 messages was ever edited after publication, because git makes
  that natural rather than requiring discipline. *Rules the substrate enforces are obeyed; rules
  requiring memory are not.* That is the whole design lesson.
- **Adversarial review works.** The project's own audit: *"the process — independent answers,
  capability-matched review pairing, declared conflicts, no verdict adopted without two reviews
  — caught essentially every serious failure. The tooling mostly makes that process auditable."*
  Every catalogued failure was found by independent re-execution.
- **The culture of self-correction is unusually strong.** Agents here retract their own published
  conclusions and say why. Build on this.

## 5. Open items

- **B6 — harness permission posture. THE OWNER HAS TAKEN THIS. Do not touch it.** For context:
  `~/.claude/settings.json` sets `defaultMode: bypassPermissions` and installs a PreToolUse hook
  auto-approving every Bash call; the one restrictive hook script is referenced by nothing.
- **B7 — 3 failing tests.** Stale pins to superseded source (an integrity flag now False, an
  instrumentation anchor that no longer exists, a "unique" constructor now duplicated). Making
  them green means deciding whether each pinned verdict still means anything — a call about the
  experiment record, not hygiene. Do not silently re-pin a number.
- **B9 — 325 files / 87 MB tracked inside gitignored `data/raw/`.** 290 are under
  `data/raw/games`, which `AGENTS.md` protects along with the 05:17 cron. Needs a deliberate
  decision, not a quick `git rm --cached`.
- **B10 — dangling LFS attribute** at `chatgpt_1/lfs-probe/.gitattributes`. Skipped: cosmetic,
  and in another agent's namespace, which the protocol says we do not rewrite.
- **The e7a 375-vs-586 question.** `coordination/tasks/20260804-readable-orchard-loc-cost.md`
  is closed as *"complete; 375-line readable orchard cost verified"*. An unpublished re-run
  under a stricter formatting definition, salvaged onto
  `archive/local_codex_1-stranded-20260810`, says **586** — same 79 functions, different
  pretty-printer. The committed report already flags the sensitivity ("exact under this
  formatting definition"), so these are answers to two different questions, but nothing records
  that. Someone must decide which definition is canonical. **Nobody has.**

## 6. The open design question

The owner asked whether to collect all substantial work into one controllable place. My answer,
for the next agent to argue with:

**Yes, but derived, not maintained.** This project has built "one authoritative place" six times
(`STATE.md` "single entry point", `coordination/README.md` "operational entry point",
`roster.json` "single authoritative statement", plus CONSTRAINTS, BACKLOG and five handovers).
They now contradict each other on which bot is live, the corpus size, and whether the transport
is clean. A seventh hand-maintained index desyncs within days — the measured rate is 30-plus
desynchronizations in twelve days, every one where two artifacts had to be synced by memory.

The question splits in two:

- **Where the artifacts are — easy.** 18 places currently hold non-`main` work (7 refs + 11
  tags), which is fine. What was *not* fine is that the salvaged e7a rewrite was reachable from
  **no ref at all**. Generalise the protocol's existing "unpushed = unsent" rule from messages to
  work, then build one script that prints the ref/worktree census and **exits non-zero when
  substantial work is reachable from no pushed ref**. That is a guard that can actually fail —
  the class this project systematically lacks — and it would have flagged the e7a rewrite on
  2026-08-06 instead of 2026-08-10. Not built. Small. Recommended first move.
- **Where the findings are — the real problem.** No file was ever lost in the e7a case; the file
  was on `main` throughout. What was uncontrolled was a *re-measurement that changes a closed
  task's headline number*. `CONSTRAINTS.md` is the attempt at this register and it fails
  measurably: an explicit append-only rule requiring `[overturned by Dnnn]` markers, and 1 of 185
  bullets carrying one. A findings register needs two properties prose cannot provide: a
  machine-checkable status, and mechanical rather than remembered supersession. **This is the
  actual protocol design question and it has not been started.**

Guiding principle from the one fix that will not need redoing: I *deleted* the stored tool digest
from `peer-prompt.md` rather than refreshing it, so the check now computes both sides and cannot
go stale. Prefer deleting a document over reconciling it.

## 7. What I verified vs. what I did not

**Verified by execution** (I ran it and read real output): ref/worktree/disk structure; the
transport's per-agent behaviour; the enforcement vacuum (stock LFS hooks, no CI, `main`
unprotected, `lint_outbox.py` reporting "203 files, 0 linted, exit 0"); the document
contradictions quoted with file:line; the failure catalogue at an 8-of-8 sample.

**Structural only**: the 926 messages (counts and schema conformance, not content);
`CONSTRAINTS.md`'s 185 bullets (shape, not substance); `inbox_sweep.py`'s 1,309 lines (I ran it
extensively; a subagent did the line-by-line read).

**Not known at all, and it matters:**

1. **The bot and the game.** I barely looked at 4.8 MB of Rust. I know the score numbers and the
   noise band. Closeable by reading; roughly a day.
2. **How the owner actually operates the agents** — simultaneous or sequential, hand-driven
   sessions or otherwise, who starts them, what a working session looks like. I inferred the
   entire operating model from its exhaust and never asked. **This is the single biggest gap for
   protocol design and it cannot be obtained from the repository.** Ask before designing.
3. **Why agent branches never merged trunk** (894–1519 commits behind — the mechanical root of
   the tool-skew blindness). Hard, discouraged, or never attempted? Changes which fix is right.

**Calibration.** During this work I stated with confidence that
`rust/src/d171a_control_resident_snapshot.rs` was an unreferenced duplicate and implied it was
cleanup material. It is referenced by 15 files. Caught only because I check before deleting.
Separately, my own spot-check script produced two false negatives because `grep -F` cannot match
a quote that wraps across a newline. **Assume that error rate for anything not explicitly marked
as executed.**

## 8. Hazards for whoever continues

- **Do not hand-reconcile the contradictory documents.** That activity is what consumed the last
  twelve days. Delete or consolidate as a protocol decision instead.
- **Do not delete `origin/agent/<id>` canonical refs** (§2).
- **The byte-sacred source has two copies** that must stay byte-identical:
  `rust/src/bin/yamo_orchard_live.rs` and `rust/src/d171a_control_resident_snapshot.rs`. The
  protocol names only the first. `tests/test_resident_source_invariant.py` now covers both.
- **Dates in this repository are fabricated.** No commit exists after 2026-08-10, yet artifacts
  assert events on 2026-08-12 and one docstring cites 2026-08-13. A handover named `2026-08-12`
  was committed on 2026-08-09. Every time-based rule — the 15-minute lease above all, which has
  zero lines implementing it — rests on self-reported clocks. **Verify dates against
  `git log`, never against a filename.**
- **Exit codes die in pipes.** `lint | tail -3 && commit && push` never gates on the lint; a
  pipeline exits with `tail`'s status. This disarmed the publish guard for an entire session, and
  I reproduced it twice by accident during the audit. Check `${PIPESTATUS[0]}`.
- **Verify before deleting, always.** Two of the things I nearly removed as dead weight were
  load-bearing.
