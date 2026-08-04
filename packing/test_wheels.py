"""Smoke-test an installed ManimPango wheel outside the source package."""

from __future__ import annotations

from pathlib import Path

import manimpango


def main() -> None:
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
