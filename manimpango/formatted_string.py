from typing import Any, Union
import copy
import itertools as it
import xml.sax as sax
import warnings


class MarkupHandler(sax.ContentHandler):
    def __init__(self, text_str):
        super().__init__()
        self._line_chars_count = list(map(len, text_str.splitlines()))
        # Each element of `tag_data`, `_tag_data_heap` is:
        # [
        #     start_tag_span_start,
        #     start_tag_span_end,
        #     end_tag_span_start,
        #     end_tag_span_end,
        #     tag_name,
        #     attr_dict
        # ]
        self.tag_data = []
        self._tag_data_heap = []
        # 0 for not open, 1 for start tag opening, -1 for end tag opening
        self._tag_open_status = 0

    @property
    def curr_index(self):
        col_num = self._locator.getColumnNumber()
        line_num = self._locator.getLineNumber()
        return sum(self._line_chars_count[:line_num - 1]) + col_num + line_num - 1

    def startElement(self, name, attrs):
        assert self._tag_open_status == 0
        self._tag_data_heap.append([
            self.curr_index, -1, -1, -1, name, dict(attrs)
        ])
        self._tag_open_status = 1

    def endElement(self, name):
        assert self._tag_open_status == 0
        assert self._tag_data_heap[-1][4] == name
        self._tag_data_heap[-1][2] = self.curr_index
        self._tag_open_status = -1

    def close_tag(self):
        if self._tag_open_status == 0:
            return
        if self._tag_open_status == 1:
            self._tag_data_heap[-1][1] = self.curr_index
        else:
            self._tag_data_heap[-1][3] = self.curr_index
            self.tag_data.append(self._tag_data_heap.pop())
        self._tag_open_status = 0

    def characters(self, content):
        self.close_tag()

    def endDocument(self):
        self.close_tag()


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

    # TODO: paragraph properties, e.g. `justify`, `indent`, `insert_hypens`

    def __init__(self, text: str = "", need_escape: bool = False, **kwargs):
        self.text = text
        self.need_escape = need_escape
        self.global_attrs = {}
        filtered_kwargs = FormattedString.filter_attrs(kwargs)
        self.update_global_attrs(filtered_kwargs)
        self.local_attrs = {}

        if need_escape:
            # TODO
            self.tag_spans = ()
        else:
            handler = MarkupHandler(text)
            sax.parseString(text, handler)
            self.tag_spans = tuple(sorted(it.chain(*(
                ((data[0], data[1]), (data[2], data[3]))
                for data in handler.tag_data
            ))))
            for data in handler.tag_data:
                text_span = (data[1], data[2])
                tag_name = data[4]
                raw_attr_dict = data[5]
                if tag_name == "span":
                    attr_dict = FormattedString.filter_attrs(raw_attr_dict)
                elif tag_name in FormattedString.TAG_TO_ATTR_DICT.keys():
                    attr_dict = FormattedString.TAG_TO_ATTR_DICT[tag_name]
                else:
                    warnings.warn(f"Unknown tag: '{tag_name}'")
                    continue
                self.update_local_attrs(text_span, attr_dict)

    def __repr__(self) -> str:
        return f"FormattedString({repr(self.text)})"

    def __add__(self, string: Union[str, "FormattedString"]) -> "FormattedString":
        if isinstance(string, str):
            result = self.copy()
            result.text += string
            return result

        if isinstance(string, FormattedString):
            text_len = self.text_len
            result = self.copy()
            result.text += string.text
            result.tag_spans += tuple(
                (text_len + sp[0], text_len + sp[1])
                for sp in string.tag_spans
            )
            result.local_attrs.update({
                (text_len + sp[0], text_len + sp[1]): attr_dict
                for sp, attr_dict in string.local_attrs.items()
            })
            return result

        raise TypeError(f"Unsupported operand type(s) for +: 'FormattedString' and '{type(string)}'")

    def copy(self) -> "FormattedString":
        return copy.deepcopy(self)

    @property
    def text_len(self) -> int:
        return len(self.text)

    @property
    def text_without_tags(self) -> str:
        piece_ends, piece_starts = zip(*self.tag_spans)
        return "".join(
            self.text[piece_start:piece_end]
            for piece_start, piece_end in zip(
                (0, *piece_starts), (*piece_ends, self.text_len)
            )
        )

    def convert_index(self, index: int) -> int:
        if not 0 <= index <= self.text_len:
            raise ValueError(f"Index {index} out of range")
        if any(
            span[0] < index < span[1]
            for span in self.tag_spans
        ):
            raise ValueError(f"Index {index} is inside tag")
        skipped_length = sum(
            span[1] - span[0]
            for span in self.tag_spans
            if span[1] <= index
        )
        return index - skipped_length

    @staticmethod
    def filter_attrs(attr_dict: dict[str, Any]) -> dict[str, Any]:
        filtered_out_keys = set(filter(
            lambda key: key not in FormattedString.SPAN_ATTR_KEY_ALIASES,
            attr_dict.keys()
        ))
        if filtered_out_keys:
            warnings.warn(f"Unknown key(s): {str(filtered_out_keys)[1:-1]}")
            return {
                key: value
                for key, value in attr_dict.items()
                if key not in filtered_out_keys
            }
        return attr_dict

    @staticmethod
    def convert_key_alias(key: str) -> str:
        return FormattedString.SPAN_ATTR_KEY_CONVERSION[key]

    @staticmethod
    def update_attr_dict(attr_dict: dict[str, str], key: str, value: Any) -> None:
        converted_key = FormattedString.convert_key_alias(key)
        attr_dict[converted_key] = str(value)

    def update_global_attr(self, key: str, value: Any) -> None:
        FormattedString.update_attr_dict(self.global_attrs, key, value)

    def update_global_attrs(self, attr_dict: dict[str, Any]) -> None:
        for key, value in attr_dict:
            self.update_global_attr(key, value)

    def update_local_attr(self, text_span: tuple[int, int], key: str, value: Any) -> None:
        span = tuple(map(self.convert_index, text_span))
        if span[0] >= span[1]:
            warnings.warn(f"Span {text_span} doesn't match any part of the string")
            return

        if span in self.local_attrs.keys():
            FormattedString.update_attr_dict(self.local_attrs[span], key, value)
            return

        span_triplets = []
        for sp, attr_dict in self.local_attrs.items():
            if sp[1] <= span[0] or span[1] <= sp[0]:
                continue
            spans_to_add = []
            if sp[0] < span[0]:
                spans_to_add.append((sp[0], span[0]))
            if span[1] < sp[1]:
                spans_to_add.append((span[1], sp[1]))
            span_to_become = (max(sp[0], span[0]), min(sp[1], span[1]))
            span_triplets.append((sp, span_to_become, spans_to_add))
        for span_to_remove, span_to_become, spans_to_add in span_triplets:
            attr_dict = self.local_attrs.pop(span_to_remove)
            self.local_attrs[span_to_become] = attr_dict
            for span_to_add in spans_to_add:
                self.local_attrs[span_to_add] = attr_dict.copy()
            FormattedString.update_attr_dict(self.local_attrs[span_to_become], key, value)

    def update_local_attrs(self, text_span: tuple[int, int], attr_dict: dict[str, Any]) -> None:
        for key, value in attr_dict:
            self.update_local_attr(text_span, key, value)
