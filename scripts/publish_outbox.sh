#!/usr/bin/env bash
# Canonical outbox publish: lint (armed) -> commit -> push -> remote-verify.
# The lint is NEVER piped; its exit code is the gate. This exists because
# `lint | tail -3 && commit && push` gated on tail for a whole session and
# published an invalid immutable message (guards task, instance 4 / G5 F1).
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "usage: publish_outbox.sh <agent-id> <commit-message>" >&2
    exit 2
fi
AGENT="$1"
MSG="$2"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
# symbolic-ref, not rev-parse: must work on an unborn branch (fresh clone)
BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || true)"
if [ -z "$BRANCH" ]; then
    echo "refusing: detached HEAD" >&2
    exit 2
fi
if [ "$BRANCH" != "agent/$AGENT" ]; then
    echo "refusing: on branch '$BRANCH', expected 'agent/$AGENT'" >&2
    exit 2
fi

python3 scripts/lint_outbox.py --me "$AGENT" --staged

git commit -m "$MSG"
git push origin "$BRANCH"
git fetch origin "$BRANCH"
if [ "$(git rev-parse HEAD)" != "$(git rev-parse "origin/$BRANCH")" ]; then
    echo "remote-verify FAILED: origin/$BRANCH != HEAD" >&2
    exit 1
fi
echo "published $(git rev-parse --short HEAD) on $BRANCH — lint armed, remote verified"
