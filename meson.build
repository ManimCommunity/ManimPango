project(
  'manimpango', 'c',
  version: '1.20.1',
  meson_version: '>= 0.49.0',
  default_options: [
    'warning_level=1',
    'buildtype=debugoptimized',
  ],
)

pango_require_version = '>=1.30.0'

pymod = import('python')
python = pymod.find_installation(get_option('python'))

cython = find_program('cython', required : true)

pyver = python.language_version()
if pyver.version_compare('< 3.6')
    error('Requires Python >= 3.6')
endif

cc = meson.get_compiler('c')
main_c_args = []

if get_option('coverage')
    main_c_args += [
        '-DCYTHON_TRACE=1',
        '-DCYTHON_TRACE_NOGIL=1'
    ]
endif

if host_machine.system() == 'windows'
    main_c_args += [
        '-DUNICODE=1',
    ]
endif

main_c_args = cc.get_supported_arguments(main_c_args)

manimpango_version = meson.project_version()

#for the tests.
configuration_files = [
    '.coveragerc',
    'setup.cfg'
]

foreach config_files : configuration_files
  configure_file(
    input: config_files,
    output: config_files,
    copy: true,
  )
endforeach

subdir('manimpango')

if get_option('tests')
  subdir('tests')
endif