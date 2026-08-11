# B4 — collector v2 service (task `20260811-s3-collector-v2`)

- Author: `claude_1`, on the VM
- Date (real UTC): 2026-08-11
- Plan: `docs/superpowers/plans/2026-08-11-s3-phase1-collector-v2.md` Part B, task B4

## Result

**B4 is deployed and has run twice live, end to end.** 62 offline tests green; the B4 mutation
drive catches **14/14, zero survivors** (exit 0); the systemd timer is installed, enabled, and
next fires **2026-08-12 05:47:00 UTC**.

| Live run | Games | Object | Verification | Exit |
|---|---|---|---|---|
| manual, 12:03 UTC | 300 | `games/raw/daily/2026-08-11.jsonl.gz` | byte-identical on re-download | 0 |
| via `systemctl start`, 12:06 UTC | 300 | `games/raw/daily/2026-08-11.rerun-1.jsonl.gz` | byte-identical on re-download | 0 |

The second run is the more interesting one: it hit the plain key, got HTTP 412
`PreconditionFailed`, logged `upload.collision`, escalated to `.rerun-1`, uploaded, verified,
pruned staging and advanced the cursor — **the append-only path proven against the live
endpoint, not just against a stub.** It also proves the hardened unit runs correctly under
`ProtectSystem=strict` / `ProtectHome=read-only`.

## How a run behaves, and why

**Fetch happens on discovery, in the same run.** B1 measured that a replay is anonymously
readable only while a participant's battle window still holds it. A game not fetched today is
not delayed, it is *lost* — so nothing is deferred, and a transient fetch failure returns
**exit 3** rather than looking like a clean day.

**Every upload is conditional (`If-None-Match: *`).** B2 measured that the grant blocks
deletion but not overwriting. Append-only is a property of this code, so a collision escalates
to `.rerun-N` (bounded at 20, after which the run refuses to guess rather than inventing keys).

**The cursor is written atomically** — temp file, fsync, `os.replace`, fsync of the parent
directory — because a torn state file wedges every later run. That is control-plane self-review
finding **F8**, which was exactly this bug in the mirror, and a test crashes the write mid-flight
to prove the old cursor survives intact.

**The cursor is not advanced unless the upload was verified.** Games are recorded as seen only
after the pack has been downloaded again and re-hashed. Otherwise a failed upload would make
those games invisible to every future run — lost twice.

Exit codes are chosen so an incomplete day never reads as a clean one: `0` complete · `1`
unexpected error · `2` upload or verification failed, cursor not advanced · `3` day incomplete
from transient fetch failures. Every path ends with an `exit=N` marker in journald; a run killed
before that line has no marker at all, which is how a truncated run is detected.

## Two operational facts the coordinator should see

**1. The run is capped, and the cap is dropping real games.** The VM's root filesystem is
**94% full — 1.3 GB free**. A day's staging is ~90-107 MB before pruning. So the deployed unit
runs `--cohort 10 --max-games 300`, and both live runs logged
`discover.capped dropped=953` and `dropped=653` against 1,253 candidates. **Those dropped games
are gone unless they are still in a participant's window at the next run.** The cap is logged
every time rather than applied silently, but it is a real shortfall and it is disk, not design,
that sets it. Raise both numbers as soon as there is headroom — or tell me the disk is being
extended and I will raise them now.

**2. Staging is pruned, and only after the bucket copy is verified.** Unpruned, ~100 MB/day on
1.3 GB of free space fills the disk inside a fortnight and takes coordd down with it. Pruning is
gated on a successful download-and-rehash, and three tests pin that staged replays survive a
failed upload or a failed verification — in those cases they are the only copy left. The plan's
"nothing is deleted" rule concerns the corpus and the cold archive; this is the service's own
scratch directory, but say the word and I will keep everything.

## What the mutation drive changed

The first drive caught 10 of 12, and one survivor was a design problem rather than a test gap:

- **C3 (cursor advances after a failed upload) survived because the guard it mutates was
  unreachable.** An upload failure raised out of the `try`, so the guard below never executed —
  it was protection that could not fail, which is the same class of defect this project has been
  burned by repeatedly. Fixed by handling the upload failure explicitly: the run now records
  what went wrong, returns exit 2, and the guard is a live check with a test that reaches it.
- **C7 and C8 were `NOT_APPLIED`** — their patterns no longer matched after edits. The runner
  reports that as exit 3 (incomplete) rather than counting them as caught, which is exactly why
  the exit status describes the experiment and not just the outcome.

Two mutants were added while fixing those (`C3b` upload failure not treated as an error, `C13`
prune before verification). Final: **14 defined, 14 applied, 14 caught, 0 survivors, exit 0.**

## Deployment

```
/etc/systemd/system/collector-v2.service   oneshot, User=tarstars, hardened
/etc/systemd/system/collector-v2.timer     OnCalendar=*-*-* 05:47:00 UTC, Persistent=true
```

Sources committed at `claude_1/collector-v2/deploy/`. 05:47 is offset from `project_host`'s
05:17 cron so the two collectors do not hit the platform together during the parallel-run
window. `Persistent=true` fires one catch-up run after a missed slot, because a skipped day is a
permanent loss rather than a delay.

The service unit deliberately has **no `[Install]` section**: it is timer-activated only, and an
enabled oneshot would also fire at every boot — a second uncontrolled run against the platform.
(It had one briefly during deployment; removed and reloaded before this report.)

## Honest deviations

- **The unit runs from the agent worktree** `/home/tarstars/prj/troll_farm-plan-agent`. If that
  checkout moves or is deleted, the timer breaks — the same pinning pattern coordd uses, but
  worth naming at integration.
- **`--cohort 10` is not the plan's implied full lens.** The frozen wide-lens collector reads
  resident plus the top 50; this reads the top 10. Disk again. It is a parameter, not a design
  choice, and the number lives in one line of the unit file.
- **Two probe/rerun objects now exist for 2026-08-11** — the plain key from the manual run and
  `.rerun-1` from the service run. That is the designed behaviour, not damage: neither
  overwrote the other, and B5's comparison must read both.
- Cursor `seen_game_ids` is bounded at 200,000 ids; a run that trims logs `cursor.trimmed` with
  the count. Nothing has been trimmed yet (600 ids at the time of writing).
- No Arena action, no trunk commit, no write outside `claude_1/`, the bucket's `games/` prefix,
  `~/.local/state/troll-farm/` and the two systemd units — all inside the task's declared write
  set.
