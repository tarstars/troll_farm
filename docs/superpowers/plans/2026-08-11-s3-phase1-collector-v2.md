# S3 Phase 1 + Collector v2 Implementation Plan

Executes Phase 1–2 of `docs/superpowers/specs/2026-08-11-cloud-storage-migration-design.md`
under the owner-approved split (2026-08-11): control-plane and corpus upload run on
`project_host` by the coordinator; the collector-v2 software is implemented on the VM.
**HARD PAUSE: nothing touches the USB cold archive (spec Phase 3). Nothing is deleted
anywhere. The `project_host` 05:17 cron keeps running unchanged throughout.**
**No compute instances are created this grant period.**

Format note: Part B is spec-grade — interfaces, acceptance checks, and decision points are
binding; implementation details are the executor's, because the VM environment has verified
unknowns (Task B1 resolves the largest). This is a deliberate deviation from the full-code
plan format, chosen because the last plan's defects were all baked-in environment
assumptions.

## Part A — coordinator, on project_host (execute immediately)

- [x] A1. Create the bucket in `troll-farm-auto` as `troll-farm-agent`:
      `yc storage bucket create --name <troll-farm-data | fallback troll-farm-data-tarstars>`
      (private ACL, standard class, ru-central1). Record the final name here and in the
      handoff. **Done 2026-08-11: `troll-farm-data`.**
- [x] A2. Create data-plane service account `troll-farm-vm-writer` with **storage.uploader
      + storage.viewer only** (upload + read/list; no delete, no bucket admin — the object
      layout is append-only by design, so overwrite rights are unnecessary). Static access
      keys → `~/.config/yandex-cloud/keys/vm-writer-s3.json` (0600). Also static keys for
      `troll-farm-agent` (admin, stays on project_host) →
      `~/.config/yandex-cloud/keys/agent-s3.json` (0600). Keys never enter git or chat;
      the vm-writer pair travels to the VM via the owner (one paste into claude_1's
      session), landing at `~/.config/troll-farm/s3-keys.json` (0600) there.
      **Done 2026-08-11: both key files in place (0600); vm-writer pair verified present
      on the VM by `claude_1` (0600, never logged).**
- [x] A3. Pack the existing corpus deterministically: `data/scripts/pack_games.py` —
      all `data/raw/games/*.json` sorted by numeric id, chunks of 1,000 →
      `backfill/pack-%06d.jsonl.gz` (gzip; zstd unavailable in the local venv, extension
      names the truth), one line per game `{"game_id", "sha256", "size", "raw"}` with the
      raw JSON embedded; per-pack manifest `manifest/backfill-%06d.jsonl` lines
      `{"game_id", "sha256", "size", "pack"}`. Packing is read-only over `data/raw/games/`.
      **Done 2026-08-11: 16 packs / 15,291 games / 672 MB staged durably at
      `~/.cache/troll-farm/s3-backfill/`.**
- [x] A4. **NETWORK GATE (owner rule 2026-08-11): project_host is sometimes on metered
      mobile internet. Do not start this or any other big upload without the owner
      explicitly confirming the connection is WiFi/unmetered.** Automated detection is
      unreliable (a phone hotspot looks like WiFi to nmcli), so the owner's word is the
      gate. Then: upload packs + manifests to `s3://<bucket>/games/` (boto3 against
      `storage.yandexcloud.net`, admin keys). Verify: object count == pack count; per-pack
      re-download spot-check (≥3 packs, sha256 match); total game count across manifests
      == local count at pack time. Record counts in the handoff.
      **Done 2026-08-11, after the owner's explicit WiFi confirmation: 32 objects
      uploaded; remote 16/16 packs, 16/16 manifests; sha256 spot-checks 3/3 MATCH;
      manifest lines 15,291 == local 15,291; VERIFY: PASS (exit 0). Full log:
      `local_claude_1/verification/s3-backfill-upload-2026-08-11.md` on
      `agent/local_claude_1`.**
- [ ] A5. Owner console errand (bundled with the budget alert): enable billing export
      into `s3://<bucket>/billing/` — console-only, not scriptable here.

## Part B — VM implementation (executor: the owner-designated model under the `claude_1`
protocol identity; task record + v2 handoff; **register and dual-track this task in coordd
per the shadow runbook — this is the first real shadow-mode workload**)

Global constraints: stdlib-preferred Python; `zstandard` or gzip for packing (match Part
A's naming honestly); keys only from `~/.config/troll-farm/s3-keys.json`, never logged,
never committed; no writes outside the VM and the bucket's `games/` prefix; the bucket
layout is **append-only** (uploader rights cannot overwrite — design around it, never
request broader rights); no Arena actions; no trunk commits (work on `agent/claude_1`,
handoff for integration).

- [ ] B1. **Platform-access check (gates everything).** From the VM, exercise the frozen
      collector's read path (`data/scripts/collect_wide.py` imports) against the platform
      for a handful of known public game ids, WITHOUT any session cookie. Deliverable: a
      short report — works cookieless / needs the cookie / needs anything else. If a
      cookie is required, STOP and report; the coordinator will provision it the same way
      as the coordd token before B4 proceeds.
- [ ] B2. S3 client + creds convention: minimal wrapper (boto3 via `uv` if available,
      else stdlib SigV4) reading `~/.config/troll-farm/s3-keys.json`; smoke test:
      list `games/`, put + get + sha256-verify one probe object under
      `games/probe/`, report round-trip. Uploader cannot delete the probe — expected;
      note it and leave the probe.
- [ ] B3. Daily packer, tested: group a day's fetched game files → 
      `games/raw/daily/YYYY-MM-DD.jsonl.gz` (or `.zst` if zstandard installed — extension
      must match content) + manifest `games/manifest/daily-YYYY-MM-DD.jsonl`, same line
      schema as Part A backfill manifests. Tests: pack/manifest round-trip from fixture
      files; determinism (same input → same bytes apart from timestamps — prefer no
      timestamps inside packs).
- [ ] B4. Collector v2 service: fetch new public games (reusing the frozen collector's
      client), stage locally, pack + upload daily, cursor state in
      `~/.local/state/troll-farm/collector-v2.json` (atomic writes — remember mirror
      finding F8), systemd **timer** (daily, offset from 05:17 UTC to avoid platform
      double-load; pick e.g. 05:47 UTC), journald logging with an `exit=N`-style end
      marker (the cron-health guard pattern). No overwrites: a re-run of the same day
      writes `daily-YYYY-MM-DD.rerun-N` objects rather than failing.
- [ ] B5. Comparison tool for the parallel-run window: given a date range, compare game-id
      sets in the bucket's daily manifests vs a `project_host`-exported id list (the
      coordinator supplies it in the task thread); output missing/extra ids. Acceptance:
      run it for the first live day and publish the result in the handoff.
- [ ] B6. Handoff: v2 message with artifact pins (report from B1, code, tests, systemd
      units, first comparison), coordd dual-tracked claim released, and honest deviations
      list. Reviewers: coordinator (cross-review) + `codex_1` (second pair of eyes,
      per the disjoint-findings lesson).

## Cut-over criteria (later, not this plan)

Seven consecutive days where the VM collector's manifests contain every id the
`project_host` cron collected (allowing platform-side timing skew at day boundaries),
zero upload errors, and the owner's nod — then the cron demotes to replica per the spec.
USB cold archive remains untouched until the owner re-attaches the drive and activates
spec Phase 3.
