project(
    'ManimPango',
    'cython', 'c',
    version: '0.6.1',
    default_options: [
        'warning_level=2',
        'c_std=c11',
    ],
)

# Import meson-python for py extension module support
py = import('python').find_installation(pure: false)

# Check for required dependencies using pkg-config
pango_dep = dependency('pango', version: '>=1.44')
pangocairo_dep = dependency('pangocairo', version: '>=1.44')
glib_dep = dependency('glib-2.0', version: '>=2.0')
cairo_dep = dependency('cairo', version: '>=1.14')
fontconfig_dep = dependency('fontconfig')

# Add include directory for local .pxd files
inc = include_directories('manimpango')

# Define extension modules using py.extension_module
_render_ext = py.extension_module(
    '_render',
    'manimpango/_render.pyx',
    dependencies: [
        pangocairo_dep,
        pango_dep,
        glib_dep,
        cairo_dep,
    ],
    include_directories: inc,
    install: true,
    subdir: 'manimpango',
)

_fonts_ext = py.extension_module(
    '_fonts',
    'manimpango/_fonts.pyx',
    dependencies: [
        pangocairo_dep,
        pango_dep,
        glib_dep,
        cairo_dep,
        fontconfig_dep,
    ],
    include_directories: inc,
    install: true,
    subdir: 'manimpango',
)

# Install Python modules
py.install_sources(
    [
        'manimpango/__init__.py',
        'manimpango/_text.py',
        'manimpango/enums.py',
    ],
    subdir: 'manimpango',
)
