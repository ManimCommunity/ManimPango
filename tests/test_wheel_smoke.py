"""Unit tests for the wheel smoke-test environment guards."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


def _load_wheel_smoke_module():
    path = Path(__file__).parents[1] / "packing" / "test_wheels.py"
    spec = importlib.util.spec_from_file_location("wheel_smoke", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


wheel_smoke = _load_wheel_smoke_module()


def test_remove_windows_path_entry_is_case_insensitive() -> None:
    path = r"C:\Python;C:\CIBW\VENDOR\bin;C:\Windows\System32"

    sanitized = wheel_smoke._remove_windows_path_entry(path, r"c:\cibw\vendor\bin")

    assert sanitized == r"C:\Python;C:\Windows\System32"


def test_sanitize_macos_loader_variables(monkeypatch) -> None:
    monkeypatch.setenv("DYLD_LIBRARY_PATH", "/build/vendor/lib")
    monkeypatch.setenv("DYLD_FALLBACK_LIBRARY_PATH", "/build/vendor/lib")

    wheel_smoke._sanitize_library_search_path("darwin")

    assert "DYLD_LIBRARY_PATH" not in os.environ
    assert "DYLD_FALLBACK_LIBRARY_PATH" not in os.environ
