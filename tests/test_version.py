"""Tests for version info — v2 API."""

import manimpango


class TestVersionInfo:
    def test_get_version_info_keys(self):
        info = manimpango.get_version_info()
        assert "manimpango" in info
        assert "pango" in info
        assert "cairo" in info

    def test_get_version_info_types(self):
        info = manimpango.get_version_info()
        for key, value in info.items():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_pango_version_format(self):
        info = manimpango.get_version_info()
        parts = info["pango"].split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts)

    def test_cairo_version_format(self):
        info = manimpango.get_version_info()
        parts = info["cairo"].split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts)

    def test_manimpango_version_matches(self):
        info = manimpango.get_version_info()
        assert info["manimpango"] == manimpango.__version__

    def test_pango_version_minimum(self):
        """Pango >= 1.44 is required."""
        info = manimpango.get_version_info()
        parts = info["pango"].split(".")
        major, minor = int(parts[0]), int(parts[1])
        assert (major, minor) >= (1, 44)


class TestBackwardsCompatVersionFunctions:
    def test_pango_version(self):
        v = manimpango.pango_version()
        assert isinstance(v, str)
        assert v == manimpango.get_version_info()["pango"]

    def test_cairo_version(self):
        v = manimpango.cairo_version()
        assert isinstance(v, str)
        assert v == manimpango.get_version_info()["cairo"]
