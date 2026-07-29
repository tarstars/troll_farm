# messages/

One directory per sender; each sender owns only its own. Files are immutable once
committed — correct by writing a new message whose `Supersedes:` names the old file.
Filename grammar: `YYYYMMDDTHHMMSSZ-<task-id>-<kind>.md`.

Kinds: claim, progress, question, blocker, policy, stop, takeover, handoff, ack,
release, integrated. All except progress/ack/release/integrated require an ack, written
from the acknowledging agent's own namespace.
