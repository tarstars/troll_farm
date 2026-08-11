from pathlib import Path
from types import SimpleNamespace

import pytest

from cgauto.check_external_storage import (
    DEFAULT_SCRATCH_ROOTS,
    DEFAULT_LOGICAL_ROOTS,
    StoragePreflightError,
    validate_layout,
)


def _label_medium_data(_path: Path) -> str:
    return "medium_data"


def _disk_usage(free: int = 50 * 1024**3) -> SimpleNamespace:
    return SimpleNamespace(total=100 * 1024**3, used=50 * 1024**3, free=free)


def _valid_layout(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    mount = tmp_path / "mounted-medium-data"
    project = mount / "database" / "troll_farm"
    repo.mkdir()
    project.mkdir(parents=True)
    for relative in DEFAULT_LOGICAL_ROOTS:
        target = project / relative
        target.mkdir(parents=True)
        logical = repo / relative
        logical.parent.mkdir(parents=True, exist_ok=True)
        logical.symlink_to(target, target_is_directory=True)
    return repo, mount


def test_valid_layout_accepts_only_external_backed_links(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)
    result = validate_layout(
        repo_root=repo,
        mount_point=mount,
        label="medium_data",
        required_free_bytes=10 * 1024**3,
        label_for_path=_label_medium_data,
        disk_usage=lambda _path: _disk_usage(),
    )
    assert result["ok"] is True
    assert result["free_bytes"] == 50 * 1024**3
    assert set(result["links"]) == {str(path) for path in DEFAULT_LOGICAL_ROOTS}


def test_real_directory_fails_closed(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)
    logical = repo / "outputs"
    logical.unlink()
    logical.mkdir()

    with pytest.raises(StoragePreflightError, match="is not a symlink"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(),
        )


def test_link_outside_project_root_fails_closed(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    logical = repo / "artifacts"
    logical.unlink()
    logical.symlink_to(outside, target_is_directory=True)

    with pytest.raises(StoragePreflightError, match="escapes physical project root"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(),
        )


def test_insufficient_free_space_fails_closed(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)

    with pytest.raises(StoragePreflightError, match="insufficient free space"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            required_free_bytes=10 * 1024**3,
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(free=5 * 1024**3),
        )


def _scratch(tmp_path: Path, repo: Path, writable: bool = True) -> None:
    """Give the repo the two local scratch roots the cloud archive cannot host."""
    for relative in DEFAULT_SCRATCH_ROOTS:
        target = tmp_path / "scratch" / relative
        target.mkdir(parents=True)
        if not writable:
            target.chmod(0o500)
        logical = repo / relative
        logical.parent.mkdir(parents=True, exist_ok=True)
        logical.symlink_to(target, target_is_directory=True)


def test_read_only_backend_blocks_write_intent(tmp_path: Path) -> None:
    """A read-only cloud mount must never hand a PASS to a caller about to write."""
    repo, mount = _valid_layout(tmp_path)

    with pytest.raises(StoragePreflightError, match="read-only; bulk writes are blocked"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(),
            writable=False,
            intent="write",
        )


def test_read_only_backend_satisfies_read_intent(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)
    result = validate_layout(
        repo_root=repo,
        mount_point=mount,
        label="medium_data",
        required_free_bytes=10 * 1024**3,
        label_for_path=_label_medium_data,
        disk_usage=lambda _path: _disk_usage(),
        writable=False,
        intent="read",
    )
    assert result["ok"] is True
    assert result["writable"] is False
    # Object storage reports a fictitious free figure; the threshold must not be applied.
    assert result["free_bytes"] is None


def test_scratch_root_must_be_writable(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)
    _scratch(tmp_path, repo, writable=False)

    with pytest.raises(StoragePreflightError, match="not writable"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            scratch_roots=DEFAULT_SCRATCH_ROOTS,
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(),
        )


def test_scratch_roots_may_live_outside_the_project_root(tmp_path: Path) -> None:
    """Scratch is local by design — it must not be judged against the archive root."""
    repo, mount = _valid_layout(tmp_path)
    _scratch(tmp_path, repo)

    result = validate_layout(
        repo_root=repo,
        mount_point=mount,
        label="medium_data",
        scratch_roots=DEFAULT_SCRATCH_ROOTS,
        label_for_path=_label_medium_data,
        disk_usage=lambda _path: _disk_usage(),
    )
    assert result["ok"] is True
    assert set(result["scratch"]) == {str(path) for path in DEFAULT_SCRATCH_ROOTS}


def test_missing_scratch_root_fails_closed(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)

    with pytest.raises(StoragePreflightError, match="scratch root is missing"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            scratch_roots=DEFAULT_SCRATCH_ROOTS,
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(),
        )


def _union(tmp_path: Path, repo: Path, writable: bool = True) -> None:
    """Point the logical roots at real LOCAL directories, as the union model requires."""
    for relative in DEFAULT_LOGICAL_ROOTS:
        target = tmp_path / "local" / relative
        target.mkdir(parents=True)
        if not writable:
            target.chmod(0o500)
        logical = repo / relative
        if logical.is_symlink():
            logical.unlink()
        logical.parent.mkdir(parents=True, exist_ok=True)
        logical.symlink_to(target, target_is_directory=True)


def test_union_roots_allow_writes_over_a_read_only_backend(tmp_path: Path) -> None:
    """The whole point of the union: the mount is read-only, writing still works."""
    repo, mount = _valid_layout(tmp_path)
    _union(tmp_path, repo)

    result = validate_layout(
        repo_root=repo,
        mount_point=mount,
        label="medium_data",
        union_roots=True,
        label_for_path=_label_medium_data,
        disk_usage=lambda _path: _disk_usage(),
        writable=False,
        intent="write",
    )
    assert result["ok"] is True


def test_union_root_that_is_not_writable_fails_closed(tmp_path: Path) -> None:
    repo, mount = _valid_layout(tmp_path)
    _union(tmp_path, repo, writable=False)

    with pytest.raises(StoragePreflightError, match="union root is not writable"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            union_roots=True,
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(),
            writable=False,
            intent="write",
        )


def test_union_free_space_is_measured_on_the_local_root(tmp_path: Path) -> None:
    """Free space must be checked where the bytes land, not on the read-only mount.

    Without this the threshold silently could not fail: the mount's branch sets
    free_bytes=None for a read-only backend.
    """
    repo, mount = _valid_layout(tmp_path)
    _union(tmp_path, repo)

    with pytest.raises(StoragePreflightError, match="insufficient free space at"):
        validate_layout(
            repo_root=repo,
            mount_point=mount,
            label="medium_data",
            union_roots=True,
            required_free_bytes=10 * 1024**3,
            label_for_path=_label_medium_data,
            disk_usage=lambda _path: _disk_usage(free=5 * 1024**3),
            writable=False,
            intent="write",
        )
