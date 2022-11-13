from manimpango.fonts.enums import Style, Weight
import manimpango.renderer as r
import manimpango.layout as l
import manimpango.fonts as f

t = '''\
<span fgcolor="RED" bgcolor="WHITE">\
Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud.
</span>
'''

fd = f.FontDescription(weight=Weight.LIGHT, family='TeX Gyre Adventor', size=24, style=Style.OBLIQUE)
print(fd.size)
#b = l.Layout(markup='<span fgcolor="RED" bgcolor="WHITE">hi hello world this is nice</span>', font_desc=fd)
b = l.Layout(markup=t, font_desc=fd)

render = r.SVGRenderer('test.svg', 1000, 100, b)
render.render()

print(r.SVGRenderer('test.svg', 100, 100, l.Layout('hello')))

render = r.PNGRenderer('test.png', 500, 500, b)
render.render()
# import manimpango
# raise Exception(manimpango.list_fonts())
