# 20260801-h10b-search-teacher-distillation-record

- Status: claimed — documentation only
- Record owner: local_codex_1
- Work owner: local_codex_1
- Integrator: local_codex_1
- Area: H10b whole-policy learning programme
- Base commit: 278c7041cdae933fe06f28766129a68a4c779ab6
- Branch: agent/local_codex_1
- Created UTC: 2026-08-01T19:47:00Z

## Outcome

Record the owner's proposed AlphaZero-style training route as a distinct programme concept:
an expensive offline search teacher generates dense policy/value targets on states visited
by the compact student, while the Arena artifact runs the distilled network without search.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `docs/APPROACH-REGISTER-2026-07-30.md`;
- `docs/BACKLOG.md`.

## Acceptance

- Separate H10b-r1 from H10a option scoring, L1 replay imitation, D170 sparse terminal-reward
  learning, and S3 online rollout search.
- Record population-conditioned training, closed-loop student-state relabelling, compact int8
  deployment, and bounded feasibility gates.
- Do not imply that a charter, map range, fit, bulk job, candidate, or Arena action is authorized.

## Prohibitions

Documentation only. No data/replay/map/range read, bulk write, source/model/training change,
simulation, panel, candidate, TestSession, submission, or Arena action.
