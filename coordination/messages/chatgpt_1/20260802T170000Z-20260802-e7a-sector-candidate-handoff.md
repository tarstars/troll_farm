---
type: HANDOFF
task_id: 20260802-e7a-sector-candidate
from: chatgpt_1
to: local_codex_1
cc: user, claude_1
created_utc: 2026-08-02T17:00:00Z
requires_ack: true
---

# Handoff: final E7a sector-conditioned candidate

The owner's requested candidate has been produced, host-validated, and integrated.

## Artifact

```text
path:
cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs

bytes:
62,820

SHA-256:
97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595

canonical integration:
fc77657b42a61ca5f18a749178758c66432f4df4
```

Parent is the exact strongest established preseed resident, 62,725 bytes, SHA `a8eb3b2b...`.
The candidate changes only `MoisanBot::focus_type`: choose PLUM where the unchanged choice is
LEMON and `plum_distance_sum - lemon_distance_sum <= 8`; otherwise preserve control.

## Validation

- 4/4 focused construction tests pass;
- standalone Rust compilation passes;
- exact inverse source transformation passes;
- 13/60 frozen sector and 10/13 positive-sign census pass;
- `EXACT_CONTROL_OR_FLIP_BRIDGE` passes on 8 roots × both seats;
- complete results equal original E7 FLIP inside the sector and control outside;
- zero runtime/command faults;
- manifest SHA `8ec00737776e1a3125c5e50003712c9493ce429390e5b1d4a077e31e98be0cdb`;
- bridge SHA `4353345b3ef37725263e295fc94d7853d02ce20abc3a3ac92babe41c9c347bc7`.

## Frozen consumed-panel price

Integrated pricing commit: `61d929c7e0dcd3e6a9ad5bf029429d3d64b60bca`.

```text
C1 - C0: +4.008333 terminal margin
95% root-cluster interval: [-1.587500, +13.101458]

C1 - A1 always-FLIP: +16.181944
95% interval: [+4.729132, +28.668090]

seat 0 / seat 1: +5.791667 / +2.225000
all six family means: positive
own score / opponent score: +0.211111 / -3.797222
```

The rule captures 38.14% of the +10.509722 hindsight ceiling and primarily suppresses opponent
score. It has positive developmental headroom but does not qualify: the rule and labels are
consumed, the broad ridge model failed, and the C1-C0 interval crosses zero.

## Disposition and requested controller action

```text
MATERIALIZED_EXACT_BRIDGE
POSITIVE_CONSUMED_PANEL_HEADROOM
NOT_QUALIFIED
```

Keep the candidate in the submission inventory. Do not submit automatically while another
live cycle is active. Any later publication is a separately serialized controller decision and
must explicitly record that this is an owner-requested exploratory candidate rather than a
frozen-protocol-qualified promotion.

Final human-readable record:
`chatgpt_1/e7a-sector-candidate-final-2026-08-02.md`, commit
`49e5b97c9b5975a35afb6002fe5a2cdc125451bc`.

No TestSession or Arena mutation was performed by ChatGPT.
