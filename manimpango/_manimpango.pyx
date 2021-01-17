
# class TextAttributes:
#     def __init__(
#         self,
#         start:int,
#         end:int,
#         font_desc_string:str=None,
#         language:str=None,
#         foreground:Color=None,
#         background:Color=None,
#         strikethrough:bool=None,
#         strikethrough_color:Color=None,
#         underline:Underline=None,
#         underline_color:Color=None,
#         scale:float=None,
#         rise:float=None
#         letter_spacing:int=None,
#         font_fallback:bool=None,
#         gravity:Gravity=None,
#         gravity_hint:GravityHint=None,
#         font_features:str=None,
#         foreground_alpha:int=None,
#         background_alpha:int=None,
#         allow_breaks:bool=None,
#         insert_hyphens:bool=None,
#         show:Show=None
#     ):
#         self.start = start
#         self.end = end
#         self.font_desc_string = font_desc
#         self.language = language
#         self.foreground = foreground
#         self.background = background
#         self.strikethrough = strikethrough
#         self.strikethrough_color = strikethrough_color
#         self.underline = underline
#         self.underline_color = underline_color
#         self.scale= scale
#         self.rise = rise
#         self.letter_spacing = letter_spacing
#         self.font_fallback = font_fallback
#         self.gravity = gravity
#         self.gravity_hint = gravity_hint
#         self.font_features = font_features
#         self.foreground_alpha = foreground_alpha
#         self.background_alpha = background_alpha
#         self.allow_breaks = allow_breaks
#         self.insert_hyphens = insert_hyphens
#         self.show = show

#     cdef PangoFontDescription get_font_desc(self):
#         font_desc = self.font_desc_string.encode('utf-8')
#         return pango_font_description_from_string(font_desc)

cdef class AttrList:
    cdef PangoAttrList* _list
    def __cinit__(self):
        self._list = pango_attr_list_new()
        if self._list is NULL:
            raise MemoryError("Can't initialise a AttrList")
    #def __init__(self, *attributes):
    #    for i in attributes:
    #        pango_attr_list_insert(self._list,i)

cdef class Text:
    cdef list attributes
    cdef int size
    cdef str font_desc
    cdef str orig_text
    cdef str markup
    def __init__(
        self,
        attributes:list,
        size:int,
        font_desc_string:str,
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