#!/usr/bin/env python3
"""Run four one-hour no-orchard/orchard live cycles and publish every leg."""

from __future__ import annotations

import fcntl
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cgauto import api_submit_once
from cgauto import arena_transfer_checkpoint as checkpoint
from cgauto import battle_taxonomy as arena
from cgauto.export_agent_replays import export_corpus


REPO = Path(__file__).resolve().parents[1]
TASK_ID = "20260803-orchard-ab-night-cycle"
ANALYSIS = Path("data/analysis/live-agent-6553250/orchard-ab-night-20260803")
SHARED = Path("data/shared-lfs/orchard-ab-night-20260803")
STATE = ANALYSIS / "state.json"
USER_ID = 1302251
MATURITY_SECONDS = 3600
HEARTBEAT_SECONDS = 900
SOURCES = {
    "no-orchard": {
        "path": Path("claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs"),
        "sha256": "d1f32c358d0f7b6a49b988c1b4ad6958a2d8ed84a9e3492632087732aae7e02a",
    },
    "orchard": {
        "path": Path("cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"),
        "sha256": "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595",
    },
}
SEQUENCE = [variant for _cycle in range(4) for variant in ("no-orchard", "orchard")]


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"[{utc()}] RUN {' '.join(command)}", flush=True)
    return subprocess.run(command, cwd=REPO, text=True, capture_output=True, check=check)


def git_publish(paths: list[Path], message: str) -> str:
    if run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0:
        raise RuntimeError("refusing to publish with pre-existing staged changes")
    run(["git", "add", "--", *[str(path) for path in paths]])
    run(["git", "diff", "--cached", "--check"])
    commit = run(["git", "commit", "-m", message]).stdout.strip()
    print(commit, flush=True)
    pushed = run(["git", "push", "origin", "agent/local_codex_1"], check=False)
    print(pushed.stdout, pushed.stderr, flush=True)
    if pushed.returncode != 0:
        raise RuntimeError("git push failed; no automatic retry")
    return run(["git", "rev-parse", "HEAD"]).stdout.strip()


def progress_message(leg: int, title: str, body: str) -> Path:
    path = Path("coordination/messages/local_codex_1") / f"{stamp()}-{TASK_ID}-progress.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "type: PROGRESS\n"
        f"task_id: {TASK_ID}\n"
        "from: local_codex_1\n"
        "to: user\n"
        "cc: claude_1, chatgpt_1\n"
        f"created_utc: {utc()}\n"
        "requires_ack: false\n"
        "---\n\n"
        f"# {title}\n\n{body}\n",
        encoding="utf-8",
    )
    return path


def cron_blackout() -> None:
    announced = False
    while True:
        now = datetime.now().astimezone()
        minute = now.hour * 60 + now.minute
        if not (5 * 60 + 14 <= minute < 5 * 60 + 32):
            return
        if not announced:
            print(f"[{utc()}] daily-collector blackout active; waiting", flush=True)
            announced = True
        time.sleep(30)


def discover_agent(submission_id: int, timeout_seconds: int = 300) -> int:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        cron_blackout()
        battles = arena.call(
            "gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None]
        )
        found = {
            int(player["playerAgentId"])
            for battle in battles
            for player in battle.get("players") or []
            if int(player.get("userId", -1)) == USER_ID
            and int(player.get("submissionId", -1)) == submission_id
        }
        if len(found) == 1:
            return found.pop()
        if len(found) > 1:
            raise RuntimeError(f"submission {submission_id} maps to multiple agents {found}")
        time.sleep(10)
    raise RuntimeError(f"agent discovery timed out for submission {submission_id}")


def recover_source(expected_sha256: str) -> None:
    with tempfile.TemporaryDirectory(prefix="troll-farm-source-check-") as directory:
        output = Path(directory) / "source.rs"
        for _attempt in range(6):
            result = run(
                [
                    sys.executable,
                    "cgauto/recover_live_source.py",
                    str(output),
                    "--expected-sha256",
                    expected_sha256,
                ],
                check=False,
            )
            if result.returncode == 0:
                return
            time.sleep(10)
    raise RuntimeError("platform source recovery did not reach the expected hash")


def scrub_checkpoint(payload: dict[str, Any]) -> dict[str, Any]:
    for row in payload.get("rows") or []:
        row["opponent"] = "PLAYER_OPPONENT"
    if payload.get("unexpected_rows"):
        raise RuntimeError("checkpoint contains unexpected identity rows")
    return payload


def wait_settled(agent_id: int, submission_id: int, timeout_seconds: int = 600) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        cron_blackout()
        battles = arena.call(
            "gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None]
        )
        matching = []
        unexpected = []
        for battle in battles:
            players = [
                player
                for player in battle.get("players") or []
                if int(player.get("userId", -1)) == USER_ID
            ]
            if len(players) != 1:
                unexpected.append(battle.get("gameId"))
                continue
            player = players[0]
            if (
                int(player.get("playerAgentId", -1)) == agent_id
                and int(player.get("submissionId", -1)) == submission_id
            ):
                matching.append(battle)
            else:
                unexpected.append(battle.get("gameId"))
        pending = sum(not battle.get("done") for battle in matching)
        if matching and not unexpected and pending == 0:
            return
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"queue did not settle: matching={len(matching)} pending={pending} "
                f"unexpected={len(unexpected)}"
            )
        time.sleep(30)


def heartbeat(state: dict[str, Any], leg_number: int, variant: str, minutes: int) -> None:
    state["updated_at_utc"] = utc()
    state["current_leg"] = leg_number
    state["current_variant"] = variant
    state["phase"] = f"maturity-wait-t+{minutes}m"
    atomic_json(STATE, state)
    message = progress_message(
        leg_number,
        f"Night A/B leg {leg_number}/8 {variant}: T+{minutes}m",
        "The exact submitted identity remains in its one-hour maturity window. No Arena "
        "mutation, result collection, or retry occurred during this phase marker.",
    )
    git_publish([STATE, message], f"Renew night A/B leg {leg_number} at {minutes} minutes")


def wait_maturity(state: dict[str, Any], leg_number: int, variant: str, accepted_mono: float) -> None:
    next_heartbeat = HEARTBEAT_SECONDS
    while True:
        elapsed = time.monotonic() - accepted_mono
        if elapsed >= MATURITY_SECONDS:
            return
        if elapsed >= next_heartbeat and next_heartbeat < MATURITY_SECONDS:
            heartbeat(state, leg_number, variant, next_heartbeat // 60)
            next_heartbeat += HEARTBEAT_SECONDS
            continue
        time.sleep(min(30, MATURITY_SECONDS - elapsed))


def collect_and_export(
    state: dict[str, Any], leg_number: int, variant: str, agent_id: int, submission_id: int
) -> dict[str, Any]:
    cron_blackout()
    wait_settled(agent_id, submission_id)
    payload = scrub_checkpoint(
        checkpoint.capture(agent_id, submission_id, f"night-ab-leg-{leg_number:02d}-{variant}")
    )
    if not payload["identity_clean"] or payload["summary"]["validity_runtime_signals"]:
        raise RuntimeError("terminal checkpoint is not identity/runtime clean")

    leg_name = f"leg-{leg_number:02d}-{variant}"
    leg_dir = ANALYSIS / leg_name
    shared_dir = SHARED / leg_name
    leg_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = leg_dir / "checkpoint.json"
    atomic_json(checkpoint_path, payload)

    collected = run(
        [
            sys.executable,
            "data/scripts/collect.py",
            "--agent-id",
            str(agent_id),
            "--agent-only",
        ],
        check=False,
    )
    collector_summary = (collected.stdout + collected.stderr).replace("tass", "TARGET")
    (leg_dir / "collector-summary.txt").write_text(collector_summary, encoding="utf-8")
    if collected.returncode != 0:
        raise RuntimeError(f"collector exited {collected.returncode}")

    manifest = export_corpus(
        agent_id=agent_id,
        submission_id=submission_id,
        battle_list=Path(f"data/raw/battles/{agent_id}.json"),
        raw_root=Path("data/raw/games"),
        output_dir=shared_dir,
        observed_at_utc=payload["observed_at"],
    )
    if manifest["game_count"] != payload["matching_finished"]:
        raise RuntimeError("package/checkpoint game-count mismatch")

    result = {
        "leg": leg_number,
        "variant": variant,
        "agent_id": agent_id,
        "submission_id": submission_id,
        "checkpoint": str(checkpoint_path),
        "package_manifest": str(shared_dir / "manifest.json"),
        "completed_at_utc": utc(),
        "arena": payload["arena"],
        "summary": payload["summary"],
        "game_count": manifest["game_count"],
        "package_sha256": manifest["package_sha256"],
        "package_bytes": manifest["package_bytes"],
    }
    atomic_json(leg_dir / "result.json", result)
    state["legs"].append(result)
    state["updated_at_utc"] = utc()
    state["phase"] = "leg-complete"
    atomic_json(STATE, state)
    message = progress_message(
        leg_number,
        f"Night A/B leg {leg_number}/8 {variant} complete",
        f"One-hour checkpoint: agent `{agent_id}`, submission `{submission_id}`, "
        f"{manifest['game_count']} games, score {payload['arena']['score']}, "
        f"rank {payload['arena']['rank']}/{payload['arena']['total']}. Full sanitized "
        "replays and exact hashes are staged under the task's Git LFS namespace.",
    )
    commit = git_publish(
        [leg_dir, shared_dir, STATE, message],
        f"Record night A/B leg {leg_number:02d} {variant}",
    )
    result["commit"] = commit
    return result


def render_final(state: dict[str, Any]) -> str:
    legs = state["legs"]
    lines = [
        "# Orchard/no-orchard overnight live cycle",
        "",
        f"Completed UTC: {utc()}",
        "",
        "Eight fresh submissions alternated no-orchard then orchard four times. Every row is a",
        "one-hour, identity-clean checkpoint with a complete sanitized replay package.",
        "",
        "| Leg | Variant | Agent | Submission | Games | Score | Rank | W/T/L | Mean margin | Catastrophes | Negative mass |",
        "|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for leg in legs:
        summary = leg["summary"]
        arena_row = leg["arena"]
        lines.append(
            f"| {leg['leg']} | {leg['variant']} | {leg['agent_id']} | {leg['submission_id']} | "
            f"{leg['game_count']} | {arena_row['score']} | {arena_row['rank']}/{arena_row['total']} | "
            f"{summary['wins']}/{summary['ties']}/{summary['losses']} | "
            f"{summary['mean_margin']:.3f} | {summary['catastrophic_losses']} | "
            f"{summary['negative_margin_mass']:.0f} |"
        )
    lines.extend(["", "## Repeated live comparison", ""])
    by_variant = {
        variant: [leg for leg in legs if leg["variant"] == variant]
        for variant in ("no-orchard", "orchard")
    }
    for variant, group in by_variant.items():
        scores = [float(leg["arena"]["score"]) for leg in group]
        margins = [float(leg["summary"]["mean_margin"]) for leg in group]
        lines.append(
            f"- {variant}: score mean {statistics.mean(scores):.3f}, median "
            f"{statistics.median(scores):.3f}; mean game margin across leg means "
            f"{statistics.mean(margins):.3f}."
        )
    pair_deltas = [
        float(legs[index + 1]["arena"]["score"]) - float(legs[index]["arena"]["score"])
        for index in range(0, 8, 2)
    ]
    lines.extend(
        [
            f"- Orchard minus no-orchard paired score deltas: {pair_deltas}; mean "
            f"{statistics.mean(pair_deltas):.3f}, median {statistics.median(pair_deltas):.3f}.",
            "",
            "Opponent queues are not paired game-for-game, so this is repeated live evidence rather",
            "than a clean causal estimate. No endpoint fallback or automatic submission retry was used.",
            "The sequence ends with orchard active.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    os.chdir(REPO)
    lock_path = Path("/tmp/troll-farm-orchard-ab-night-20260803.lock")
    lock = lock_path.open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("another night A/B controller is already active")
    if run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0:
        raise SystemExit("pre-existing staged changes")

    state: dict[str, Any] = {
        "schema": "orchard-ab-night-cycle-v1",
        "task_id": TASK_ID,
        "status": "running",
        "started_at_utc": utc(),
        "updated_at_utc": utc(),
        "sequence": SEQUENCE,
        "maturity_seconds_per_leg": MATURITY_SECONDS,
        "current_leg": None,
        "current_variant": None,
        "phase": "starting",
        "legs": [],
    }
    atomic_json(STATE, state)

    try:
        for leg_number, variant in enumerate(SEQUENCE, 1):
            cron_blackout()
            source = SOURCES[variant]
            accepted_mono = time.monotonic()
            submitted_at = utc()
            result = api_submit_once.submit_once(
                (REPO / source["path"]).resolve(), source["sha256"]
            )
            leg_dir = ANALYSIS / f"leg-{leg_number:02d}-{variant}"
            leg_dir.mkdir(parents=True, exist_ok=True)
            result["submitted_at_utc"] = submitted_at
            atomic_json(leg_dir / "submit.json", result)
            if not result["accepted"]:
                raise RuntimeError(
                    f"leg {leg_number} submission failed; ambiguous={result['ambiguous']}"
                )
            submission_id = int(result["submission_id"])
            state.update(
                {
                    "updated_at_utc": utc(),
                    "current_leg": leg_number,
                    "current_variant": variant,
                    "current_submission_id": submission_id,
                    "phase": "agent-discovery",
                }
            )
            atomic_json(STATE, state)
            agent_id = discover_agent(submission_id)
            recover_source(source["sha256"])
            result["agent_id"] = agent_id
            result["platform_source_verified"] = True
            atomic_json(leg_dir / "submit.json", result)

            state.update(
                {
                    "updated_at_utc": utc(),
                    "current_leg": leg_number,
                    "current_variant": variant,
                    "current_agent_id": agent_id,
                    "current_submission_id": submission_id,
                    "phase": "maturity-wait",
                }
            )
            atomic_json(STATE, state)
            message = progress_message(
                leg_number,
                f"Night A/B leg {leg_number}/8 {variant} submitted",
                f"Canonical endpoint accepted exact source SHA `{source['sha256'][:12]}...` once as "
                f"agent `{agent_id}`, submission `{submission_id}`. Platform source recovery is "
                "exact. The one-hour maturity clock is running.",
            )
            git_publish(
                [leg_dir / "submit.json", STATE, message],
                f"Start night A/B leg {leg_number:02d} {variant}",
            )
            wait_maturity(state, leg_number, variant, accepted_mono)
            collect_and_export(state, leg_number, variant, agent_id, submission_id)

        state["status"] = "complete"
        state["phase"] = "complete"
        state["updated_at_utc"] = utc()
        atomic_json(STATE, state)
        result_path = ANALYSIS / "result.md"
        result_path.write_text(render_final(state), encoding="utf-8")
        message = progress_message(
            8,
            "Night orchard/no-orchard A/B cycle complete",
            "All eight one-hour legs, checkpoints, and sanitized replay packages are complete. "
            "The final active submission is the orchard variant. See the task result table.",
        )
        git_publish([STATE, result_path, message], "Complete orchard/no-orchard night cycle")
        return 0
    except Exception as error:  # preserve a durable local stop record; never auto-retry submit
        state["status"] = "failed"
        state["phase"] = "failed"
        state["updated_at_utc"] = utc()
        state["error"] = f"{type(error).__name__}: {error}"
        ambiguous = "ambiguous=True" in str(error)
        if state.get("current_variant") == "no-orchard" and not ambiguous:
            orchard = SOURCES["orchard"]
            restore = api_submit_once.submit_once(
                (REPO / orchard["path"]).resolve(), orchard["sha256"]
            )
            restore["attempted_at_utc"] = utc()
            restore["reason"] = "safe orchard restore after non-ambiguous cycle failure"
            state["failure_restore"] = restore
            if restore["accepted"]:
                state["current_variant"] = "orchard-restore-after-failure"
        atomic_json(STATE, state)
        print(f"[{utc()}] FAILED {state['error']}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
