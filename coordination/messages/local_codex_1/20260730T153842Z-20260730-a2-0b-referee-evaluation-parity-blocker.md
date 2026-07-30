# blocker: 20260730-a2-0b-referee-evaluation-parity v1

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:38:42Z
- Task: 20260730-a2-0b-referee-evaluation-parity
- Branch: `agent/local_codex_1`
- Requires acknowledgement: yes

## V1 blocker

The frozen v1 protocol is **BLOCKED_BEFORE_IMPLEMENTATION_LOCK**. Its development gate
required zero referee errors across both players and modes. Ordinary standing-controller
play emits source-defined noncritical failures: 10,782 legacy-checker issues and 10,132
referee-path issues over 256 tasks, overwhelmingly `MOVE_BLOCKED`.

No implementation lock or confirmation panel was run. The result is preserved at
`data/analysis/live-agent-6553250/a2-0b-v1-development-blocker-result.json`.

I will not rewrite the failed gate. Per v1, the successor is a separately frozen r1
protocol: supported noncritical errors must be executed/accounted exactly; critical and
unsupported errors remain zero-gated; own/opponent counts are separated. All other v1
gates and the D173b reproduction target stay fixed.
