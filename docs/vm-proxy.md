# VM egress proxies — claude-proxy / codex-proxy (RECOVERED KNOWLEDGE, 2026-08-20)

The troll-vm (`compute-vm-4-16-20-ssd-1785607330087`, ssh alias `troll-vm`)
cannot reach the model APIs directly: egress must go through the local proxy
`http://10.77.0.1:3128`. Two wrapper scripts exist for exactly this and are
THE sanctioned way to run the CLIs there:

- `/home/tarstars/bin/claude-proxy` — exports HTTP(S)_PROXY to the proxy,
  sets `CLAUDE_CODE_SHELL_PREFIX=/usr/local/bin/claude-direct-command`
  (shell commands bypass the proxy), then execs `~/.local/bin/claude`.
- `/home/tarstars/bin/codex-proxy` — same proxy env, execs `~/.local/bin/codex`.

**Bare `claude`/`codex` on the VM fail with 403** ("Request not allowed" /
Forbidden) — that is the network refusing direct egress, NOT expired
credentials. This bit on 2026-08-20: the agent launcher's first observed wake
launched bare `claude -p` and died on 403; so did the by-hand reproduction;
the failure was misread as auth expiry until the owner remembered the
proxies. The launcher config now points at the wrappers.

History note: the wrappers predate the repo records — they were set up in
VM-side agent sessions and never written down anywhere (no repo ref, no
transcript on the laptop mentioned them). This file exists so that can never
happen again: **infrastructure that lives only in someone's shell is
infrastructure the next session doesn't have.**
