#!/usr/bin/env python3
"""Create and enforce a one-read, rotating official-map holdout.

The seed payload is authenticated ciphertext.  Commands print identifiers and
counts, never keys or seeds.  Private keys and the rollback-resistant audit
state belong outside Git in a coordinator-controlled directory.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import tempfile
from typing import Any


SCHEMA_VERSION = 1
PBKDF2_ITERATIONS = 250_000
KEY_SUFFIX = ".key"
ALLOCATION_KEY = "allocation.key"
LOCKED_OPPONENTS = [
    ("delineate", 6479768),
    ("wala", 6481141),
    ("escdemon", 6483545),
    ("norxondor", 6480540),
    ("laconic", 6482055),
]


class SealError(RuntimeError):
    """A seal invariant failed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SealError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SealError(f"expected a JSON object in {path}")
    return value


def atomic_write(path: Path, value: bytes, mode: int = 0o644, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive and path.exists():
        raise SealError(f"refusing to overwrite {path}")
    temp = path.parent / f".{path.name}.tmp-{os.getpid()}-{secrets.token_hex(4)}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temp, flags, mode)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            try:
                os.link(temp, path)
            except FileExistsError as exc:
                raise SealError(f"refusing to overwrite {path}") from exc
            temp.unlink()
        else:
            os.replace(temp, path)
        os.chmod(path, mode)
    finally:
        if temp.exists():
            temp.unlink()


def key_path(key_dir: Path, seal_id: str) -> Path:
    return key_dir / f"{seal_id}{KEY_SUFFIX}"


def write_key(path: Path, key: bytes) -> None:
    if len(key) != 32:
        raise SealError("keys must be 32 bytes")
    atomic_write(path, key.hex().encode() + b"\n", mode=0o600, exclusive=True)


def read_key(path: Path) -> bytes:
    try:
        file_mode = stat.S_IMODE(path.stat().st_mode)
        text = path.read_text().strip()
        key = bytes.fromhex(text)
    except (OSError, ValueError) as exc:
        raise SealError(f"cannot read private key {path}: {exc}") from exc
    if file_mode & 0o077:
        raise SealError(f"private key permissions are too broad: {path} mode {file_mode:o}")
    if len(key) != 32:
        raise SealError(f"private key {path} is not 32 bytes")
    return key


def allocation_slice(
    allocation_key: bytes,
    seed_start: int,
    seed_stop_exclusive: int,
    count: int,
    sequence: int,
) -> list[int]:
    span = seed_stop_exclusive - seed_start
    offset = (sequence - 1) * count
    if span <= 0 or count <= 0 or sequence <= 0 or offset + count > span:
        raise SealError("invalid population or map count")
    ranked = sorted(
        range(seed_start, seed_stop_exclusive),
        key=lambda seed: (
            hmac.new(
                allocation_key,
                b"sealed-holdout-v1:allocation\0" + seed.to_bytes(8, "big", signed=True),
                hashlib.sha256,
            ).digest(),
            seed,
        ),
    )
    return ranked[offset : offset + count]


def openssl_crypt(source: Path, target: Path, key_file: Path, *, decrypt: bool) -> None:
    command = [
        "openssl",
        "enc",
        "-d" if decrypt else "-e",
        "-aes-256-ctr",
        "-pbkdf2",
        "-iter",
        str(PBKDF2_ITERATIONS),
        "-md",
        "sha256",
        "-pass",
        f"file:{key_file}",
        "-in",
        str(source),
        "-out",
        str(target),
    ]
    if not decrypt:
        command.insert(4, "-salt")
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        detail = completed.stderr.strip() or "openssl failed"
        raise SealError(detail)


def ciphertext_hmac(key: bytes, ciphertext: bytes) -> str:
    mac_key = hmac.new(key, b"sealed-holdout-v1:ciphertext-mac", hashlib.sha256).digest()
    return hmac.new(mac_key, ciphertext, hashlib.sha256).hexdigest()


def create_seal(
    root: Path,
    key_dir: Path,
    seal_id: str,
    role: str,
    key: bytes,
    seeds: list[int],
    selection_sequence: int,
    population: dict[str, int],
    generator: dict[str, str],
    created_utc: str,
) -> dict[str, Any]:
    if len(seeds) != len(set(seeds)):
        raise SealError("selection contains duplicate seeds")
    private_key = key_path(key_dir, seal_id)
    write_key(private_key, key)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "seal_id": seal_id,
        "created_utc": created_utc,
        "generator": generator,
        "population": population,
        "map_count": len(seeds),
        "selection_sequence": selection_sequence,
        "seeds": seeds,
    }
    payload_bytes = canonical_json(payload)
    sealed_dir = root / "sealed"
    sealed_dir.mkdir(parents=True, exist_ok=True)
    cipher_path = sealed_dir / f"{seal_id}.enc"
    if cipher_path.exists():
        raise SealError(f"refusing to overwrite {cipher_path}")
    with tempfile.NamedTemporaryFile(dir=key_dir, prefix=f".{seal_id}-payload-", delete=False) as tmp:
        plain_path = Path(tmp.name)
        os.chmod(plain_path, 0o600)
        tmp.write(payload_bytes)
    cipher_temp = cipher_path.parent / f".{cipher_path.name}.tmp-{os.getpid()}"
    try:
        openssl_crypt(plain_path, cipher_temp, private_key, decrypt=False)
        ciphertext = cipher_temp.read_bytes()
        atomic_write(cipher_path, ciphertext, exclusive=True)
    finally:
        plain_path.unlink(missing_ok=True)
        cipher_temp.unlink(missing_ok=True)

    relative_cipher = cipher_path.relative_to(root).as_posix()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "seal_id": seal_id,
        "role_at_creation": role,
        "status_at_creation": f"sealed_{role}",
        "created_utc": created_utc,
        "generator": generator,
        "population": population,
        "map_count": len(seeds),
        "candidate_player_index": 0,
        "pairing": "candidate and frozen baseline use the same seed and external opponent",
        "selection": {
            "algorithm": "slice of population ranked by secret HMAC-SHA256; disjoint by construction",
            "domain": "sealed-holdout-v1:allocation",
            "sequence": selection_sequence,
            "rank_start": (selection_sequence - 1) * len(seeds),
            "rank_stop_exclusive": selection_sequence * len(seeds),
        },
        "payload_sha256": sha256_bytes(payload_bytes),
        "ciphertext": {
            "path": relative_cipher,
            "algorithm": "AES-256-CTR via openssl enc; encrypt-then-HMAC-SHA256",
            "pbkdf2_iterations": PBKDF2_ITERATIONS,
            "sha256": sha256_bytes(ciphertext),
            "hmac_sha256": ciphertext_hmac(key, ciphertext),
        },
        "key": {
            "id": seal_id,
            "sha256_commitment": sha256_bytes(key),
            "location_policy": "coordinator-private path outside Git and shared artifact storage",
        },
        "use_rule": {
            "authorized_reads": 1,
            "precommitted_gate_required": True,
            "sealed_successor_required_before_read": True,
            "retire_to_development_on_read": True,
        },
    }
    manifest_path = sealed_dir / f"{seal_id}.manifest.json"
    atomic_write(manifest_path, canonical_json(manifest), exclusive=True)
    return manifest


def seal_manifest_path(root: Path, seal_id: str) -> Path:
    return root / "sealed" / f"{seal_id}.manifest.json"


def load_manifest(root: Path, seal_id: str) -> dict[str, Any]:
    manifest = load_json(seal_manifest_path(root, seal_id))
    if manifest.get("seal_id") != seal_id:
        raise SealError(f"manifest identity mismatch for {seal_id}")
    return manifest


def decrypt_payload(root: Path, key_dir: Path, seal_id: str) -> dict[str, Any]:
    manifest = load_manifest(root, seal_id)
    private_key = key_path(key_dir, seal_id)
    key = read_key(private_key)
    if sha256_bytes(key) != manifest["key"]["sha256_commitment"]:
        raise SealError(f"key commitment mismatch for {seal_id}")
    cipher_path = root / manifest["ciphertext"]["path"]
    ciphertext = cipher_path.read_bytes()
    if sha256_bytes(ciphertext) != manifest["ciphertext"]["sha256"]:
        raise SealError(f"ciphertext SHA-256 mismatch for {seal_id}")
    if not hmac.compare_digest(
        ciphertext_hmac(key, ciphertext), manifest["ciphertext"]["hmac_sha256"]
    ):
        raise SealError(f"ciphertext HMAC mismatch for {seal_id}")
    with tempfile.NamedTemporaryFile(dir=key_dir, prefix=f".{seal_id}-open-", delete=False) as tmp:
        plain_path = Path(tmp.name)
    try:
        openssl_crypt(cipher_path, plain_path, private_key, decrypt=True)
        payload_bytes = plain_path.read_bytes()
    finally:
        plain_path.unlink(missing_ok=True)
    if sha256_bytes(payload_bytes) != manifest["payload_sha256"]:
        raise SealError(f"payload commitment mismatch for {seal_id}")
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError as exc:
        raise SealError(f"invalid decrypted payload for {seal_id}") from exc
    validate_payload(payload, manifest)
    return payload


def validate_payload(payload: dict[str, Any], manifest: dict[str, Any]) -> None:
    seeds = payload.get("seeds")
    if not isinstance(seeds, list) or any(type(seed) is not int for seed in seeds):
        raise SealError("payload seeds are not an integer list")
    if payload.get("seal_id") != manifest["seal_id"] or len(seeds) != manifest["map_count"]:
        raise SealError("payload identity or count mismatch")
    if payload.get("selection_sequence") != manifest["selection"]["sequence"]:
        raise SealError("payload selection sequence mismatch")
    if len(set(seeds)) != len(seeds):
        raise SealError("payload contains duplicate seeds")
    start = manifest["population"]["seed_start"]
    stop = manifest["population"]["seed_stop_exclusive"]
    if any(not start <= seed < stop for seed in seeds):
        raise SealError("payload seed outside reserved population")


def verify(root: Path, key_dir: Path | None) -> dict[str, Any]:
    state = load_json(root / "seal-state.json")
    seal_ids = list(state.get("retired_seal_ids", []))
    for field in ("active_seal_id", "standby_seal_id"):
        if state.get(field):
            seal_ids.append(state[field])
    if len(seal_ids) != len(set(seal_ids)) or not seal_ids:
        raise SealError("state has duplicate or missing seal identities")
    if state.get("authorized_open_count") != len(state.get("retired_seal_ids", [])):
        raise SealError("authorized-open count does not match retired seals")
    manifest_hashes = state.get("seal_manifest_sha256")
    if not isinstance(manifest_hashes, dict) or set(manifest_hashes) != set(seal_ids):
        raise SealError("state does not pin every seal manifest exactly once")
    for seal_id in seal_ids:
        if sha256_file(seal_manifest_path(root, seal_id)) != manifest_hashes[seal_id]:
            raise SealError(f"manifest SHA-256 mismatch for {seal_id}")
        manifest = load_manifest(root, seal_id)
        if manifest.get("map_count") != state.get("map_count"):
            raise SealError(f"map count mismatch for {seal_id}")
        if manifest.get("population") != state.get("population"):
            raise SealError(f"population mismatch for {seal_id}")
        cipher_path = root / manifest["ciphertext"]["path"]
        if sha256_file(cipher_path) != manifest["ciphertext"]["sha256"]:
            raise SealError(f"ciphertext SHA-256 mismatch for {seal_id}")
        if key_dir is not None:
            key = read_key(key_path(key_dir, seal_id))
            if sha256_bytes(key) != manifest["key"]["sha256_commitment"]:
                raise SealError(f"key commitment mismatch for {seal_id}")
            if not hmac.compare_digest(
                ciphertext_hmac(key, cipher_path.read_bytes()),
                manifest["ciphertext"]["hmac_sha256"],
            ):
                raise SealError(f"ciphertext HMAC mismatch for {seal_id}")
    if key_dir is not None:
        audit = load_json(key_dir / "audit-state.json")
        if audit != state:
            raise SealError("tracked and private audit states differ")
        allocation_key = read_key(key_dir / ALLOCATION_KEY)
        if sha256_bytes(allocation_key) != state.get("allocation_key_sha256"):
            raise SealError("allocation-key commitment mismatch")
        active = state["active_seal_id"]
        if (key_dir / f".opened-{active}.lock").exists():
            raise SealError("active seal has an open marker")
        if (root / "receipts" / f"{active}.json").exists():
            raise SealError("active seal has a tracked read receipt")
        for retired in state["retired_seal_ids"]:
            if not (key_dir / f".opened-{retired}.lock").exists():
                raise SealError(f"retired seal lacks private open marker: {retired}")
            if not (root / "receipts" / f"{retired}.json").exists():
                raise SealError(f"retired seal lacks tracked read receipt: {retired}")
    return state


def state_document(
    population: dict[str, int],
    map_count: int,
    active: str,
    standby: str | None,
    manifest_hashes: dict[str, str],
    allocation_key_sha256: str,
    now: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "population": population,
        "map_count": map_count,
        "active_seal_id": active,
        "standby_seal_id": standby,
        "retired_seal_ids": [],
        "seal_manifest_sha256": manifest_hashes,
        "allocation_key_sha256": allocation_key_sha256,
        "authorized_open_count": 0,
        "next_sequence": 3,
        "updated_utc": now,
    }


def command_init(args: argparse.Namespace) -> None:
    root = args.root.resolve()
    key_dir = args.key_dir.resolve()
    if (root / "seal-state.json").exists() or (key_dir / "audit-state.json").exists():
        raise SealError("seal state already exists")
    key_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(key_dir, 0o700)
    population = {
        "seed_start": args.seed_start,
        "seed_stop_exclusive": args.seed_stop_exclusive,
    }
    if args.maps * 2 > args.seed_stop_exclusive - args.seed_start:
        raise SealError("population too small for disjoint active and standby sets")
    generator = {
        "kind": "official Java SHA1PRNG port",
        "path": args.generator_path,
        "function": "generate_official(i64)",
        "source_ref": args.generator_ref,
        "source_commit": args.generator_commit,
        "source_sha256": args.generator_sha256,
    }
    now = utc_now()
    active_id = "holdout-001"
    standby_id = "holdout-002"
    allocation_key = secrets.token_bytes(32)
    write_key(key_dir / ALLOCATION_KEY, allocation_key)
    active_key = secrets.token_bytes(32)
    active_seeds = allocation_slice(
        allocation_key,
        args.seed_start,
        args.seed_stop_exclusive,
        args.maps,
        1,
    )
    standby_key = secrets.token_bytes(32)
    standby_seeds = allocation_slice(
        allocation_key,
        args.seed_start,
        args.seed_stop_exclusive,
        args.maps,
        2,
    )

    create_seal(
        root,
        key_dir,
        active_id,
        "active",
        active_key,
        active_seeds,
        1,
        population,
        generator,
        now,
    )
    create_seal(
        root,
        key_dir,
        standby_id,
        "standby",
        standby_key,
        standby_seeds,
        2,
        population,
        generator,
        now,
    )

    manifest_hashes = {
        active_id: sha256_file(seal_manifest_path(root, active_id)),
        standby_id: sha256_file(seal_manifest_path(root, standby_id)),
    }
    state = state_document(
        population,
        args.maps,
        active_id,
        standby_id,
        manifest_hashes,
        sha256_bytes(allocation_key),
        now,
    )
    atomic_write(root / "seal-state.json", canonical_json(state), exclusive=True)
    atomic_write(key_dir / "audit-state.json", canonical_json(state), mode=0o600, exclusive=True)
    print(f"created sealed active {active_id} and disjoint standby {standby_id}; maps={args.maps}")


def git_output(arguments: list[str], *, cwd: Path) -> bytes:
    completed = subprocess.run(["git", *arguments], cwd=cwd, capture_output=True)
    if completed.returncode:
        detail = completed.stderr.decode(errors="replace").strip()
        raise SealError(detail or f"git {' '.join(arguments)} failed")
    return completed.stdout


def repo_relative(path: Path, repo: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError as exc:
        raise SealError(f"{label} must be inside the Git worktree") from exc


def command_prepare_gate(args: argparse.Namespace) -> None:
    root = args.root.resolve()
    state = verify(root, None)
    active = state["active_seal_id"]
    repo = Path(git_output(["rev-parse", "--show-toplevel"], cwd=Path.cwd()).decode().strip())
    baseline = args.baseline.resolve()
    candidate = args.candidate.resolve()
    opponents = args.external_opponents.resolve()
    output = args.output.resolve()
    gate = {
        "schema_version": SCHEMA_VERSION,
        "seal_id": active,
        "holdout_manifest_sha256": sha256_file(seal_manifest_path(root, active)),
        "map_count": state["map_count"],
        "candidate_player_index": 0,
        "baseline_path": repo_relative(baseline, repo, "baseline"),
        "baseline_sha256": sha256_file(baseline),
        "candidate_path": repo_relative(candidate, repo, "candidate"),
        "candidate_sha256": sha256_file(candidate),
        "external_opponents_path": repo_relative(opponents, repo, "external opponents"),
        "external_opponents_sha256": sha256_file(opponents),
        "decision_rule": args.decision_rule,
        "frozen_utc": utc_now(),
    }
    repo_relative(output, repo, "gate manifest")
    atomic_write(output, json.dumps(gate, indent=2, sort_keys=True).encode() + b"\n", exclusive=True)
    print(f"prepared gate manifest for {active}; commit it with both source bytes before open")


def validate_gate(root: Path, gate_path: Path, gate_commit: str) -> dict[str, Any]:
    repo = Path(git_output(["rev-parse", "--show-toplevel"], cwd=Path.cwd()).decode().strip())
    relative_gate = repo_relative(gate_path, repo, "gate manifest")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", gate_commit):
        raise SealError("gate commit must be a full 40-hex commit id")
    git_output(["cat-file", "-e", f"{gate_commit}^{{commit}}"], cwd=repo)
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", gate_commit, "HEAD"], cwd=repo
    )
    if ancestor.returncode:
        raise SealError("gate commit is not an ancestor of the checked-out HEAD")
    committed_gate = git_output(["show", f"{gate_commit}:{relative_gate}"], cwd=repo)
    current_gate = gate_path.read_bytes()
    if committed_gate != current_gate:
        raise SealError("gate manifest bytes are not those at gate commit")
    gate = load_json(gate_path)
    state = load_json(root / "seal-state.json")
    active = state["active_seal_id"]
    manifest_path = seal_manifest_path(root, active)
    required = {
        "schema_version": SCHEMA_VERSION,
        "seal_id": active,
        "holdout_manifest_sha256": sha256_file(manifest_path),
        "map_count": state["map_count"],
        "candidate_player_index": 0,
    }
    for field, expected in required.items():
        if gate.get(field) != expected:
            raise SealError(f"gate field {field} does not match the active seal")
    for field in (
        "baseline_path",
        "baseline_sha256",
        "candidate_path",
        "candidate_sha256",
        "external_opponents_path",
        "external_opponents_sha256",
        "decision_rule",
        "frozen_utc",
    ):
        if not gate.get(field):
            raise SealError(f"gate field {field} is required")
    baseline_bytes = git_output(["show", f"{gate_commit}:{gate['baseline_path']}"], cwd=repo)
    if sha256_bytes(baseline_bytes) != gate["baseline_sha256"]:
        raise SealError("baseline hash does not match gate commit")
    candidate_bytes = git_output(["show", f"{gate_commit}:{gate['candidate_path']}"], cwd=repo)
    if sha256_bytes(candidate_bytes) != gate["candidate_sha256"]:
        raise SealError("candidate hash does not match gate commit")
    opponent_bytes = git_output(
        ["show", f"{gate_commit}:{gate['external_opponents_path']}"], cwd=repo
    )
    if sha256_bytes(opponent_bytes) != gate["external_opponents_sha256"]:
        raise SealError("external-opponent hash does not match gate commit")
    try:
        opponents = json.loads(opponent_bytes)["opponents"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise SealError("external-opponent manifest has no opponent list") from exc
    if not isinstance(opponents, list) or any(not isinstance(row, dict) for row in opponents):
        raise SealError("external-opponent list is invalid")
    identities = [(row.get("name"), row.get("agent_id")) for row in opponents]
    if identities != LOCKED_OPPONENTS:
        raise SealError("external-opponent identities or order differ from the locked set")
    gate["_opponents"] = opponents
    return gate


def command_open(args: argparse.Namespace) -> None:
    root = args.root.resolve()
    key_dir = args.key_dir.resolve()
    state = verify(root, key_dir)
    active = state["active_seal_id"]
    successor = state.get("standby_seal_id")
    if not successor:
        raise SealError("active holdout has no sealed successor; read refused")
    gate = validate_gate(root, args.gate_manifest.resolve(), args.gate_commit)
    reveal_path = args.reveal_path.resolve()
    if reveal_path.exists():
        raise SealError(f"refusing to overwrite reveal path {reveal_path}")
    receipt_path = root / "receipts" / f"{active}.json"
    if receipt_path.exists():
        raise SealError(f"authorized receipt already exists for {active}")

    lock_path = key_dir / f".opened-{active}.lock"
    lock_value = canonical_json(
        {"seal_id": active, "gate_commit": args.gate_commit, "opened_utc": utc_now()}
    )
    atomic_write(lock_path, lock_value, mode=0o600, exclusive=True)
    payload = decrypt_payload(root, key_dir, active)
    opponents = gate.pop("_opponents")
    blocks = [
        {
            "opponent": opponents[index % len(opponents)]["name"],
            "opponent_agent": opponents[index % len(opponents)]["agent_id"],
            "seed": seed,
        }
        for index, seed in enumerate(payload["seeds"])
    ]
    reveal = {
        "schema_version": SCHEMA_VERSION,
        "seal_id": active,
        "map_count": len(blocks),
        "assignment": "encrypted seed-list order round-robin over locked opponent order",
        "blocks": blocks,
    }
    reveal_bytes = canonical_json(reveal)
    atomic_write(reveal_path, reveal_bytes, exclusive=True)

    now = utc_now()
    retired = list(state["retired_seal_ids"])
    retired.append(active)
    state.update(
        {
            "active_seal_id": successor,
            "standby_seal_id": None,
            "retired_seal_ids": retired,
            "authorized_open_count": state["authorized_open_count"] + 1,
            "updated_utc": now,
        }
    )
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "seal_id": active,
        "opened_utc": now,
        "gate_commit": args.gate_commit,
        "gate_manifest_sha256": sha256_file(args.gate_manifest.resolve()),
        "decision_rule": gate["decision_rule"],
        "sealed_payload_sha256": sha256_bytes(canonical_json(payload)),
        "reveal_sha256": sha256_bytes(reveal_bytes),
        "retired_to_development": True,
        "reveal_path": str(reveal_path),
        "successor_activated": successor,
    }
    retirements_path = root / "development-retirements.json"
    if retirements_path.exists():
        retirements = load_json(retirements_path)
    else:
        retirements = {"schema_version": SCHEMA_VERSION, "retirements": []}
    retirements["retirements"].append(receipt)
    atomic_write(root / "seal-state.json", canonical_json(state))
    atomic_write(key_dir / "audit-state.json", canonical_json(state), mode=0o600)
    atomic_write(receipt_path, canonical_json(receipt), exclusive=True)
    atomic_write(retirements_path, canonical_json(retirements))
    print(f"authorized one-time read retired {active}; activated {successor}; standby required")


def command_add_standby(args: argparse.Namespace) -> None:
    root = args.root.resolve()
    key_dir = args.key_dir.resolve()
    state = verify(root, key_dir)
    if state.get("standby_seal_id"):
        raise SealError("a sealed standby already exists")
    sequence = state["next_sequence"]
    seal_id = f"holdout-{sequence:03d}"
    population = state["population"]
    allocation_key = read_key(key_dir / ALLOCATION_KEY)
    if sha256_bytes(allocation_key) != state["allocation_key_sha256"]:
        raise SealError("allocation-key commitment mismatch")
    key = secrets.token_bytes(32)
    seeds = allocation_slice(
        allocation_key,
        population["seed_start"],
        population["seed_stop_exclusive"],
        state["map_count"],
        sequence,
    )
    generator = load_manifest(root, state["active_seal_id"])["generator"]
    create_seal(
        root,
        key_dir,
        seal_id,
        "standby",
        key,
        seeds,
        sequence,
        population,
        generator,
        utc_now(),
    )
    state["standby_seal_id"] = seal_id
    state["seal_manifest_sha256"][seal_id] = sha256_file(seal_manifest_path(root, seal_id))
    state["next_sequence"] = sequence + 1
    state["updated_utc"] = utc_now()
    atomic_write(root / "seal-state.json", canonical_json(state))
    atomic_write(key_dir / "audit-state.json", canonical_json(state), mode=0o600)
    print(f"created disjoint sealed standby {seal_id}; maps={state['map_count']}")


def command_verify(args: argparse.Namespace) -> None:
    state = verify(args.root.resolve(), args.key_dir.resolve() if args.key_dir else None)
    private = " and private audit/HMAC" if args.key_dir else ""
    print(
        f"verified ciphertext{private}; active={state['active_seal_id']}; "
        f"standby={state.get('standby_seal_id')}; authorized_opens={state['authorized_open_count']}"
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="draw encrypted active and standby holdouts")
    init.add_argument("--root", type=Path, required=True)
    init.add_argument("--key-dir", type=Path, required=True)
    init.add_argument("--seed-start", type=int, required=True)
    init.add_argument("--seed-stop-exclusive", type=int, required=True)
    init.add_argument("--maps", type=int, required=True)
    init.add_argument("--generator-path", required=True)
    init.add_argument("--generator-ref", required=True)
    init.add_argument("--generator-commit", required=True)
    init.add_argument("--generator-sha256", required=True)
    init.set_defaults(handler=command_init)

    verify_parser = commands.add_parser("verify", help="check seal without decrypting it")
    verify_parser.add_argument("--root", type=Path, required=True)
    verify_parser.add_argument("--key-dir", type=Path)
    verify_parser.set_defaults(handler=command_verify)

    prepare = commands.add_parser(
        "prepare-gate", help="write the manifest that freezes sources and decision rule"
    )
    prepare.add_argument("--root", type=Path, required=True)
    prepare.add_argument("--baseline", type=Path, required=True)
    prepare.add_argument("--candidate", type=Path, required=True)
    prepare.add_argument("--external-opponents", type=Path, required=True)
    prepare.add_argument("--decision-rule", required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.set_defaults(handler=command_prepare_gate)

    open_parser = commands.add_parser("open", help="perform the single authorized gate read")
    open_parser.add_argument("--root", type=Path, required=True)
    open_parser.add_argument("--key-dir", type=Path, required=True)
    open_parser.add_argument("--gate-manifest", type=Path, required=True)
    open_parser.add_argument("--gate-commit", required=True)
    open_parser.add_argument("--reveal-path", type=Path, required=True)
    open_parser.set_defaults(handler=command_open)

    standby = commands.add_parser("add-standby", help="draw the successor required for next read")
    standby.add_argument("--root", type=Path, required=True)
    standby.add_argument("--key-dir", type=Path, required=True)
    standby.set_defaults(handler=command_add_standby)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        args.handler(args)
    except (SealError, KeyError, OSError) as exc:
        print(f"seal error: {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
