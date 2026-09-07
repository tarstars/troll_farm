# Current Claude entry point

You are the primary implementer for this project's owner. Read `AGENTS.md`,
`WORKFLOW.md`, `WORKSTATE.md`, then your assigned task. Read relevant sections of
`EVALUATION.md` before designing comparisons or platform actions. Do not read the
historical README ledger or old research queue wholesale.

Goal: a significant Troll Farm bot improvement reaching verified rank <=7 in the
highest platform division. Last verified live baseline: V439, rank 28; not achieved.
Publication is owner-authorized, but ordinary delegated tasks are offline: the
primary reviewer coordinates external tests and publication unless your ticket
explicitly assigns them. Never infer publication authority from an old task file.

Implement, test, measure, and return a compact evidence-backed handoff. Follow the
ticket's time/experiment budget. Do not expand into an audit programme, spawn more
agents, or commit/push unless the ticket explicitly requests it. Preserve existing
dirty files; only edit assigned files. Prefer isolated candidate modules/builders;
leave `bot.rs` and `submission.rs` unchanged until a reviewed promotion.

Work only here and in `/data/separate_troll_farm-working/`. The neighbor
`/home/tarstars/prj/troll_farm` is read-only, including its working storage/queues.
Use `TMPDIR=/data/separate_troll_farm-working/tmp`. Use `apply_patch` for file edits.
Never expose credentials or change account/model/authentication configuration.

The historical charter is preserved in `docs/CLAUDE-HISTORICAL-2026-09-02.md` for
reproducibility, not instructions. V468, the +40 own-score gate, top-ten target,
old no-publication rule, and old queue order do not govern current work.
