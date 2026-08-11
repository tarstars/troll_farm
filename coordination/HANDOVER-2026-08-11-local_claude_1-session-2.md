# HANDOVER 2026-08-11 (second session) — `local_claude_1`, context-flush safe

Verified state, not intention. Supersedes `HANDOVER-2026-08-11-local_claude_1-session-close.md`
for everything it covers; that file's "★ ONE ACTION IS HELD" section is **discharged**.
Trunk = `main` = `session-2026-07-01` = `6f20feaa`, both origins. Agent branch
`agent/local_claude_1` = `1b0a3f5c`-or-later, clean. Only untracked path on trunk is
`local_claude_1/inbox-seen.json` (per-checkout state, normal — see the wart in §6).

## 1. The held upload is done, and so is Phase 3

The owner confirmed WiFi, which discharged the metered-network gate for both uploads below.
**The rule still governs any future big upload** — hotspots look like WiFi; only the owner's
word counts.

**Backfill (plan A4).** 32 objects; remote 16/16 packs + 16/16 manifests; 3/3 sha256 spot
re-downloads; manifest lines 15,291 == local. `VERIFY: PASS`, exit 0. Record
`local_claude_1/verification/s3-backfill-upload-2026-08-11.md`. Plan A1–A4 ticked.

**Cold archive (spec Phase 3, owner-activated out of order because it is the one phase that
needs the USB attached).** All **3,483 files / 9.99 GiB** from
`/media/tarstars/medium_data/database/troll_farm` are at `s3://troll-farm-data/archive/<path>`.
`VERIFY: PASS` — head-check 3,483/3,483 on size+sha256, six full re-downloads including the
728.5 MiB object (multipart reassembly covered), both count checks equal — plus an
**independent** post-hoc walk of the USB agreeing exactly: 3,483 files / 10,723,508,326 bytes.
Tool `data/scripts/upload_archive.py`; record
`local_claude_1/verification/s3-archive-phase3-2026-08-11.md`.

Bucket now: `archive/` 3,483 objects 9.99 GiB, `archive-manifest/` 7, `games/` 40 objects
0.68 GiB — 10.67 GiB against a 50 GiB cap.

### The USB question, answered precisely

**Unplugging `medium_data` now loses no data.** It does *not* yet make the drive redundant:
2,346 repo symlinks address those files by **absolute** path, so detaching still dangles them
and fails ~20 frozen-analysis seal tests, and `cgauto/check_external_storage.py` fails closed
on bulk writes (the good failure). That is spec **Phase 4**, not started:
- `geesefs` **0.35.0 is packaged in the Yandex apt repo** (`common.dist.yandex.ru`).
- The mount must land on `/media/tarstars/medium_data` for absolute symlinks to resolve;
  that directory is root-owned and created by udisks2 on attach → **needs sudo, cleanest with
  the drive detached**.
- Cost watch: frozen trees are COLD class; if seal tests read them through the mount on every
  run, measure retrieval charges before that becomes routine.

Design decisions locked in, so a successor does not "optimise" them away: **per-file objects,
not packs** (packing would make Phase 4 impossible), and **manifests outside `archive/`** so
the prefix stays a pure mirror.

## 2. ★ My own published error, and the correction — read before repeating it

I turned `claude_1`'s honest `dropped=953` throughput figure into "~950 real games
permanently lost per run", ruled it urgent to the owner and to `claude_1`, and **it was
false**. Measured afterwards:

- of the VM's **600** games collected 2026-08-11, **0** were new to the project (338 were
  first collected by the `project_host` cron on 27–28 July);
- of **2,488** games visible in participant windows at the time of measuring, **1** was not
  already held (top-10 cohort: 1,136 visible, same 1 missing).

The cap was dropping **redundant re-fetches**. Correction published as
`coordination/messages/local_claude_1/20260811T142500Z-20260811-s3-collector-v2-correction.md`
(supersedes my policy message in full); evidence
`local_claude_1/verification/collector-v2-marginal-coverage-2026-08-11.md`.
`claude_1` acknowledged it as governing and noted it corrects its own framing too.

**Lesson for the successor: measure before ruling, and never layer an inference on a peer's
measurement and publish it as fact.** B1's retention finding is sound — unfetched games do
expire — but that does not make *dropped candidates* new-and-lost.

## 3. Live threads

1. **`claude_1` → `20260811-collector-v2-dedupe`** — assigned, **claimed in coordd generation 1
   at 14:54:58Z (verified by execution, not by its word)**. Record
   `coordination/tasks/20260811-collector-v2-dedupe.md`, handoff
   `.../20260811T144908Z-20260811-collector-v2-dedupe-handoff.md`. Binding design: build the
   known-id set from `games/manifest/{backfill,daily}-*.jsonl` **every run, never cached**
   (stale cache under-fetches silently); subtract **before** fetching; **fail loud** if the set
   cannot be built (an empty known-set silently re-fetches everything); **oldest-first** among
   un-held (games leave the window from the far end); zero-new is `exit=0 fetched=0` with **no
   empty pack**. Deliberately **not** deduping against `project_host`'s corpus — a game the
   notebook holds but S3 lacks *should* be fetched; that is the migration working, and it keeps
   the task independent of me.
2. **`20260811-s3-collector-v2` stays in `review`** — B1–B4 complete and **deployed**; timer
   `collector-v2.timer` **active, next fire Wed 2026-08-12 05:47:00 UTC**; last run
   `end exit=0 seconds=145.2`, `seen_total=600`. Reviewers: me + `codex_1` (acked 12:10Z,
   verdict correctly withheld). **B5 parity is unblocked** — I supplied
   `local_claude_1/exports/project-host-game-ids-2026-08-11.txt` (361 ids) with a README.
3. **Shadow mode** — coordd active on the VM, tunnel now persistent on `project_host`
   (see §5). Exit criteria and P2 carries unchanged, plus three new carries in §6.

## 4. Decisions and corrections that landed on trunk

- **`append-only` was never enforced by permissions.** `claude_1` measured: DELETE refused
  (403), plain PUT to a live key **succeeds**. Enforced now in code by `If-None-Match: *`
  with a loud `PreconditionFailed`. Plan text corrected at `02752aa3` — the false claim is no
  longer readable as fact anywhere.
- **B9 DECIDED: defer untracking** the 325 tracked files under gitignored `data/raw/`
  (ignore rule is `data/.gitignore:1:raw/`; tracked files override it). Precondition "S3 is
  canonical for raw dumps" is unmet until Phase 2 cut-over. **New finding that de-risks it:
  no test reads those paths** — the only `tests/` mention is a docstring in
  `test_waste_sweep.py` saying it does *not* touch the corpus. Trigger: Phase 2 cut-over.
- **Rulings to `claude_1` that stand**: conditional uploads affirmed; staging pruned only
  after the uploaded pack is re-downloaded and re-hashed (between fetch and verified upload
  the staged file is often the only copy in existence); tests relocate under `tests/` at
  integration **but must run unconditionally and fail rather than skip**.

## 5. Infrastructure changed this session

- **coordd tunnel is now a persistent user unit** on `project_host` — it had never been
  installed (last session's was ad-hoc). `~/.config/systemd/user/coordd-tunnel.service` →
  `troll-vm`, token at `~/.coordd/token` (0600), `127.0.0.1:7077/health` ok, `doctor` green.
  First full mirror pushed 924 messages; subsequent mirrors incremental.
- Nothing was deleted anywhere. The USB staging at `~/.cache/troll-farm/s3-backfill/` is
  retained.

## 6. Hazards and warts for whoever continues

- **Metered network** — unchanged, still binding for future uploads.
- **Yandex echoes object metadata title-cased (`Sha256`)**, unlike AWS's lowercase. A
  lowercase lookup silently defeats head-and-skip resume; my smoke test on the two smallest
  trees caught it before the 10 GiB run. Smoke-test uploaders on the smallest input first.
- **`inbox_sweep` seen-state is per-checkout and untracked**, so trunk and the agent worktree
  keep divergent inboxes (observed 7 unseen vs 0). The **ack-required list was byte-identical
  in both**, so obligations are never at risk — only novelty. Now a P2 carry.
- **coordd `register_handoff` cannot distinguish a failed fetch from a missing commit** on the
  VM deploy (`/var/lib/coordd/repo.git` has an unreachable GitHub origin). `claude_1` had to
  hand-deliver commits by bundle. P2 carry.
- Exit codes die in pipes — run guards bare and check `$?`. Dates: trust `git log`, never
  filenames. Byte-sacred `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`, verified this
  session). Old coordination protocol is still authoritative; publish through
  `lint_outbox.py`, unpiped, from the agent worktree.

## 7. Debts and the owner's queue

**My debt, stated plainly and repeatedly to the team**: I have read all of `claude_1`'s
reports end to end and have **not** audited its collector-v2 code line by line. My rulings
are design rulings, not a code-review verdict. `20260811-s3-collector-v2` must not be closed
on my say-so alone.

**Owner queue**: budget alert at 17,000 ₽ and billing export into `troll-farm-data/billing/`
(both console-only); G6 go-ahead; **Phase 4 activation** (needs sudo; the drive can be
detached first). Grant period still nearly spent → **no compute creation**.

**Open question I did not rule on, deliberately**: today's id sets were VM 600 / cron 361 with
an overlap of **9** — near-disjoint cohorts (VM `--cohort 10` vs frozen resident + top 50). The
spec's cut-over criterion ("the VM's manifests contain every id the cron collected") therefore
currently measures cohort choice rather than collector correctness, and retiring the cron while
the VM stays at `--cohort 10` would cost roughly **350 games/day** of coverage. Belongs in the
Phase 2 cut-over discussion.

## 8. Fast resume ritual

```bash
cd /home/tarstars/prj/troll_farm && git fetch origin
python3 scripts/inbox_sweep.py --me local_claude_1 --fetch   # expect exit 1, errors 0
.venv/bin/python3 scripts/coordctl.py doctor --repo .        # expect coordd reachable
ssh troll-vm 'systemctl is-active coordd; systemctl is-active collector-v2.timer'
```
Then read: this file → §2 (the correction) → `coordination/tasks/20260811-collector-v2-dedupe.md`
→ the runbook's "Known items".
