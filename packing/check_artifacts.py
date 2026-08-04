"""Assert that distributable artifacts carry the required license notices."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

REQUIRED_NOTICE_PATHS = ("LICENSE", "packing/LICENSE.bin")


def collect_artifacts(paths: list[Path]) -> list[Path]:
    """Expand artifact directories without relying on the invoking shell."""
    artifacts: list[Path] = []
    for path in paths:
        if path.is_dir():
            artifacts.extend(sorted(path.glob("*.whl")))
            artifacts.extend(sorted(path.glob("*.tar.gz")))
        else:
            artifacts.append(path)
    return artifacts


def artifact_paths(artifact: Path) -> set[str]:
    if artifact.suffix == ".whl":
        with zipfile.ZipFile(artifact) as archive:
            return set(archive.namelist())
    if artifact.name.endswith(".tar.gz"):
        with tarfile.open(artifact) as archive:
            return set(archive.getnames())
    raise ValueError(f"unsupported artifact: {artifact}")


def assert_required_notices(artifact: Path) -> None:
    paths = artifact_paths(artifact)
    for notice in REQUIRED_NOTICE_PATHS:
        has_notice = any(
            path.endswith(f"/licenses/{notice}") or path.endswith(f"/{notice}")
            for path in paths
        )
        if not has_notice:
            raise RuntimeError(f"{artifact.name} does not include {notice}")


def main() -> None:
    artifacts = collect_artifacts([Path(argument) for argument in sys.argv[1:]])
    if not artifacts:
        raise SystemExit("usage: check_artifacts.py ARTIFACT_OR_DIRECTORY [...]")
    for artifact in artifacts:
        assert_required_notices(artifact)


if __name__ == "__main__":
    main()
