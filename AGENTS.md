# Agent Operating Policy

This repository has a long experiment history. Reading order: `docs/STATE.md` (live state),
then `docs/CONSTRAINTS.md` before proposing any experiment, then the tail of the live ledger
volume named in STATE §5. Use `rg` and `docs/archive/INDEX.md` instead of loading frozen
ledgers unless archaeology is explicitly required.

## Multi-Agent Coordination

- If more than one writing agent is active, the protocol in
  `coordination/multi-agent-protocol.md` is in force. Read it before writing anything.
- One worktree and `agent/<id>` branch per writing agent; never share a worktree. One
  integrator; one arena controller (both `local_claude_1` since the 2026-08-06 owner
  reassignment — `coordination/roster.json` on `origin/main` is the authority, not this line).
- Four artifacts: task records (`coordination/tasks/`), status snapshots
  (`coordination/status/<id>.md`), immutable typed messages
  (`coordination/messages/<sender>/YYYYMMDDTHHMMSSZ-<task-id>-<kind>.md`), and handoffs.
  Each sender owns only its own message directory; acknowledgements are written from the
  acknowledger's namespace, never into someone else's.
- Check your inbox with `python3 scripts/inbox_sweep.py --me <your-id>`; it exits 1 while
  anything addressed to you is unacknowledged.
- A task has a 15-minute concrete-progress lease. Long-running experiments renew it via
  phase markers; a silent multi-hour run is a lease breach even if work is happening.
- Invariants that break other agents' work if violated (protocol §7): keep
  `rust/src/bin/yamo_orchard_live.rs` byte-exact at SHA prefix `fff6669b` (it is
  library-visible as `troll_farm::resident_policy`); never run a formatter across
  `rust/src/bin/` or `cgauto/` because experiment locks record file hashes; never open
  sealed map ranges; do not disturb `data/raw/games/` or the 05:17 collection cron.

## Local Bulk Storage Policy

- Bulk roots are served by whichever backend is mounted at
  `/media/tarstars/medium_data/database/troll_farm`: the USB (ext4 label
  `medium_data`, writable, only while attached) or — the steady state since
  2026-08-11 — a **read-only** GeeseFS mount of `troll-farm-data:archive`.
  The path is observed state; the label or mount source is the identity.
- The archive-backed logical roots are `artifacts`, `outputs`, and
  `data/external`; each must be a symlink resolving beneath the physical
  project root. `yt_work` and `data/generated` are **local scratch** under
  `~/.cache/troll-farm/` and are deliberately outside it.
- Before writing through a bulk root, run
  `python3 cgauto/check_external_storage.py --required-free-gib <GiB>`;
  before a bulk read, `--intent read`. If the backend, project root, free
  space, or any required symlink is unavailable, stop. Never create a
  replacement real directory in the repository, and never loosen the check to
  get past a read-only failure.
- **New bulk output: local disk, then periodic upload** (owner decision
  2026-08-11). `artifacts`, `outputs` and `data/external` are *union roots* —
  real local directories under `~/.cache/troll-farm/bulk/` whose children link
  into the read-only archive, so history reads unchanged and new directories
  are simply created. Refresh with
  `python3 data/scripts/link_archive_roots.py --apply`; upload with
  `data/scripts/upload_archive.py`; replace a local copy with a link only
  after its upload verifies.
- Put large simulation matrices, replay-derived corpora, datasets,
  checkpoints, raw prediction/trajectory dumps, YT payloads and downloads,
  runtime archives, and profiler captures under the external-backed roots.
  Keep source, compact configs, protocols, manifests, checksums, aggregate
  statistics, result summaries, figures, and reports in the repository.
- `data/analysis`, `data/raw`, and `data/processed` are legacy mixed roots.
  Do not replace them wholesale with symlinks because they contain tracked or
  compact records. New bulk artifacts must use the clean roots. Historical
  bulk files may be moved only with copy-before-delete validation and
  path-preserving links as described in `docs/storage-policy.md`.
- Build outputs and virtual environments are reproducible local caches, not
  research archives. They may remain local while useful, but clear stale
  Cargo targets and inactive-worktree environments before allowing them to
  crowd out research data.
- `rust/target` is a disposable cache. At session end, if it exceeds ~10 GB,
  delete `rust/target/debug`; keep `rust/target/release`, whose
  `libtroll_farm.so` serves the Python ctypes tests.

## YT Storage And Compute Policy

- The canonical Troll Farm YT root is exactly
  `//home/delivery_ml/research/tarstars/troll_farm`.
- Treat YT Cypress nodes as scarce. Prefer one large table or archive with
  discriminator columns/manifest metadata over many small tables or files.
- Keep reusable inputs canonical and make runs reference them; do not copy
  datasets or runtimes into every run directory.
- Prefer YT map/sort/reduce for large independent simulation, Monte Carlo,
  corpus-generation, dedupe, and evaluation batches. Prefer GPU jobs for
  training-scale neural workloads only after the frozen workflow passes a
  local/YT parity gate.
- Use the local machine for unit tests, smoke tests, payload assembly, quick
  inspection, and work comfortably below one hour. For a batch expected to
  exceed roughly one hour, evaluate the YT route first.
- Download or summarize required outputs before deleting a reconstructable
  remote run. Keep operation IDs, hashes, row counts, and compact metrics in a
  local report.

## Storage Integrity

- Never delete the only verified copy of an artifact.
- For migration, require matching regular-file counts and apparent bytes plus
  an itemized zero-change `rsync --dry-run --delete` before source removal.
- Preserve repo-relative paths in commands and manifests. Do not rewrite
  historical commands to physical mount paths.
- Do not put secrets, personal tokens, browser profiles, or session state into
  Git or shared artifact storage.
