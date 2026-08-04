project(
    'ManimPango',
    'cython', 'c',
    version: '0.6.1',
    default_options: [
        'warning_level=2',
        'c_std=c11',
    ],
)

py = import('python').find_installation(pure: false)

pango_dep = dependency('pango', version: '>=1.44')
pangocairo_dep = dependency('pangocairo', version: '>=1.44')
glib_dep = dependency('glib-2.0', version: '>=2.0')
cairo_dep = dependency('cairo', version: '>=1.14')
font_backend_deps = []
if host_machine.system() == 'linux'
    font_backend_deps += [dependency('fontconfig')]
elif host_machine.system() == 'darwin'
    font_backend_deps += [dependency('appleframeworks', modules: ['CoreFoundation', 'CoreText'])]
endif

# Include directory for local .pxd files
inc = include_directories('src/manimpango')

_render_ext = py.extension_module(
    '_render',
    'src/manimpango/_render.pyx',
    'src/manimpango/font_backend.c',
    dependencies: [
        pangocairo_dep,
        pango_dep,
        glib_dep,
        cairo_dep,
        font_backend_deps,
    ],
    include_directories: inc,
    install: true,
    subdir: 'manimpango',
)

_fonts_ext = py.extension_module(
    '_fonts',
    'src/manimpango/_fonts.pyx',
    'src/manimpango/font_backend.c',
    dependencies: [
        pangocairo_dep,
        pango_dep,
        glib_dep,
        cairo_dep,
        font_backend_deps,
    ],
    include_directories: inc,
    install: true,
    subdir: 'manimpango',
)

py.install_sources(
    [
        'src/manimpango/__init__.py',
        'src/manimpango/_spans.py',
        'src/manimpango/_text.py',
        'src/manimpango/enums.py',
        'src/manimpango/exceptions.py',
    ],
    subdir: 'manimpango',
)
