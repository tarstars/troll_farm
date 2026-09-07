# Autonomous goal: top-seven Troll Farm bot

This file records the proposed goal. Writing it does not activate the goal; the
owner will set it separately.

Act autonomously until this Troll Farm bot reaches **7th place or better in the
highest platform division**, with a completed rollout and a confirming observation
as defined in `EVALUATION.md`.

Completion requires the exact submitted agent to meet that rank with 160 distinct
completed games, 100% cached and uncached rollout progress, no pending games, and
qualifying observations at least five minutes apart. Local results or a temporary
ladder placement do not count as completion.

Use `claude-proxy` for implementation, debugging, testing, and analysis. Keep
Astra's role to brief direction, focused verification, and consequential decisions.
Target at most 2,000 Astra tokens per routine checkpoint; this is an operating
target, not an enforced billing cap. Avoid repeated historical reviews.

You may modify this project, run experiments, evaluate candidates on the platform,
and publish supported improvements without asking the owner each time. Keep the
neighboring `/home/tarstars/prj/troll_farm` project read-only. Preserve the best
verified bot and existing work. Follow `AGENTS.md` for working storage.

Follow `WORKFLOW.md` and `EVALUATION.md`. Prefer runnable candidates and competitive
measurements over additional audit infrastructure. After each bounded batch,
independently assess the result and start the next useful batch. Once activated,
this goal provides standing authorization for successive in-scope batches; routine
batch boundaries do not require renewed approval.

Continue without routine approval requests. Stop when the goal is verified or
progress requires the owner's decision, unavailable access, or additional spending
authorization. Do not purchase services or change authentication. Keep updates short
and maintain a compact resumable checkpoint in `WORKSTATE.md`.
