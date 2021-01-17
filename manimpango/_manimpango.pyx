import typings as T
import copy
from enum import Enum
cdef class Color:
    cdef int red
    cdef int green
    cdef int blue
    cdef PangoColor* color
    cdef bint gc
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue
     
    def copy(self):
        """
        Make a deep copy of the ``Color`` structure.
        :return:
            a copy of :class:`Color`
        """
        temp = Color(
            red = self.red,
            green = self.green,
            blue = self.blue
        )
        return temp

    def __copy__(self) -> "Color":
        return self.copy()

    def __deepcopy__(self, memo) -> "Color":
        return self.copy()

    @property
    def red(self):
        return self._red

    @red.setter
    def red(self, red: int):
        self._red = int(red)
        self.color.red = red

    @property
    def green(self):
        return self._green

    @green.setter
    def green(self, green: int):
        self._green = int(green)
        self.color.green = green

    @property
    def blue(self):
        return self._blue

    @blue.setter
    def blue(self, blue: int):
        self._blue = int(blue)
        self.color.blue = blue

    def parse_color(self, spec: str) -> bool:
        """
        Fill in the fields of a color from a string
        specification. The string can either one of
        a large set of standard names. (Taken from
        the CSS specification), or it can be a
        hexadecimal value in the form '#rgb'
        '#rrggbb' '#rrrgggbbb' or '#rrrrggggbbbb'
        where 'r', 'g' and 'b' are hex digits of
        the red, green, and blue components of the
        color, respectively. (White in the four forms
        is '#fff' '#ffffff' '#fffffffff' and
        '#ffffffffffff')
        :param spec:
            a string specifying the new color
        :return:
            ``TRUE`` if parsing of the specifier succeeded,
            otherwise false.
        """
        spec_encode = spec.encode('utf-8')
        ret = pango_color_parse(self.color, spec_encode)
        if ret:
            self._red = int(self.color.red)
            self._green = int(self.color.green)
            self._blue = int(self.color.blue)

    def to_string(self):
        """
        Returns a textual specification of color in the
        hexadecimal form #rrrrggggbbbb, where r, g and b
        are hex digits representing the red, green, and
        blue components respectively.
        :return:
            string hexadecimal
        """
        string = pango_color_to_string(self.color)
        new = copy.deepcopy(string.decode("utf-8"))
        g_free(string)
        return new

    def __eq__(self, col: "Color") -> bool:
        if isinstance(col, Color):
            return (
                self.red == col.red
                and self.green == col.green
                and self.red == self.red
            )
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Color(red={self.red},blue={self.blue},green={self.green})>"
class Underline(Enum):
    NONE = PANGO_UNDERLINE_NONE
    SINGLE = PANGO_UNDERLINE_SINGLE
    DOUBLE = PANGO_UNDERLINE_DOUBLE
    LOW = PANGO_UNDERLINE_LOW
    ERROR = PANGO_UNDERLINE_ERROR
class Gravity(Enum):
    SOUTH = PANGO_GRAVITY_SOUTH
    EAST = PANGO_GRAVITY_EAST
    NORTH = PANGO_GRAVITY_NORTH
    WEST = PANGO_GRAVITY_WEST
    AUTO = PANGO_GRAVITY_AUTO
class GravityHint(Enum):
    NATURAL = PANGO_GRAVITY_HINT_NATURAL
    STRONG = PANGO_GRAVITY_HINT_STRONG
    LINE = PANGO_GRAVITY_HINT_LINE
class Show(Enum):
    NONE = PANGO_SHOW_NONE
    SPACES = PANGO_SHOW_SPACES
    LINE_BREAKS = PANGO_SHOW_LINE_BREAKS
    IGNORABLES=PANGO_SHOW_IGNORABLES
class TextAttributes:
    def __init__(
        self,
        start:int,
        end:int,
        font_desc_string:str=None,
        language:str=None,
        foreground:Color=None,
        background:Color=None,
        strikethrough:bool=None,
        strikethrough_color:Color=None,
        underline:Underline=None,
        underline_color:Color=None,
        scale:float=None,
        rise:float=None
        letter_spacing:int=None,
        font_fallback:bool=None,
        gravity:Gravity=None,
        gravity_hint:GravityHint=None,
        font_features:str=None,
        foreground_alpha:int=None,
        background_alpha:int=None,
        allow_breaks:bool=None,
        insert_hyphens:bool=None,
        show:Show=None
    ):
        self.start = start
        self.end = end
        self.font_desc_string = font_desc
        self.language = language
        self.foreground = foreground
        self.background = background
        self.strikethrough = strikethrough
        self.strikethrough_color = strikethrough_color
        self.underline = underline
        self.underline_color = underline_color
        self.scale= scale
        self.rise = rise
        self.letter_spacing = letter_spacing
        self.font_fallback = font_fallback
        self.gravity = gravity
        self.gravity_hint = gravity_hint
        self.font_features = font_features
        self.foreground_alpha = foreground_alpha
        self.background_alpha = background_alpha
        self.allow_breaks = allow_breaks
        self.insert_hyphens = insert_hyphens
        self.show = show

    cdef PangoFontDescription get_font_desc(self):
        font_desc = self.font_desc_string.encode('utf-8')
        return pango_font_description_from_string(font_desc)

cdef class AttrList:
    cdef PangoAttrList* _list
    def __cinit__(self):
        self._list = pango_attr_list_new()
        if self._list is NULL:
            raise MemoryError("Can't initialise a AttrList")
    def __init__(self, *attributes):
        for i in attributes:
            pango_attr_list_insert(self._list,i)

cdef class Text:
    cdef list attributes
    cdef int size
    cdef str font_desc
    cdef str orig_text
    cdef str markup
    def __init__(
        attributes:list,
        size:int,
        font_desc_string:str
        line_spacing:int,
        orig_text:str,
        markup:str = None
    ):
        self.attributes = attributes
        self.size = size
        self.font_desc = font_desc_string

    def __iter__(self):
        self.n=0
        return self