# This module contains implementation of Colours as how
# it is Pango. Should be helpful when we implement
# attributes.

import copy

cdef class Color:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

    cpdef Color copy(self):
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

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
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

    cpdef void parse_color(self, char* spec):
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

    cpdef str to_string(self):
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

    def __eq__(self, col) -> bool:
        if isinstance(col, Color):
            return (
                self.red == col.red
                and self.green == col.green
                and self.red == self.red
            )
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Color(red={self.red},blue={self.blue},green={self.green})>"
