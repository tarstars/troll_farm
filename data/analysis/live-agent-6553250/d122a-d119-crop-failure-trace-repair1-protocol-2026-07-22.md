# D122a crop-trace repair 1 — frozen mechanics amendment

Date: 2026-07-22  
Status: frozen after the first trace exception and before any successful trace result

The original D122 evaluator assumed every crop failure followed an intervention. Its first run
reproduced the frozen models and then stopped with `choice=None` while building safe alternatives;
no result file was written. This reveals only that at least one crop failure is a non-intervened
forced-control outcome. No task identity, policy metric, or alternative score was emitted.

Repair only the result representation: when a crop-failure trace has no selected choice, record
`forced_control_crop_failure_without_intervention`, mark action alternatives inapplicable, and
continue. All models, policies, data, tracing fields, focus set, and interpretation constraints
remain unchanged. The original protocol and lock remain evidence; this repair receives a new lock.
