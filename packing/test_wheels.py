"""Smoke-test a repaired ManimPango wheel outside the build environment."""

from __future__ import annotations

import ntpath
import os
import subprocess
import sys
from importlib.metadata import Distribution, distribution
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1].resolve()
WINDOWS_VENDOR_BIN = r"C:\cibw\vendor\bin"
MACOS_VENDOR_ROOT = "/Users/runner/pangobuild"


def _remove_windows_path_entry(path: str, entry: str) -> str:
    """Return a Windows PATH value without one normalized entry."""
    normalized_entry = ntpath.normcase(ntpath.normpath(entry))
    return ";".join(
        candidate
        for candidate in path.split(";")
        if ntpath.normcase(ntpath.normpath(candidate)) != normalized_entry
    )


def _sanitize_library_search_path(platform: str | None = None) -> None:
    """Remove build-time vendor locations before loading the installed wheel."""
    platform = platform or sys.platform
    if platform == "win32":
        os.environ["PATH"] = _remove_windows_path_entry(
            os.environ.get("PATH", ""), WINDOWS_VENDOR_BIN
        )
    elif platform == "darwin":
        os.environ.pop("DYLD_LIBRARY_PATH", None)
        os.environ.pop("DYLD_FALLBACK_LIBRARY_PATH", None)


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory)
    except ValueError:
        return False
    return True


def _bundled_libraries(installed_distribution: Distribution) -> list[Path]:
    """List bundled dynamic libraries carried by the installed wheel."""
    files = installed_distribution.files or ()
    return [
        installed_distribution.locate_file(file)
        for file in files
        if file.suffix.lower() in {".dll", ".dylib"}
    ]


def _native_binaries(installed_distribution: Distribution) -> list[Path]:
    """List native extension and library files carried by the wheel."""
    files = installed_distribution.files or ()
    return [
        installed_distribution.locate_file(file)
        for file in files
        if file.suffix.lower() in {".dll", ".dylib", ".pyd", ".so"}
    ]


def _verify_macos_dependencies(binaries: list[Path]) -> None:
    """Reject macOS extensions still linked to the build-time Pango prefix."""
    for binary in binaries:
        dependencies = subprocess.run(
            ["otool", "-L", str(binary)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if MACOS_VENDOR_ROOT in dependencies:
            raise RuntimeError(
                f"installed wheel still links {binary.name} to {MACOS_VENDOR_ROOT}"
            )


def _import_installed_wheel() -> tuple[object, list[Path]]:
    """Import the wheel only after its build-time loader paths were removed."""
    _sanitize_library_search_path()

    import manimpango

    module_path = Path(manimpango.__file__).resolve()
    if _is_within(module_path, PROJECT_ROOT):
        raise RuntimeError("wheel smoke test imported ManimPango from the source tree")

    installed_distribution = distribution("ManimPango")
    libraries = _bundled_libraries(installed_distribution)
    if not libraries:
        raise RuntimeError("installed wheel does not contain bundled native libraries")
    if sys.platform == "darwin":
        _verify_macos_dependencies(_native_binaries(installed_distribution))
    return manimpango, libraries


def main() -> None:
    manimpango, _ = _import_installed_wheel()
    fallback = manimpango.render(
        "Wheel custom-font smoke test", font="Sans", disable_ligatures=True
    )
    if not fallback.svg or fallback.width <= 0 or fallback.height <= 0:
        raise RuntimeError("installed wheel did not render text")

    font_path = (
        Path(__file__).parents[1] / "tests" / "fonts" / "BungeeOutline-Regular.ttf"
    )
    with manimpango.register_font(font_path):
        if "Bungee Outline" not in manimpango.list_fonts():
            raise RuntimeError("installed wheel did not expose a registered font")
        custom = manimpango.render(
            "Wheel custom-font smoke test",
            font="Bungee Outline",
            disable_ligatures=True,
        )
        if not custom.svg or custom.width <= 0 or custom.height <= 0:
            raise RuntimeError(
                "installed wheel did not render with the registered font"
            )
        if custom.svg == fallback.svg:
            raise RuntimeError(
                "installed wheel rendered the registered font as the Sans fallback"
            )


if __name__ == "__main__":
    main()
