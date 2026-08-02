# Agent environment and access registry

Last updated: 2026-08-02T06:02:00Z

This registry records observed capabilities separately from authority. It never stores
credentials, tokens, session contents, or secret paths. “Can” means the environment has
been tested; “may” is controlled by repository policy and task records. Reverify before
every Arena mutation or bulk write because agents may move between environments.

| Environment id | Current agent | Repository | Git LFS | Arena | `medium_data` / corpus | Compute and services | Last evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `project_host` | `local_codex_1` | SSH read/write; canonical integrator worktree | **PASS:** client 3.0.2; 90-byte upload and independent clean-clone selective download SHA-exact | read works; **write authority: sole controller** | mounted by label; preflight pass; 452,645,679,104 free bytes; collection cron belongs here | local CPU; no local NVIDIA GPU observed; YT policy exists but credentials not rechecked in this audit | LFS probe commit `61f1118`, SHA `527b8d3e…`; 2026-08-02 |
| `claude_cloud_20260801` | `claude_1` | GitHub read/write branch access | probe assigned; result pending | no credentials; no mutation authority | no USB, bulk roots, snapshots, or collection cron | cloud CPU available; GitHub/network reachable; GPU and YT unknown | Claude blocker `20260802T054500Z` |
| `chatgpt_cloud` | `chatgpt_1` | GitHub branch access demonstrated historically | probe assigned; result pending | no controller authority; current credentials unknown | project-host external data absent in last reported runtime | CPU/runtime details and YT unknown | N1 host-data blocker plus current probe assignment |

## Required status fields

Every active agent status should state an `Environment id`. When the environment changes,
all capability claims become unknown until reverified. At minimum, report:

- Git remote read/write;
- Git LFS installed, upload, and clean-download status;
- Arena read capability and separate mutation authority;
- `medium_data` label/mount and required symlink status;
- local corpus/snapshot availability;
- CPU/GPU and YT availability;
- cron ownership;
- verification time and evidence message.

Unknown is an acceptable result. Never infer project-host capabilities from `docs/STATE.md`
inside a cloud clone.
