# HANDOVER 2026-08-11 — `local_claude_1` session close (context flush)

Everything here is verified state, not intention. Trunk = `main` = `session-2026-07-01`
= both origins at `a8294b1d`. Working tree clean except my untracked
`local_claude_1/inbox-seen.json` (per-agent seen state, normal).

## ★ ONE ACTION IS HELD, DELIBERATELY — the S3 backfill upload

- Staging is READY at **`~/.cache/troll-farm/s3-backfill/`** (durable, moved out of the
  session scratchpad): 16 packs + 16 manifests + `summary.json`; 15,291 games, 672 MB.
  If it ever goes missing, `data/scripts/pack_games.py` re-creates it deterministically
  in minutes (game count will have grown — that is fine, note the new count).
- **HELD by the owner's metered-network rule**: project_host is sometimes on mobile
  internet (at close: hotspot `tass_mobile`). **Do not upload until the owner explicitly
  says the connection is WiFi/unmetered.** Detection cannot be automated — hotspots look
  like WiFi; only the owner's word counts.
- To execute once cleared:
  `.venv/bin/python3 data/scripts/upload_backfill.py --staging ~/.cache/troll-farm/s3-backfill --bucket troll-farm-data`
  (creds default to `~/.config/yandex-cloud/keys/agent-s3.json`). It uploads then
  verifies (counts, ≥3 sha256 spot re-downloads, manifest totals) and prints
  VERIFY: PASS/FAIL. Record the counts in the task thread.

## The session in one paragraph

The coordination redesign is built and half-migrated: control plane `coordd` runs in
shadow mode on the Yandex VM (git still authoritative until P2); all three owner rulings
landed (B7 seals → suite 1670/0 fully green with the USB attached; B9 as-is until cloud
Phase 3; e7a → **pinned rustfmt is the canonical readable format**, `docs/readable-format.md`);
the cloud storage migration is designed, saved, and its Phase 1 is executing under
`docs/superpowers/plans/2026-08-11-s3-phase1-collector-v2.md` — Part A done except the
held upload, Part B assigned to `claude_1` on the VM.

## Cloud facts (also in agent memory `yandex-cloud-setup`)

- `yc` CLI installed; profiles: `default` (owner OAuth) and `troll-farm-agent` (active,
  SA-scoped to folder `troll-farm-auto` `b1gdtsgj3op76133urr0`).
- Bucket **`troll-farm-data`** (private, 50 GB cap). Data-plane SA
  `troll-farm-vm-writer` = storage.uploader + storage.viewer ONLY (append-only by
  construction). Keys: project_host `~/.config/yandex-cloud/keys/{agent-s3,vm-writer-s3}.json`;
  VM copy at `~/.config/troll-farm/s3-keys.json` (0600, placed via SSH, verified).
- **SSH alias `troll-vm`** (tarstars@51.250.37.145, key `~/.ssh/experiment-cloud`).
  VM clones live under `~/prj/` there.
- Grant 18,000 ₽/mo; ~15,000 already consumed this period → **no compute creation this
  period**; steady headroom ~10,500 ₽/mo. Quotas: GPU all zero; 28 free vCPU.
- Owner console errands still open: budget alert at 17,000 ₽; billing export into
  `troll-farm-data/billing/`.

## Waiting on

1. **`claude_1` on the VM**: task `20260811-s3-collector-v2` (plan Part B, B1–B6).
   Handoff + keys-preplaced progress both published and verified visible in its sweep
   VM-side. B1 (cookieless platform-read check) gates everything; if a cookie is needed,
   provision like the coordd token. Reviewers on its handoff: coordinator + `codex_1`.
   It must dual-track the task in coordd (first real shadow-mode workload).
2. **Shadow-mode evidence** per `coordination/coordd-shadow-runbook.md` (deployed and
   healthy on the VM since 2026-08-11 morning; weekly comparisons; exit criteria → write
   the P2 plan, which must own the twelve carried defects listed in the runbook's
   "Known items", including self-review F1–F8 — F1/F5 coordinator-reproduced).
3. **Owner**: the WiFi word for the upload; console errands; G6 go-ahead someday;
   cloud-spec Phase 3 (USB cold archive) when the drive is re-attached — hard-paused.

## Hazards for whoever continues

- Metered-network gate above — it is in plan A4, agent memory, and here.
- Exit codes die in pipes (`sweep | grep` ate an exit this very session — run guards
  bare, check `$?`).
- Dates: trust `git log`, never filenames (fabricated-clock history in this repo).
- Byte-sacred `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`); no formatters over
  hash-locked sources — the canonical READABLE format (pinned rustfmt) applies to
  derived copies only.
- Without the USB attached, ~20 frozen-analysis tests fail via dangling symlinks —
  environmental, not regression; full-suite baseline with USB = 1670 passed / 0 failed.
- The old coordination protocol is STILL authoritative (shadow mode observes only);
  publish messages with the lint, unpiped.

## Fast resume ritual

```bash
cd /home/tarstars/prj/troll_farm && git fetch origin
python3 scripts/inbox_sweep.py --me local_claude_1 --fetch   # expect exit 1, errors 0
.venv/bin/python3 scripts/coordctl.py doctor --repo .        # cron may be red if machine slept
ssh troll-vm 'systemctl is-active coordd'                    # expect: active
```
Then read: this file → the runbook's Known items → the S3 plan checklist.
