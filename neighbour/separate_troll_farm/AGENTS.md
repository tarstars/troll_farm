# Project working storage

- Store new temporary files, compiled test programs, replay downloads, and large analysis output under `/data/separate_troll_farm-working/`.
- Use `/data/separate_troll_farm-working/tmp/` as `TMPDIR` when running tools that create temporary files.
- Keep `/tmp` for small system-managed files only; do not accumulate project experiments there.
- Archive useful temporary results before cleanup instead of deleting them immediately.
- While a platform candidate is stabilizing, keep doing useful offline analysis rather than only waiting.

# Claude-led workflow

- The owner requests minimal primary-model token use and delegation through the
  installed `/home/tarstars/bin/claude-proxy`. Follow `WORKFLOW.md`.
- Start from the short `WORKSTATE.md`, not the complete historical ledger. Claude
  owns bounded implementation/testing batches; the primary agent reviews evidence
  and coordinates publication. Preserve existing work and use one writer at a time.
- `EVALUATION.md` is the current evaluation authority. The old Claude charter is
  archived in `docs/CLAUDE-HISTORICAL-2026-09-02.md`, not active instructions.
