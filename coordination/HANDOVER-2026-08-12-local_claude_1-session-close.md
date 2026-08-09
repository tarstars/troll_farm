# Session-close handover — `local_claude_1`, 2026-08-12

Written on owner instruction: *"write down all important things in a context-flush safe way."*
This **supersedes** `HANDOVER-2026-08-12-local_claude_1.md` for everything it covers; that file
remains valid for roster, programmes, hazards and my error record, and I amended its two false
claims in place.

Conflict order: newest pushed correction → `docs/STATE.md` → the governing task record →
`docs/CONSTRAINTS.md` → these handovers.

**Repo state at close: `main` = `session-2026-07-01` = `agent/local_claude_1`, all pushed.**

---

## 0. The one thing that cannot wait

**An Arena run is in flight.** `readable__no_orchard` is live and maturing. Nothing else may be
submitted until it settles.

```text
agent 6604529 / submission 41113243
source  cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs
sha256  98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29
last read  21 games · 18.63 · rank 83/139 · identity_clean=True · signals=0
```

**Purpose:** a *second* mature observation. Its prior single run scored 24.76/rank 21 — our
highest ever — but the registry itself raises `SINGLE_MATURE_RUN`, and a related no-orchard
source scored 23.27. A 1.5-point spread is wider than the ±0.5–1 noise band, so its true level
is unknown. This run settles it.

**Next action:** terminal submission-scoped checkpoint at ~160 games, compared against 24.76.

```bash
cd /home/tarstars/prj/troll_farm
.venv/bin/python cgauto/arena_transfer_checkpoint.py --agent-id 6604529 \
  --submission-id 41113243 --role candidate-terminal \
  --output data/analysis/live-agent-6553250/readable-no-orchard-rerun-20260812/terminal.json
```

**Interpretation, fixed in advance so it cannot be rationalised after the fact:**

- within ~±0.5 of 24.76 → level corroborated; it becomes our best-evidenced bot
- near 23.3 → 24.76 was a favourable draw; correct the register, stop calling it our ceiling
- otherwise → two observations 1.5 apart establish **variance, not a level**; say so plainly

**Do not restore on a weak score.** Restore only on unambiguous source/identity/runtime failure.
Cold reads sit far below matured ones — 18.63 at 21 games is normal and carries no information.
The keep/restore decision after a clean mature read is the **owner's**, not the agent's.

**Restore target (NOT the one in the promotion runbook):**

```text
cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs
sha256 2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381
agent 6594200 / submission 41090606
```

⚠ **`docs/PROMOTION-RUNBOOK.md` does not govern this run and must not be followed.** Its
authorization gate binds it to candidate D171a only, and its §1 identities are stale: it names
resident `a8eb3b2b…` / agent `6561795`, not live for weeks. **Its abort path would restore the
wrong bot.** I recorded this in the task file; it is the single most dangerous stale document in
the repo right now.

Records: `coordination/tasks/20260812-readable-no-orchard-rerun-arena.md` (full execution log,
one row per action) and `data/analysis/live-agent-6553250/readable-no-orchard-rerun-20260812/`.

---

## 1. What closed this session

**The gate is integrated.** `main:claude_1/pipeline/fuzz_panel.py` is `d8900abf31dd030d…` with 33
TRAIN references; it had 0 before. Nine branches merged, `abgate-selfplay-gate` deliberately
unmerged per invariant 4. All four hash-locked sources verified after merge (`fff6669b…`,
`2caac7c6…`, `98628e98…`, `a8eb3b2b…`), zero changes under `rust/`/`sim/`/`cgauto/`, one
agent-authored CI file stripped.

**B1 closed by execution.** I ran the r4 §8 packet in a second checkout: 163 + 24 tests OK,
16/16 mutations caught, floor **BLOCK 118/240** and candidate **BLOCK 121/240**, both with zero
`GATE_UNREADY`. Two checks beyond the packet: deterministic across two runs, and both my packets
**row-identical** to the committed `evidence-r4` packets — stronger than matching the total,
since two runs can agree on 118 while disagreeing about which games block. Record:
`local_claude_1/verification/train-r4-independent-execution-review-2026-08-12.md`.

**`118/240` is now citable — with r4 §9's restriction attached:** TRAIN is witnessed in only 2
games and **10 of 17 repaired rules have no corpus witness**. The floor is not evidence for
those; they are pinned by unit tests, the differential and the mutation drive. `claude_1`
disclosed this itself and disclosed it accurately.

**Transport is clean for the first time in this programme.**

```text
delivery errors 0 · quarantine errors 0 · quarantined 9 · immutable-path collisions 0
```

Three further blobs quarantined (`47aae1a6…`, `69e9a66c…`, `ffe97634…`), each verified to have a
valid replacement, so no content was lost. Hold released because both peers had by then attacked
the mechanism.

**Six unread reviews read.** M3a correct-subject `REVISION_REQUIRED` (replay not portable); M3a
golden bundle v2 claims **green** — *unverified, and my last second-checkout run of v1 failed 2
of 10 tests, so execute before believing it*; fast-verification-executor requirements; M2 rev 2
`ADVERSARIAL_ACCEPTED`; I-30 rev 3 core accepted, `REVISION_REQUIRED` at the trust root;
bite-test r2 historical accepted, current revision required.

---

## 2. Findings that peers owe answers on

- **`chatgpt_1`'s published tool digests reconcile with nothing.** Both SHA-256 values in its
  `20260811T232000Z` blocker match **no blob in the entire history** of either file — I
  enumerated all 13 versions of `inbox_sweep.py` and all 3 of `lint_outbox.py`. Decisively, the
  blob `db4adb7e…` it cites *in the same message* hashes to `0f78bf38…`, not the `5a199bb4…` it
  claims. **Its blob ids were all correct**, which is why I granted the adjudication in full.
  The pattern: committed-blob analysis reliable, execution-derived claims not. I alleged no
  cause; I asked it to re-publish or say the run is unre-derivable.
- **`scripts/lint_outbox.py` is ABSENT from `agent/claude_1`.** Not stale — missing. It has been
  publishing without the tool that catches exactly the defects that put its messages in
  quarantine. That reframes those errors as a tooling gap, not carelessness. Its
  `inbox_sweep.py` is also still `12b27e9c…` against current `0f78bf38…`.
- **`chatgpt_2`** still owes its tool digest (content SHA-256, **not** Git blob id).

---

## 3. Corrections to my own record — read these before trusting my figures

Three more this session, all the same shape as the nine before: **a number adjacent to the right
one, quoted instead of measured.**

1. **Integration size.** I wrote that `claude_1`'s branch diverged by "2,104 files, +193,920 /
   −729,616". Measured: **251 files, +231,176 / −127**, touching only `claude_1/` and
   `coordination/`. The job was far smaller and safer than I had advertised.
2. **Live standing.** I quoted 22.81 / rank 32 / 137 as current. It was the *settled checkpoint*;
   current standing at submission time was **22.7 / rank 35 / 139**. The slot we gave up was
   already eroding.
3. **My own quarantine authorization.** I published an adjudication with no `quarantines` array —
   violating the TQ-2 rule I wrote myself after `chatgpt_1` found that hole. The mechanism
   rejected me and **failed closed** (`quarantined 0`, not partial). Repaired by a superseding
   message, not an edit; messages are immutable.

**Two tools stopped me before a peer had to** — the outbox lint rejected a handoff citing an
unpushed artifact commit (the identical defect to one of the messages I was quarantining), and
TQ-2 rejected the adjudication above. That is the trend worth keeping: errors caught by tools
and by me pre-publication, rather than by peers after.

---

## 4. Standing operating rules (unchanged, and they earned their keep today)

- **A reply is evidence of nothing.** Agents publish the *content* SHA-256 of tools they run.
- **Dual-format every message** — v2 front matter **and** a legacy `- To:` block.
- **Always `lint_outbox.py --staged` before publishing, and never pipe it** — a pipe discards the
  exit code.
- **A correction does NOT clear a delivery error.** Quarantine is the only repair.
- **Messages are immutable.** Repair a bad message with another message, never an edit.
- **Commit before any git history operation.**
- **Two independent reviews before adopting any conclusion.**
- Never `git add -A`/`-u` with concurrent agents — stage exact paths.
- Never run a formatter over `rust/src/bin/` or `cgauto/`.
- Sealed: maps 9,844,200–215, the official holdout, 11 D164 games, 9,852,000–063, 9,857,000–127.
  Do not disturb `data/raw/games/` or the 05:17 cron.

Start ritual:

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1
python3 scripts/inbox_sweep.py --me local_claude_1 --fetch    # exit 1 = healthy (unacked only)
sha256sum rust/src/bin/yamo_orchard_live.rs                   # MUST start fff6669b
```

Exit **2** means errors; exit **1** means merely unacked messages. Current tool digests on
`main`: `inbox_sweep.py` `0f78bf38…`, `lint_outbox.py` `f3c47b70…`.

---

## 5. Next actions, ordered

1. **Terminal checkpoint on `41113243`** when it matures (§0). Nothing else is in flight.
2. **Rebuild M3a on the correct subject → replicate the idle-blocker finding → M3b.** M3b remains
   the most valuable unattempted item and the only work that asks whether a decision was
   *correct* rather than whether it *oscillated*. The idle-blocker finding is **still
   unreplicated** — it came from a library built on a different bot (`a8eb3b2b`).
3. **Verify `chatgpt_1`'s golden-bundle-v2 "green" claim by execution** before adopting it.
4. Peer answers owed (§2).
5. **Owner call pending:** five absorbed task branches meet the runbook's deletion criteria. I did
   not delete them — outward-facing, and adjacent to the open `agent/*` branch-protection
   question.

**Owner decisions still outstanding:** GitHub branch protection on `agent/*` (last unresolved
*critical* security finding — one push could nullify the quarantine irreparably); scope for
`chatgpt_2`; which banana route, if any (CBF is the only one standing, parked, unstarted).

---

## 6. The honest headline

**The competition score has not moved: the bot that was live scored 22.81 and had drifted to
22.7 / rank 35.** Everything from 2026-08-05 to today went into repairing and then verifying the
equipment used to judge changes, because that equipment was returning meaningless answers. That
was the right call and it is now finished — the gate is repaired, integrated, and independently
executed; the transport is clean.

**Today is the first day since then that an action was taken which can actually change the
number**, and it is `41113243`. It is a measurement, not a promotion: it tells us whether our
best-measured bot is genuinely 24.76 or whether we have been quoting a lucky draw.
