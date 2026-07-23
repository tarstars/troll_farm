# D43 preflight serialization recovery — frozen protocol (2026-07-21)

The first D43 execution completed all 131,072 transitions and printed update 32, then failed while
serializing the final report because `maximum_reward_identity_error` retained NumPy scalar type and
its gate became `numpy.bool_`. Python's JSON encoder rejected that value. No result JSON was written.
The completed checkpoint has SHA-256
`ae25f7a889ffe74a203bccefdc1140bd5d436091d63f0342612a5ec02550b469`.

Authorize exactly one recovery execution with the original D43 protocol, environment, checkpoint,
seed, transition budget, optimizer, model, features, gates, and output fields unchanged. The sole
numeric correction is to cast per-terminal reward identity error to builtin `float` before its
maximum and to normalize final gate values to builtin booleans for JSON. Preserve the first
checkpoint as `d43-binary-closed-loop-preflight-first-complete.pt`.

The recovery is valid only if every tensor in the recovered final model state is bit-identical to
the preserved first checkpoint and both configurations match exactly. Add that equality as a
mandatory gate and record both hashes. A mismatch rejects D43. No observed update metric may change
the recovery code, protocol, thresholds, or interpretation, and no long training or development bank
opens until a valid recovered report is analyzed.
