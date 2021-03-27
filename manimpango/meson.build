python_sources = [
  '__init__.py',
  '_version.py',
  'utils.py',
]
foreach python_source : python_sources
  configure_file(
    input: python_source,
    output: python_source,
    copy: true,
  )
endforeach
python.install_sources(python_sources,
  pure : false,
  subdir : 'manimpango'
)

cython_sources = [
  'cmanimpango.pyx',
  'enums.pyx',
  'register_font.pyx'
]
cython_args = [
    cython,
    '@INPUT@',
    '-o',
    '@OUTPUT@',
    '-3',
    '--include-dir='+meson.current_source_dir()
]

if get_option('buildtype') == 'debug'
    cython_args += [
        '--gdb'
    ]
endif

if get_option('coverage')
    cython_args += [
        '--line-directives'
    ]
endif

python_dep = python.dependency()
pangocairo_dep = dependency('pangocairo', version: pango_require_version, required: true)

foreach source : cython_sources
    module_name = source.split('.')[0]
    output_filename = module_name + '.c'
    source_c = custom_target(
        module_name,
        output : output_filename,
        input : source,
        command : cython_args
    )
    python.extension_module(
        module_name,
        source_c,
        subdir : 'manimpango',
        dependencies : [
            python_dep,
            pangocairo_dep
        ],
        c_args: main_c_args,
        install: true
    )
endforeach
