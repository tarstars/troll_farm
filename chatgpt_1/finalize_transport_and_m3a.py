#!/usr/bin/env python3
"""Execute and persist chatgpt_1's remaining transport and M3a closures.

Designed for a GitHub Actions checkout of agent/chatgpt_1-verify-20260811.
It records literal SHA-256 values, runs the authoritative inbox sweep, renews
and verifies the M3a golden bundle, commits the durable evidence, and pushes it
back to the verification branch. The renewed bundle remains externally reviewed,
not self-accepted.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "chatgpt_1/verification"
GOLDEN = REPO / "chatgpt_1/m3a-d1-situation-library-2026-08-10.json"
OLD_MANIFEST = REPO / "chatgpt_1/m3a-golden-set-manifest-2026-08-10.json"
NEW_MANIFEST = REPO / "chatgpt_1/m3a-golden-set-manifest-v2-2026-08-09.json"
VERIFIER = REPO / "chatgpt_1/m3a_verify_golden_set.py"
TESTS = REPO / "chatgpt_1/test_m3a_golden_set.py"
EXTRACTOR = REPO / "chatgpt_1/m3a_extract_from_panel.py"
VERIFY_BRANCH = "agent/chatgpt_1-verify-20260811"


def run(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args), cwd=REPO, text=True, capture_output=True, errors="replace"
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def write(name: str, text: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(text, encoding="utf-8")


def renew_bundle() -> tuple[int, int]:
    regenerated = OUT / "m3a-d1-situation-library-regenerated.json"
    extract = run(
        sys.executable,
        str(EXTRACTOR),
        "--check",
        "--output",
        str(regenerated),
    )
    write("m3a-extractor.stdout.txt", extract.stdout)
    write("m3a-extractor.stderr.txt", extract.stderr)
    write("m3a-extractor.exit-code.txt", f"{extract.returncode}\n")
    if extract.returncode != 0:
        raise RuntimeError("M3a extractor failed; see durable verification output")

    old_text = GOLDEN.read_text(encoding="utf-8")
    new_text = regenerated.read_text(encoding="utf-8")
    write(
        "m3a-pre-renewal.diff",
        "".join(
            difflib.unified_diff(
                old_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=str(GOLDEN.relative_to(REPO)),
                tofile="regenerated",
            )
        ),
    )
    GOLDEN.write_text(new_text, encoding="utf-8")

    verifier_text = VERIFIER.read_text(encoding="utf-8")
    verifier_text = verifier_text.replace(
        "m3a-golden-set-manifest-2026-08-10.json",
        "m3a-golden-set-manifest-v2-2026-08-09.json",
    ).replace(
        "troll-farm-m3a-golden-bundle/v1",
        "troll-farm-m3a-golden-bundle/v2",
    )
    VERIFIER.write_text(verifier_text, encoding="utf-8")

    tests_text = TESTS.read_text(encoding="utf-8").replace(
        "m3a-golden-set-manifest-2026-08-10.json",
        "m3a-golden-set-manifest-v2-2026-08-09.json",
    )
    TESTS.write_text(tests_text, encoding="utf-8")

    manifest = json.loads(OLD_MANIFEST.read_text(encoding="utf-8"))
    manifest["schema"] = "troll-farm-m3a-golden-bundle/v2"
    manifest["supersedes"] = [str(OLD_MANIFEST.relative_to(REPO))]
    manifest["renewal"] = {
        "reason": (
            "The v1 golden JSON predated the extractor's episode_ledger_sha256 "
            "field; second-checkout execution reproduced all 34 episodes and "
            "exposed the byte drift."
        ),
        "source_review": (
            "local_claude_1/m3a-golden-bundle-verification-2026-08-10.md"
        ),
        "renewed_by": "GitHub Actions on agent/chatgpt_1-verify-20260811",
        "policy": (
            "All source, toolchain, test, and output bytes are re-pinned together; "
            "external review remains mandatory before adoption."
        ),
    }
    manifest["regeneration"]["bundle_verification"] = (
        "python3 chatgpt_1/m3a_verify_golden_set.py --manifest "
        "chatgpt_1/m3a-golden-set-manifest-v2-2026-08-09.json"
    )
    for artifact in manifest["artifacts"]:
        path = REPO / artifact["path"]
        if not path.is_file():
            raise RuntimeError(f"missing manifest member: {artifact['path']}")
        artifact["git_blob_sha1"] = git_blob_sha1(path)
        artifact["sha256"] = sha256(path)
    NEW_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    verifier = run(
        sys.executable,
        str(VERIFIER),
        "--manifest",
        str(NEW_MANIFEST),
    )
    tests = run(sys.executable, str(TESTS))
    write("m3a-verifier.stdout.txt", verifier.stdout)
    write("m3a-verifier.stderr.txt", verifier.stderr)
    write("m3a-verifier.exit-code.txt", f"{verifier.returncode}\n")
    write("m3a-tests.stdout.txt", tests.stdout)
    write("m3a-tests.stderr.txt", tests.stderr)
    write("m3a-tests.exit-code.txt", f"{tests.returncode}\n")
    write(
        "m3a-summary.txt",
        "\n".join(
            [
                f"extractor_exit_code={extract.returncode}",
                f"verifier_exit_code={verifier.returncode}",
                f"tests_exit_code={tests.returncode}",
                f"golden_sha256={sha256(GOLDEN)}",
                f"golden_git_blob={git_blob_sha1(GOLDEN)}",
                f"manifest_sha256={sha256(NEW_MANIFEST)}",
                f"manifest_git_blob={git_blob_sha1(NEW_MANIFEST)}",
                "",
            ]
        ),
    )
    return verifier.returncode, tests.returncode


def record_transport() -> int:
    run("git", "fetch", "origin", "+refs/heads/*:refs/remotes/origin/*", check=True)
    identity = [
        f"workflow_head={run('git', 'rev-parse', 'HEAD', check=True).stdout.strip()}",
        f"main={run('git', 'rev-parse', 'refs/remotes/origin/main', check=True).stdout.strip()}",
        (
            "chatgpt_1="
            + run(
                "git", "rev-parse", "refs/remotes/origin/agent/chatgpt_1", check=True
            ).stdout.strip()
        ),
        (
            "inbox_sweep_git_blob="
            + run("git", "hash-object", "scripts/inbox_sweep.py", check=True).stdout.strip()
        ),
        f"inbox_sweep_sha256={sha256(REPO / 'scripts/inbox_sweep.py')}",
        f"lint_outbox_sha256={sha256(REPO / 'scripts/lint_outbox.py')}",
        "",
    ]
    write("transport-identity.txt", "\n".join(identity))

    sweep = run(
        sys.executable,
        str(REPO / "scripts/inbox_sweep.py"),
        "--me",
        "chatgpt_1",
        "--fetch",
    )
    write("inbox-sweep.stdout.txt", sweep.stdout)
    write("inbox-sweep.stderr.txt", sweep.stderr)
    write("inbox-sweep.exit-code.txt", f"{sweep.returncode}\n")
    return sweep.returncode


def write_reports(sweep_rc: int, verifier_rc: int, tests_rc: int) -> None:
    (REPO / "chatgpt_1/transport-verification-2026-08-09.md").write_text(
        "# Transport verification\n\n"
        "Generated from an exact GitHub Actions checkout. Literal SHA-256 values, "
        "the Git blob, authoritative sweep stdout/stderr, and exit code are under "
        "`chatgpt_1/verification/`.\n\n"
        f"- inbox sweep exit code: `{sweep_rc}`\n"
        "- exit 0: healthy/no unacknowledged obligation\n"
        "- exit 1: healthy/acknowledgment obligation remains\n"
        "- exit 2: transport or delivery failure\n",
        encoding="utf-8",
    )
    (REPO / "chatgpt_1/m3a-golden-bundle-renewal-2026-08-09.md").write_text(
        "# M3a golden-bundle renewal v2\n\n"
        "The v1 bundle's data was correct, but its golden JSON predated the "
        "extractor's `episode_ledger_sha256` field. This renewal regenerates the "
        "JSON, moves the verifier/tests to a v2 manifest, and re-pins every source, "
        "tool, test, and output byte together.\n\n"
        f"- verifier exit code: `{verifier_rc}`\n"
        f"- tests exit code: `{tests_rc}`\n"
        "- external execution and cross-implementation reviews remain mandatory; "
        "this commit is not self-acceptance.\n",
        encoding="utf-8",
    )


def commit_and_push() -> str:
    run("git", "config", "user.name", "github-actions[bot]", check=True)
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
        check=True,
    )
    paths = [
        str(GOLDEN.relative_to(REPO)),
        str(VERIFIER.relative_to(REPO)),
        str(TESTS.relative_to(REPO)),
        str(NEW_MANIFEST.relative_to(REPO)),
        "chatgpt_1/m3a-golden-bundle-renewal-2026-08-09.md",
        "chatgpt_1/transport-verification-2026-08-09.md",
        "chatgpt_1/verification",
    ]
    run("git", "add", "--", *paths, check=True)
    commit = run(
        "git",
        "commit",
        "-m",
        "verify transport and renew M3a golden bundle v2 [skip ci]",
        check=True,
    )
    push = run("git", "push", "origin", f"HEAD:{VERIFY_BRANCH}")
    if push.returncode != 0:
        raise RuntimeError(f"push failed:\n{push.stdout}\n{push.stderr}")
    return run("git", "rev-parse", "HEAD", check=True).stdout.strip()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sweep_rc = record_transport()
    verifier_rc, tests_rc = renew_bundle()
    write_reports(sweep_rc, verifier_rc, tests_rc)
    commit_sha = commit_and_push()
    print(f"result_commit={commit_sha}")
    print(f"inbox_sweep_exit_code={sweep_rc}")
    print(f"m3a_verifier_exit_code={verifier_rc}")
    print(f"m3a_tests_exit_code={tests_rc}")
    return 0 if verifier_rc == 0 and tests_rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
