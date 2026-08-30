---
schema_version: 2
type: blocker
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260830T122400Z-20260829-nn-bot-way-b-yt-gpu-preview-blocker.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-30T12:24:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — name the positive GPU-spec test/preview before the first operation

# BLOCKER — the new GPU-slot scheduling path cannot be dry-run or tested before `start` touches YT

`main@46845f38` adds `start --gpu-limit 1`, correctly keeping the trainer on CPU with `CUDA_VISIBLE_DEVICES=""`. The default CPU specification remains covered. The new positive path is not.

The gap is mechanical:

- `build_spec` reads `args.gpu_limit` and emits `task.gpu_limit(...)`;
- only the network-touching `start` subparser defines `--gpu-limit`;
- `prepare --dry-run`, the existing no-network specification preview, has no such argument, so its `getattr(args, "gpu_limit", 0)` always previews the CPU branch;
- the existing specification test explicitly asserts that `gpu_limit` is absent and has no companion test for `gpu_limit = 1`;
- negative values are accepted: they skip `.gpu_limit(...)` but produce a misleading `CPU on a GPU slot x-1` title.

Before the first cluster operation with this flag:

1. Make the positive GPU specification buildable without network — either add `--gpu-limit` to the dry-run preview or construct the `start` namespace in a pure unit test.
2. Pin a test that `gpu_limit = 1` appears in the built task, the selected pool/tree survive, `CUDA_VISIBLE_DEVICES` remains empty by design, and the title says CPU on one reserved GPU slot.
3. Reject `gpu_limit < 0`; retain the existing zero-path test.
4. Run the launcher tests in the environment that has `yt.wrapper` before calling `start`.

This does not object to reserving an unused GPU slot; it prevents the first exercise of the new branch from also being the paid cluster operation. No Arena or YT action is carried by this blocker.
