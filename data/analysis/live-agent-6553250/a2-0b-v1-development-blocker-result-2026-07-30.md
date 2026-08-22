# A2-0b v1 development result — BLOCKED before implementation lock

The frozen v1 protocol stopped correctly at its 16-map development smoke. No
implementation lock or confirmation panel was run.

Across 256 tasks (16 consumed D173b calibration maps × two seats × eight families), the
zero-error G3 premise failed:

| mode | issues | MOVE_BLOCKED | other noncritical |
|---|---:|---:|---:|
| legacy states, referee checker | 10,782 | 10,013 | 769 |
| referee path | 10,132 | 9,584 | 548 |

The remaining reasons were `no_capacity`, `nothing_to_drop`,
`opponent_plant_blocking`, `pick_stock_lost`, `train_affordability_lost`, and
`train_shack_blocked`. These are all explicit noncritical referee paths. Treating their
mere existence as a parity failure was a protocol-design error: source-faithful execution
must model them, not require deterministic standing controllers never to emit them.

This is not permission to ignore legality. The successor must require zero critical or
unsupported errors, retain reason counts and examples, and test that every supported
noncritical failure changes state exactly as the referee specifies. A2-owned commands
must receive their own stricter reporting separate from opponent failures.

Other development facts: all 256 games terminated; 224 legacy/referee tasks diverged;
legacy checker movement consumed 51,319 draws (14,007 true ties), referee trajectories
52,434 (14,562 true ties). The 68,146-byte development TSV had SHA-256
`08684486310dd8ab13da11d6fc9ca4d529ec12684aa68e1fd51a877a3fb7696b`.

Verdict: **BLOCKED_BEFORE_IMPLEMENTATION_LOCK**. Preserve v1; do not change G3 in place.
Open a separately frozen r1 repair protocol. Every other v1 gate and the D173b resident
reproduction target remain unchanged.

