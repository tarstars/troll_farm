# 20260802-e7a-sector-candidate: exact materialization of the frozen E7a rule

- Status: complete — exact source transform and control/FLIP bridge pass; unqualified for value and Arena
- Record owner / integrator: local_codex_1
- Work owner: chatgpt_1
- Host build service: local_codex_1
- Area: owner-directed materialization of the exploratory E7a sign sector
- Branches: `agent/chatgpt_1-e7a-sector-candidate`, `agent/local_codex_1`
- Created UTC: 2026-08-02T16:35:00Z
- Completed UTC: 2026-08-02T16:49:00Z

## Exact scope

Parent is the strongest repeated mature source,
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

The only transform is `MoisanBot::focus_type`: choose PLUM when the unchanged default is LEMON
and `sum_distance(PLUM) - sum_distance(LEMON) <= 8`; otherwise preserve the default. This is the
frozen exploratory rule selected from the consumed E7 panel. No refit or threshold change is
authorized.

## Result

- candidate:
  `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`;
- bytes: 62,820; SHA-256:
  `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`;
- exact parent/unique anchor/inverse transform: pass;
- frozen census: 13/60 selected, 10/13 positive sign, three non-positive;
- standalone optimized compile: pass with empty stdout/stderr;
- focused construction suite: 4/4 pass;
- exact bridge: four inside-sector roots equal full FLIP and four outside-sector roots equal
  control, both seats, 16/16 full results exact, zero runtime/command faults;
- bridge SHA-256:
  `4353345b3ef37725263e295fc94d7853d02ce20abc3a3ac92babe41c9c347bc7`;
- manifest SHA-256:
  `8ec00737776e1a3125c5e50003712c9493ce429390e5b1d4a077e31e98be0cdb`.

The first literal host build exposed an invalid Rust crate name derived from the requested
`.min.rs` filename. Local added an explicit stable `--crate-name` and changed the compile test to
use a `.min.rs` filename; the exact requested command then passed. This changes build invocation
only, not candidate bytes or the frozen rule.

## Scientific and platform disposition

`MATERIALIZED_EXACT_BRIDGE`, not `QUALIFIED`. The rule was selected from consumed labels, the
primary ridge gate failed, and frozen-rule terminal pricing/fresh prospective value remain
unresolved. The manifest and bridge both set `arena_authorized: false`. No TestSession or Arena
mutation occurred; any owner/controller submission decision is separate and must surface the
unqualified status and current live-bot replacement explicitly.
