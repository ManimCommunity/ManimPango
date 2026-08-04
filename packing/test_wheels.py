"""Smoke-test an installed ManimPango wheel outside the source package."""

from __future__ import annotations

from pathlib import Path

import manimpango


def main() -> None:
    result = manimpango.render("Wheel smoke test", disable_ligatures=True)
    if not result.svg or result.width <= 0 or result.height <= 0:
        raise RuntimeError("installed wheel did not render text")

    font_path = Path(__file__).parents[1] / "tests" / "fonts" / "BungeeOutline-Regular.ttf"
    with manimpango.register_font(font_path):
        if "Bungee Outline" not in manimpango.list_fonts():
            raise RuntimeError("installed wheel did not expose a registered font")


if __name__ == "__main__":
    main()
