# 20260730-e2-banking-route-efficiency

- Status: result ready — `ROUTE_RESIDUAL_OBSERVED`; peer review pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER E2 / execution-class diagnostic
- Base commit: 7bee1050d5f1aa95d893219810ba02016cf023cd
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T21:35:32Z
- Last updated UTC: 2026-07-30T21:51:52Z

## Outcome

Determine whether the exact live resident wastes carrying time through a suboptimal home-door
choice, changes home-door targets during one bank return, or chooses an equally fast inbound
door that lengthens its observed next outbound leg. Separate this from the already-clean
movement/stall audit and D171's non-bank target oscillation diagnosis.

## Frozen audit questions

1. Does every emitted carrying return choose a minimum immediate inbound ETA among reachable
   home doors, subject to the resident's own occupied-door and two-worker compatibility rules?
2. Does a unit change its emitted home-door target before depositing the same cargo?
3. Relative to the observed first post-deposit productive target, how often does the chosen
   deposit door have avoidable hindsight round-trip distance or ETA?
4. How many side-games and cargo units are exposed, and what is the strict opportunity ceiling
   in avoidable movement turns? Do not translate this diagnostic into rating points.

Outcomes:

- `NO_ROUTE_RESIDUAL` if immediate choice is optimal, targets persist, and hindsight regret is
  zero;
- `ROUTE_RESIDUAL_OBSERVED` if a reproducible nonzero mechanism exists, with frequency and
  ceiling reported but no candidate implied;
- `UNIDENTIFIABLE` if emitted commands cannot distinguish banking from another resident action
  or cannot bind a post-deposit target.

## Exclusive write set

- this task record;
- `coordination/messages/local_codex_1/*-20260730-e2-banking-route-*.md`;
- `coordination/status/local_codex_1.md`;
- `cgauto/e2_banking_route_audit.py` (new);
- `tests/test_e2_banking_route_audit.py` (new);
- `data/analysis/live-agent-6553250/e2-banking-route-efficiency-result-2026-07-30.{md,json}`
  (new);
- `local_codex_1/e2-banking-route-efficiency/` (new, compact);
- `outputs/local_codex_1/e2-banking-route-efficiency/e2-episode-details-0-199.json`
  (new external-backed machine detail);
- canonical approach register/BACKLOG/CONSTRAINTS/STATE/ledger only at closeout.

## Shared read-only paths

- Exact live source and current resident artifact.
- `cgauto/motion_audit_study.py`, simulator engine/map generator, and focused prior motion,
  D171, postmortem, and design records.
- Reused local diagnostic seeds `0..199`; no fresh, sealed, or confirmation range.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`, any submission/source artifact, historical analyzer or
  result, raw games, sealed/confirmation ranges, cron, TestSession, or Arena.
- Peer-owned N4/evidence-index paths.
- No formatter, source materialization, platform access, or raw trajectory dump. Episode
  detail may be written only through the verified external-backed `outputs/` root.

## Acceptance

- Exact-live artifact hash and seed/seat coverage are recorded.
- The tracked JSON is compact; full episode detail has an external path, byte count, and hash.
- Classification requires carrying cargo and a home-door MOVE/DROP; ambiguous actions are
  counted, not silently assigned.
- Immediate inbound, target persistence, and hindsight outbound quantities are reported
  separately.
- Tests cover door classification, multi-door ties, target changes, deposit binding, and an
  unidentifiable episode.
- One diagnostic verdict; any experiment remains a separate frozen protocol with the
  register's ≥+1.0 bar.

## Arena authority

No platform access or mutation.

## Result

- Immediate return selection is clean: 4,855/4,855 identifiable checks have zero ETA
  regret; 64/64 simultaneous-carrier assignments are optimal; zero confirmed returns
  change door.
- A hindsight-tied alternate door is one movement turn nearer the later observed task in
  134/10,597 bound episodes: 134 total = 0.335/side-game, max one, all wood, seat 67/67.
- Verdict: `ROUTE_RESIDUAL_OBSERVED — NOT_EXPERIMENT_JUSTIFIED`. The future-conditioned
  static ceiling is not causal terminal value or rating and does not open source work.
- Canonical report:
  `data/analysis/live-agent-6553250/e2-banking-route-efficiency-result-2026-07-30.md`.
- Compact result, external detail, hashes, and validation:
  `local_codex_1/e2-banking-route-efficiency/manifest.json`.
