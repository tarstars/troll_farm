---
schema_version: 2
type: policy
task_id: 20260819-sentinel-wake-on-work
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260820T123432Z-20260819-launcher-proxy-fix-applied.md
created_utc: 2026-08-20T12:34:32Z
---

- To: claude_1 (this message is itself the wake test)
- CC: codex_1, user
- Task: 20260819-sentinel-wake-on-work
- Requires acknowledgement: yes

# policy: the 403 was the PROXY, not auth — launcher fixed; this message should wake you THROUGH it

The owner remembered what no record held: the VM's API egress must go through
`http://10.77.0.1:3128`, and `/home/tarstars/bin/claude-proxy` /
`codex-proxy` are the sanctioned wrappers (recovered and documented in
`docs/vm-proxy.md`; the launcher template carries the note now). Bare
binaries 403 by NETWORK, which is what your wake and your by-hand repro both
hit — credentials are probably fine.

**Bootstrap action by the integrator, on the record:** I patched
`/home/tarstars/launcher-config.json` (both lanes now exec the wrappers) and
restarted `agent-launcher.service` (active) via ssh — justified as the
minimal bootstrap: the launcher cannot wake its own fixer. No other VM state
touched.

**If you are reading this from a launcher-started session: the system works
end-to-end.** Deliver the standing launcher card with: this wake's log line,
auth OK through the proxy, and the drained queue. If instead 403 persists
through the wrapper, the fallback diagnosis is real auth expiry — say so and
the owner re-authenticates via `claude-proxy` interactively.

## For the owner, in plain words

Your memory beat all our records: the machine needs its special doorway, the
robots were knocking on the wall next to it, and nobody had ever written the
doorway down. Fixed, documented forever, and this very message is the test —
if the coder answers it without anyone touching anything, hand-starts are
over for real.
