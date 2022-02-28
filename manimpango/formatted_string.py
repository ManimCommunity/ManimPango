from typing import Any, Union
import copy
import re
import xml.sax.saxutils as saxutils


class FormattedString:
    # See https://docs.gtk.org/Pango/pango_markup.html
    # A tag containing two aliases will cause warning,
    # so only use the first key of each group of aliases.
    SPAN_ATTR_KEY_ALIAS_LIST = (
        ("font", "font_desc"),
        ("font_family", "face"),
        ("font_size", "size"),
        ("font_style", "style"),
        ("font_weight", "weight"),
        ("font_variant", "variant"),
        ("font_stretch", "stretch"),
        ("font_features",),
        ("foreground", "fgcolor", "color"),
        ("background", "bgcolor"),
        ("alpha", "fgalpha"),
        ("background_alpha", "bgalpha"),
        ("underline", "underline_color"),
        ("overline", "overline_color"),
        ("rise",),
        ("baseline_shift",),
        ("font_scale",),
        ("strikethrough",),
        ("strikethrough_color",),
        ("fallback",),
        ("lang",),
        ("letter_spacing",),
        ("gravity",),
        ("gravity_hint",),
        ("show",),
        ("insert_hyphens",),
        ("allow_breaks",),
        ("line_height",),
        ("text_transform",),
        ("segment",),
    )
    SPAN_ATTR_KEY_CONVERSION = {
        key: key_alias_list[0]
        for key_alias_list in SPAN_ATTR_KEY_ALIAS_LIST
        for key in key_alias_list
    }
    SPAN_ATTR_KEY_ALIASES = tuple(SPAN_ATTR_KEY_CONVERSION.keys())

    TAG_TO_ATTR_DICT = {
        "b": {"font_weight": "bold"},
        "big": {"font_size": "larger"},
        "i": {"font_style": "italic"},
        "s": {"strikethrough": "true"},
        "sub": {"baseline_shift": "subscript", "font_scale": "subscript"},
        "sup": {"baseline_shift": "superscript", "font_scale": "superscript"},
        "small": {"font_size": "smaller"},
        "tt": {"font_family": "monospace"},
        "u": {"underline": "single"},
    }

    # TODO: paragraph properties, e.g. `justify`, `indent`, `insert_hyphens`

    def __init__(self, text: str = "", is_markup: bool = True, **kwargs):
        self.text = text
        self.is_markup = is_markup
        self._global_attrs = {}
        filtered_kwargs = FormattedString.filter_attrs(kwargs, FormattedString.SPAN_ATTR_KEY_ALIASES)
        self.update_global_attrs(filtered_kwargs)
        self._local_attrs = {}
        self._tag_strings = set()

        if is_markup:
            self._parse_markup()

    def __repr__(self) -> str:
        return f"FormattedString({repr(self.text)})"

    def __add__(self, string: Union[str, "FormattedString"]) -> "FormattedString":
        # TODO
        if isinstance(string, str):
            result = self.copy()
            result.text += string
            return result

        if isinstance(string, FormattedString):
            text_len = len(self.text)
            result = self.copy()
            result.text += string.text
            result._local_attrs.update({
                (text_len + sp[0], text_len + sp[1]): attr_dict
                for sp, attr_dict in string._local_attrs.items()
            })
            result._tag_strings.update(string._tag_strings)
            return result

        raise TypeError(f"Unsupported operand type(s) for +: 'FormattedString' and '{type(string)}'")

    def copy(self) -> "FormattedString":
        return copy.deepcopy(self)

    @staticmethod
    def filter_attrs(attr_dict: dict[str, Any], key_range: list[str]) -> dict[str, Any]:
        return {
            key: value
            for key, value in attr_dict.items()
            if key in key_range
        }

    @staticmethod
    def _convert_key_alias(key: str) -> str:
        return FormattedString.SPAN_ATTR_KEY_CONVERSION[key]

    @staticmethod
    def _update_attr_dict(attr_dict: dict[str, str], key: str, value: Any) -> None:
        converted_key = FormattedString._convert_key_alias(key)
        attr_dict[converted_key] = str(value)

    def update_global_attr(self, key: str, value: Any) -> None:
        FormattedString._update_attr_dict(self._global_attrs, key, value)

    def update_global_attrs(self, attr_dict: dict[str, Any]) -> None:
        for key, value in attr_dict.items():
            self.update_global_attr(key, value)

    def update_local_attr(self, span: tuple[int, int], key: str, value: Any) -> None:
        assert span[0] < span[1], f"Span {span} doesn't match any part of the string"
        if span in self._local_attrs.keys():
            FormattedString._update_attr_dict(self._local_attrs[span], key, value)
            return

        span_triplets = []
        gap_spans = [span]
        for sp, attr_dict in self._local_attrs.items():
            if sp[1] <= span[0] or span[1] <= sp[0]:
                continue
            span_to_become = (max(sp[0], span[0]), min(sp[1], span[1]))
            spans_to_add = []
            if sp[0] < span[0]:
                spans_to_add.append((sp[0], span[0]))
            if span[1] < sp[1]:
                spans_to_add.append((span[1], sp[1]))
            span_triplets.append((sp, span_to_become, spans_to_add))
            new_gap_spans = []
            for gsp in gap_spans:
                if gsp[1] <= sp[0] or sp[1] <= gsp[0]:
                    continue
                if gsp[0] < sp[0]:
                    new_gap_spans.append((gsp[0], sp[0]))
                if sp[1] < gsp[1]:
                    new_gap_spans.append((sp[1], gsp[1]))
            gap_spans = new_gap_spans
        for span_to_remove, span_to_become, spans_to_add in span_triplets:
            attr_dict = self._local_attrs.pop(span_to_remove)
            self._local_attrs[span_to_become] = attr_dict
            for span_to_add in spans_to_add:
                self._local_attrs[span_to_add] = attr_dict.copy()
            FormattedString._update_attr_dict(self._local_attrs[span_to_become], key, value)
        for gsp in gap_spans:
            self._local_attrs[gsp] = {}
            FormattedString._update_attr_dict(self._local_attrs[gsp], key, value)

    def update_local_attrs(self, text_span: tuple[int, int], attr_dict: dict[str, Any]) -> None:
        for key, value in attr_dict.items():
            self.update_local_attr(text_span, key, value)

    def _parse_markup(self) -> None:
        tag_pattern = r"""<(/?)(\w+)\s*((\w+\s*\=\s*('[^']*'|"[^"]*")\s*)*)>"""
        attr_pattern = r"""(\w+)\s*\=\s*(?:(?:'([^']*)')|(?:"([^"]*)"))"""
        start_match_obj_stack = []
        match_obj_pairs = []
        for match_obj in re.finditer(tag_pattern, self.text):
            if not match_obj.group(1):
                start_match_obj_stack.append(match_obj)
            else:
                match_obj_pairs.append((start_match_obj_stack.pop(), match_obj))
            self._tag_strings.add(match_obj.group())
        assert not start_match_obj_stack, "Unclosed tag(s) detected"

        for start_match_obj, end_match_obj in match_obj_pairs:
            tag_name = start_match_obj.group(2)
            assert tag_name == end_match_obj.group(2), "Unmatched tag names"
            assert not end_match_obj.group(3), "Attributes shan't exist in ending tags"
            if tag_name == "span":
                raw_attr_dict = {
                    match.group(1): match.group(2) or match.group(3)
                    for match in re.finditer(attr_pattern, start_match_obj.group(3))
                }
                attr_dict = FormattedString.filter_attrs(raw_attr_dict, FormattedString.SPAN_ATTR_KEY_ALIASES)
            elif tag_name in FormattedString.TAG_TO_ATTR_DICT.keys():
                assert not start_match_obj.group(3), f"Attributes shan't exist in tag '{tag_name}'"
                attr_dict = FormattedString.TAG_TO_ATTR_DICT[tag_name]
            else:
                raise AssertionError(f"Unknown tag: '{tag_name}'")

            text_span = (start_match_obj.end(), end_match_obj.start())
            self.update_local_attrs(text_span, attr_dict)

    def get_text_pieces(self) -> list[tuple[str, dict[str, str]]]:
        result = []

        def add_item(span: tuple[int, int], local_attr_dict: dict[str, str]) -> None:
            text_piece = self.text[slice(*span)]
            for tag_string in self._tag_strings:
                text_piece = text_piece.replace(tag_string, "")
            if self.is_markup:
                text_piece = saxutils.unescape(text_piece)
            if not text_piece:
                return
            attr_dict = self._global_attrs.copy()
            attr_dict.update(local_attr_dict)
            result.append((text_piece, attr_dict))

        local_spans = sorted(self._local_attrs.keys())
        next_span_starts = [span[0] for span in local_spans]
        next_span_starts.append(len(self.text))
        add_item((0, next_span_starts.pop(0)), {})
        for span, next_span_start in zip(local_spans, next_span_starts):
            add_item(span, self._local_attrs[span])
            add_item((span[1], next_span_start), {})
        return result
