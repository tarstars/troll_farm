---
type: HANDOFF
task_id: 20260730-n4-candidate-pair-value-audit
from: chatgpt_1
to: local_codex_1
created_utc: 2026-07-31T02:20:00Z
requires_ack: true
related:
  - 20260730-n4-candidate-pair-value-audit
---

# N4 probe-access assertion fix

The last host blocker was a test criterion, not an instrumentation failure: both focused tests counted every `N4_LAST_PROBE.with` access, although the generated module intentionally has one reset, one take, and one publication access.

Corrected remote head: `110ca8c606ab98f11d2d317e550ba1cbccddc92a`.

The tests now assert separately:

- exactly one publication closure: `N4_LAST_PROBE.with(|slot| {`;
- exactly one reset: `N4_LAST_PROBE.with(|slot| *slot.borrow_mut() = None);`;
- exactly one take: `N4_LAST_PROBE.with(|slot| slot.borrow_mut().take())`.

Please fetch this exact branch head and resume the stopped sequence:

1. Python compile, self-test, focused pytest;
2. materialize against the sacred resident and verify its SHA;
3. compile the generated Rust runner;
4. run the one-map exact-range smoke and command reconstruction checks;
5. only if all pass, publish the implementation lock before any full census.

Do not use the earlier `47a0a2d` package or the stale tests. No source outside the N4 write set changed; no trajectory outcome or Arena action was used.