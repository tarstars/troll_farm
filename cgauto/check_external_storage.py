#!/usr/bin/env python3
"""Fail-closed preflight for Troll Farm's external-backed bulk roots."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LABEL = "medium_data"
DEFAULT_PROJECT_RELATIVE = Path("database/troll_farm")
# Spec Phase 4: the bulk roots may be backed either by the USB (ext4, label above) or by
# a GeeseFS mount of the archive prefix. The cloud mount is deliberately read-only, so it
# satisfies reads and cannot satisfy a bulk write — this preflight must say so rather than
# report a cheerful PASS to a caller that is about to write.
DEFAULT_BUCKET_SOURCE = "troll-farm-data:archive"
# Archive-backed roots: their contents live on the bulk backend (USB, or the read-only
# cloud mirror of it) and must resolve beneath the physical project root.
DEFAULT_LOGICAL_ROOTS = (
    Path("artifacts"),
    Path("outputs"),
    Path("data/external"),
)
# Scratch roots: write targets that held ZERO files on the USB (verified at the Phase 3
# upload — the whole drive was 3,483 files and none were under these two). They were only
# on the drive to keep bulk off the SSD. A read-only archive is the wrong home for a write
# target, so as of 2026-08-11 they point at local disk and are validated as writable
# directories rather than as archive-backed links.
DEFAULT_SCRATCH_ROOTS = (
    Path("yt_work"),
    Path("data/generated"),
)


class StoragePreflightError(RuntimeError):
    """The external storage layout is not safe for a bulk write."""


def _run_findmnt(arguments: Sequence[str]) -> list[str]:
    completed = subprocess.run(
        ["findmnt", "-rn", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or f"exit {completed.returncode}"
        raise StoragePreflightError(f"findmnt failed: {detail}")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def find_mount_for_label(label: str) -> Path:
    mounts = _run_findmnt(["-S", f"LABEL={label}", "-o", "TARGET"])
    if not mounts:
        raise StoragePreflightError(
            f"no mounted filesystem with label {label!r}; bulk writes are blocked"
        )
    if len(mounts) != 1:
        raise StoragePreflightError(
            f"expected one mount for label {label!r}, found {len(mounts)}: {mounts}"
        )
    return Path(mounts[0])


def filesystem_label(path: Path) -> str:
    labels = _run_findmnt(["-T", str(path), "-o", "LABEL"])
    if len(labels) != 1 or not labels[0]:
        raise StoragePreflightError(f"cannot establish filesystem label for {path}")
    return labels[0]


def mount_source(path: Path) -> str:
    """The mount SOURCE covering `path` — a GeeseFS mount's identity, e.g. bucket:prefix."""
    sources = _run_findmnt(["-T", str(path), "-o", "SOURCE"])
    if len(sources) != 1 or not sources[0]:
        raise StoragePreflightError(f"cannot establish mount source for {path}")
    return sources[0]


def mount_is_readonly(path: Path) -> bool:
    options = _run_findmnt(["-T", str(path), "-o", "OPTIONS"])
    if len(options) != 1 or not options[0]:
        raise StoragePreflightError(f"cannot establish mount options for {path}")
    return "ro" in options[0].split(",")


def find_bucket_mount(source: str) -> Path:
    targets = _run_findmnt(["-S", source, "-o", "TARGET"])
    if not targets:
        raise StoragePreflightError(
            f"no mounted filesystem with source {source!r}; bulk roots are unavailable"
        )
    if len(targets) != 1:
        raise StoragePreflightError(
            f"expected one mount for source {source!r}, found {len(targets)}: {targets}"
        )
    return Path(targets[0])


def _beneath(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_layout(
    *,
    repo_root: Path,
    mount_point: Path,
    label: str,
    project_relative: Path = DEFAULT_PROJECT_RELATIVE,
    logical_roots: Sequence[Path] = DEFAULT_LOGICAL_ROOTS,
    scratch_roots: Sequence[Path] = (),
    required_free_bytes: int = 0,
    label_for_path: Callable[[Path], str] = filesystem_label,
    disk_usage: Callable[[Path], Any] = shutil.disk_usage,
    writable: bool = True,
    intent: str = "write",
) -> dict[str, Any]:
    """Validate a discovered mount and all external-backed repository links.

    `writable` describes the backing store; `intent` describes the caller. A read-only
    store satisfies `intent="read"` and can never satisfy `intent="write"` — reporting
    otherwise would hand a PASS to a bulk write that is about to fail partway through.
    """
    errors: list[str] = []
    links: dict[str, str] = {}
    scratch: dict[str, str] = {}

    if required_free_bytes < 0:
        raise ValueError("required_free_bytes must be non-negative")
    if intent not in ("read", "write"):
        raise ValueError(f"intent must be 'read' or 'write', got {intent!r}")
    if intent == "write" and not writable:
        errors.append(
            f"backing store at {mount_point} is read-only; bulk writes are blocked"
        )
    if not mount_point.is_dir():
        errors.append(f"mount point is not a directory: {mount_point}")
    else:
        try:
            actual_label = label_for_path(mount_point)
        except StoragePreflightError as error:
            errors.append(str(error))
        else:
            if actual_label != label:
                errors.append(
                    f"mount label mismatch for {mount_point}: "
                    f"expected {label!r}, got {actual_label!r}"
                )

    project_root = mount_point / project_relative
    if not project_root.is_dir():
        errors.append(f"physical project root is unavailable: {project_root}")
        resolved_project_root = project_root
        free_bytes = None
    elif not writable:
        # Object storage reports a fictitious free-space figure (geesefs says 1 PiB), so
        # comparing it to a threshold would be theatre. Nothing is written here anyway.
        resolved_project_root = project_root.resolve(strict=True)
        free_bytes = None
    else:
        resolved_project_root = project_root.resolve(strict=True)
        usage = disk_usage(resolved_project_root)
        free_bytes = int(usage.free)
        if free_bytes < required_free_bytes:
            errors.append(
                f"insufficient free space: need {required_free_bytes} bytes, "
                f"found {free_bytes}"
            )

    for relative in logical_roots:
        logical = repo_root / relative
        if not logical.is_symlink():
            errors.append(f"required logical root is not a symlink: {logical}")
            continue
        try:
            target = logical.resolve(strict=True)
        except FileNotFoundError:
            errors.append(f"logical root has a missing target: {logical}")
            continue
        links[str(relative)] = str(target)
        if not _beneath(target, resolved_project_root):
            errors.append(
                f"logical root escapes physical project root: {logical} -> {target}"
            )
            continue
        try:
            target_label = label_for_path(target)
        except StoragePreflightError as error:
            errors.append(str(error))
        else:
            if target_label != label:
                errors.append(
                    f"target label mismatch for {logical}: "
                    f"expected {label!r}, got {target_label!r}"
                )

    for relative in scratch_roots:
        logical = repo_root / relative
        if not logical.is_symlink() and not logical.is_dir():
            errors.append(f"scratch root is missing: {logical}")
            continue
        try:
            target = logical.resolve(strict=True)
        except FileNotFoundError:
            errors.append(f"scratch root has a missing target: {logical}")
            continue
        if not target.is_dir():
            errors.append(f"scratch root is not a directory: {logical} -> {target}")
            continue
        if not os.access(target, os.W_OK):
            errors.append(f"scratch root is not writable: {logical} -> {target}")
            continue
        scratch[str(relative)] = str(target)

    result = {
        "ok": not errors,
        "label": label,
        "scratch": scratch,
        "mount_point": str(mount_point),
        "project_root": str(project_root),
        "required_free_bytes": required_free_bytes,
        "free_bytes": free_bytes,
        "links": links,
        "writable": writable,
        "intent": intent,
        "errors": errors,
    }
    if errors:
        raise StoragePreflightError("\n".join(errors))
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument(
        "--project-relative", type=Path, default=DEFAULT_PROJECT_RELATIVE
    )
    parser.add_argument(
        "--root",
        action="append",
        dest="logical_roots",
        type=Path,
        help="required repo-relative logical root; repeat to override defaults",
    )
    parser.add_argument("--required-free-gib", type=float, default=0.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--bucket-source", default=DEFAULT_BUCKET_SOURCE)
    parser.add_argument(
        "--intent",
        choices=("read", "write"),
        default="write",
        help="what the caller is about to do; 'write' fails closed on a read-only backing "
        "store. Default stays 'write' so existing callers keep their guarantee.",
    )
    return parser.parse_args(argv)


def discover_backend(label: str, bucket_source: str) -> dict[str, Any]:
    """Find whichever bulk backend is present: the USB first, else the cloud mount.

    The USB wins when both are somehow present, because it is writable and local.
    """
    try:
        mount_point = find_mount_for_label(label)
    except StoragePreflightError as usb_error:
        try:
            mount_point = find_bucket_mount(bucket_source)
        except StoragePreflightError as cloud_error:
            raise StoragePreflightError(
                f"no bulk backend available.\n  USB:   {usb_error}\n  cloud: {cloud_error}"
            ) from cloud_error
        return {
            "kind": "geesefs",
            "mount_point": mount_point,
            # The cloud mount IS the project root; the USB nests it under database/troll_farm.
            "project_relative": Path("."),
            "identity": bucket_source,
            "identity_for_path": mount_source,
            "writable": not mount_is_readonly(mount_point),
        }
    return {
        "kind": "ext4",
        "mount_point": mount_point,
        "project_relative": DEFAULT_PROJECT_RELATIVE,
        "identity": label,
        "identity_for_path": filesystem_label,
        "writable": not mount_is_readonly(mount_point),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.required_free_gib < 0:
        raise SystemExit("--required-free-gib must be non-negative")
    required_free_bytes = int(args.required_free_gib * (1024**3))
    logical_roots = tuple(args.logical_roots or DEFAULT_LOGICAL_ROOTS)
    try:
        backend = discover_backend(args.label, args.bucket_source)
        project_relative = (
            args.project_relative
            if args.project_relative != DEFAULT_PROJECT_RELATIVE
            else backend["project_relative"]
        )
        result = validate_layout(
            repo_root=args.repo_root.resolve(),
            mount_point=backend["mount_point"],
            label=backend["identity"],
            project_relative=project_relative,
            logical_roots=logical_roots,
            scratch_roots=DEFAULT_SCRATCH_ROOTS,
            required_free_bytes=required_free_bytes,
            label_for_path=backend["identity_for_path"],
            writable=backend["writable"],
            intent=args.intent,
        )
        result["backend"] = backend["kind"]
    except StoragePreflightError as error:
        if args.json:
            print(json.dumps({"ok": False, "error": str(error)}, indent=2))
        else:
            print(f"storage preflight: FAIL\n{error}")
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("storage preflight: PASS")
        print(f"backend: {result.get('backend')} ({'writable' if result['writable'] else 'READ-ONLY'})")
        print(f"identity: {result['label']}")
        print(f"mount: {result['mount_point']}")
        print(f"project: {result['project_root']}")
        print(f"free bytes: {result['free_bytes']}")
        for logical, target in result["links"].items():
            print(f"{logical} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
