# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict
from xml.parsers.expat import ParserCreate


class SVGUtils:
    SVG_DEFAULT_ATTRIBUTES: Dict[str, str] = {
        "fill": "black",
        "fill-opacity": "1",
        "stroke": "none",
        "stroke-opacity": "1",
    }

    def __init__(self) -> None:
        pass

    def parse_color_string(self, color_spec: str) -> str:
        # copied from Manim's SVG parser.
        if color_spec[0:3] == "rgb":
            # these are only in integer form,
            # but the Colour module wants them in floats.
            splits = color_spec[4:-1].split(",")
            if splits[0][-1] == "%":
                # if the last character of the first number is a percentage,
                # then interpret the number as a percentage
                parsed_rgbs = [float(i[:-1]) / 100.0 for i in splits]
            else:
                parsed_rgbs = [int(i) / 255.0 for i in splits]

            # hex_color = rgb_to_hex(parsed_rgbs)

        else:
            # not necessary for web2hex case and hex
            raise NotImplementedError

        return parsed_rgbs

    def str2styledict(self, style_specs: str) -> Dict[str, str]:
        # helper for parse style
        # copied from manim's svg parser.
        style = {}

        # the style attribute should be handled separately in order to
        # break it up nicely. furthermore, style takes priority over other
        # attributes in the same element.
        if style_specs:
            for style_spec in style_specs.split(";"):
                try:
                    key, value = style_spec.split(":")
                except ValueError as e:
                    if not style_spec:
                        # there was just a stray semicolon
                        # at the end, producing an
                        # emptystring
                        pass
                    else:
                        raise e
                else:
                    style[key] = value

        return style

    def parse_style(self, stylestr: str) -> Dict:
        # Originally written by @MrMallIronmaker
        # Copied from Manim.
        # https://github.com/ManimCommunity/manim/
        # blob/aa873e0f8e5c4f35c864568213b04b88af5b4769/manim/mobject/svg/style_utils.py#L143
        SVG_DEFAULT_ATTRIBUTES = self.SVG_DEFAULT_ATTRIBUTES
        manim_style = {}
        svg_style = self.str2styledict(stylestr)
        for key in SVG_DEFAULT_ATTRIBUTES:
            if key not in svg_style:
                svg_style[key] = SVG_DEFAULT_ATTRIBUTES[key]

        if "fill-opacity" in svg_style:
            manim_style["fill_opacity"] = float(svg_style["fill-opacity"])

        if "stroke-opacity" in svg_style:
            manim_style["stroke_opacity"] = float(svg_style["stroke-opacity"])

        # nones need to be handled specially
        if "fill" in svg_style:
            if svg_style["fill"] == "none":
                manim_style["fill_opacity"] = 0
            else:
                manim_style["fill_color"] = self.parse_color_string(svg_style["fill"])

        if "stroke" in svg_style:
            if svg_style["stroke"] == "none":
                # In order to not break animations.creation.Write,
                # we interpret no stroke as stroke-width of zero and
                # color the same as the fill color, if it exists.
                manim_style["stroke_width"] = 0
                if "fill_color" in manim_style:
                    manim_style["stroke_color"] = manim_style["fill_color"]
            else:
                manim_style["stroke_color"] = self.parse_color_string(
                    svg_style["stroke"]
                )

        return manim_style


class SVGStyleTester(SVGUtils):
    def __init__(self, gotSVG: Path, expectedSVG: Path) -> None:
        self.expected_file = expectedSVG
        self.got_file = gotSVG
        self.prepare()

    def get_handler(self, final_setter):
        def func(name, attrs):
            styles = []
            if name == "g":
                if "style" in attrs:
                    styles.append(self.parse_style(attrs["style"]))
            if styles:
                # need to think of better way than this.
                exec(f"self.{final_setter} += [styles]")

        return func

    def prepare(self):
        self.got_svg_style = []
        self.expected_svg_style = []
        got_parser = ParserCreate()
        got_parser.StartElementHandler = self.get_handler("got_svg_style")
        with open(self.got_file, "rb") as f:
            got_parser.ParseFile(f)

        expected_parser = ParserCreate()
        expected_parser.StartElementHandler = self.get_handler("expected_svg_style")
        with open(self.expected_file, "rb") as f:
            expected_parser.ParseFile(f)
