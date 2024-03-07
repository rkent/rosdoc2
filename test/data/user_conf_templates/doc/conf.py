## GENERATED_CONTENT by rosdoc2.verbs.build.builders.SphinxBuilder.
## This conf.py imports the variables from the user defined (or default if none
## was provided) conf.py, extends the settings to support Breathe and Exhale and
## to set up intersphinx mappings correctly, among other things.
# flake8: noqa


import os
import sys

## Set values for variables obtained by running conf.py.
project = "user_conf_templates"
copyright = "2021, conf.j2.py Author  (Apache License 2.0)"
release = "0.1.3"
version = "0.1"
extensions = ['sphinx.ext.viewcode']
templates_path = ['/home/kent/github/rkent/rosdoc2/test/data/user_conf_templates/doc/_templates']
exclude_patterns = []
master_doc = "index"
source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown', '.markdown': 'markdown'}
html_theme = "sphinx_rtd_theme"
html_theme_options = {'collapse_navigation': False, 'sticky_navigation': True, 'navigation_depth': -1, 'includehidden': True, 'titles_only': False}
rosdoc2_settings = {}

## Based on the rosdoc2 settings, do various things to the settings before
## letting Sphinx continue.

def ensure_global(name, default):
    if name not in globals():
        globals()[name] = default

ensure_global('rosdoc2_settings', {})
ensure_global('extensions', [])

if rosdoc2_settings.get('enable_autodoc', True):
    print('[rosdoc2] enabling autodoc', file=sys.stderr)
    extensions.append('sphinx.ext.autodoc')
    # Provide all runtime dependencies to be mocked up
    autodoc_mock_imports = ['rclcpp', 'rclpy']
    import importlib
    for item in autodoc_mock_imports:
        try:
            importlib.import_module(item)
        except ModuleNotFoundError:
            pass

    # Add the package directory to PATH, so that `sphinx-autodoc` can import it
    sys.path.insert(0, os.path.dirname('/home/kent/github/rkent/rosdoc2/test/data/user_conf_templates/None'))

if rosdoc2_settings.get('enable_intersphinx', True):
    print('[rosdoc2] enabling intersphinx', file=sys.stderr)
    extensions.append('sphinx.ext.intersphinx')

build_type = 'ament_cmake'
always_run_doxygen = False
is_doxygen_invoked = True

# TODO: We need better description of how 'enable_breathe' and 'enable_exhale' are managed.
#       Default could be None, and if set then generate error if no doxygen.

# By default, the `exhale`/`breathe` extensions should be added if `doxygen` was invoked
if rosdoc2_settings.get('enable_breathe', is_doxygen_invoked):
    # Configure Breathe.
    # Breathe ingests the XML output from Doxygen and makes it accessible from Sphinx.
    # First check that doxygen would have been run
    if is_doxygen_invoked:
        print('[rosdoc2] enabling breathe', file=sys.stderr)
        ensure_global('breathe_projects', {})
        breathe_projects.update({        "user_conf_templates Doxygen Project": "/tmp/pytest-of-kent/pytest-1/test_builder0/build/user_conf_templates/output_staging/generated/doxygen/xml"
    })
        if breathe_projects:
            # Enable Breathe and arbitrarily select the first project.
            extensions.append('breathe')
            breathe_default_project = next(iter(breathe_projects.keys()))

    else:
        log.info(
            "Cannot enable the 'breathe' extension if 'doxygen' is not invoked."
            "Please enable 'always_run_doxygen' if the package is not an"
            "'ament_cmake' or 'cmake' package.")

if rosdoc2_settings.get('enable_exhale', is_doxygen_invoked):
    # Configure Exhale.
    # Exhale uses the output of Doxygen and Breathe to create easier to browse pages
    # for classes and functions documented with Doxygen.
    # This is similar to the class hierarchies and namespace listing provided by
    # Doxygen out of the box.
    print('[rosdoc2] enabling exhale', file=sys.stderr)
    # First check that doxygen would have been run
    if is_doxygen_invoked:
        extensions.append('exhale')
        ensure_global('exhale_args', {})

        default_exhale_specs_mapping = {
            'page': [':content-only:'],
            **dict.fromkeys(
                ['class', 'struct'],
                [':members:', ':protected-members:', ':undoc-members:']),
        }

        exhale_specs_mapping = rosdoc2_settings.get(
            'exhale_specs_mapping', default_exhale_specs_mapping)

        from exhale import utils
        exhale_args.update({
            # These arguments are required.
            "containmentFolder": "/home/kent/github/rkent/rosdoc2/test/data/user_conf_templates/doc/generated/cpp",
            "rootFileName": "index.rst",
            "rootFileTitle": "user_conf_templates C/C++ API",
            "doxygenStripFromPath": "..",
            # Suggested optional arguments.
            "createTreeView": True,
            "fullToctreeMaxDepth": 1,
            "unabridgedOrphanKinds": [],
            "fullApiSubSectionTitle": "Reference",
            # TIP: if using the sphinx-bootstrap-theme, you need
            # "treeViewIsBootstrap": True,
            "exhaleExecutesDoxygen": False,
            # Maps markdown files to the "md" lexer, and not the "markdown" lexer
            # Pygments registers "md" as a valid markdown lexer, and not "markdown"
            "lexerMapping": {r".*\.(md|markdown)$": "md",},
            "customSpecificationsMapping": utils.makeCustomSpecificationsMapping(
                lambda kind: exhale_specs_mapping.get(kind, [])),
            "verboseBuild": True,
        })
    else:
        log.info(
            "Cannot enable the 'breathe' extension if 'doxygen' is not invoked."
            "Please enable 'always_run_doxygen' if the package is not an"
            "'ament_cmake' or 'cmake' package.")

if rosdoc2_settings.get('override_theme', True):
    extensions.append('sphinx_rtd_theme')
    html_theme = 'sphinx_rtd_theme'
    print(f"[rosdoc2] overriding theme to be '{html_theme}'", file=sys.stderr)

if rosdoc2_settings.get('automatically_extend_intersphinx_mapping', True):
    print(f"[rosdoc2] extending intersphinx mapping", file=sys.stderr)
    if 'sphinx.ext.intersphinx' not in extensions:
        raise RuntimeError(
            "Cannot extend intersphinx mapping if 'sphinx.ext.intersphinx' "
            "has not been added to the extensions")
    ensure_global('intersphinx_mapping', {
        'only_messages': ('file:///tmp/pytest-of-kent/pytest-1/test_builder0/output/only_messages/', '/tmp/pytest-of-kent/pytest-1/test_builder0/cross_references/only_messages/objects.inv'),
        'minimum_cpp': ('file:///tmp/pytest-of-kent/pytest-1/test_builder0/output/minimum_cpp/', '/tmp/pytest-of-kent/pytest-1/test_builder0/cross_references/minimum_cpp/objects.inv'),
        'full_package': ('file:///tmp/pytest-of-kent/pytest-1/test_builder0/output/full_package/', '/tmp/pytest-of-kent/pytest-1/test_builder0/cross_references/full_package/objects.inv'),
        'minimum_package': ('file:///tmp/pytest-of-kent/pytest-1/test_builder0/output/minimum_package/', '/tmp/pytest-of-kent/pytest-1/test_builder0/cross_references/minimum_package/objects.inv'),
        'meta_package': ('file:///tmp/pytest-of-kent/pytest-1/test_builder0/output/meta_package/', '/tmp/pytest-of-kent/pytest-1/test_builder0/cross_references/meta_package/objects.inv')
    })

if rosdoc2_settings.get('support_markdown', True):
    print(f"[rosdoc2] adding markdown parser", file=sys.stderr)
    # The `myst_parser` is used specifically if there are markdown files
    # in the sphinx project
    extensions.append('myst_parser')

# Provide tags to conditionally include documentation
for tag in ['package_name', 'package_version', 'package_description', 'package_directory', 'breathe_projects', 'containmentFolder', 'did_run_doxygen', 'build_type', 'exec_depends', 'intersphinx_mapping_extensions', 'package', 'package_authors', 'package_licenses', 'package_src_directory', 'package_underline', 'package_version_short', 'root_title', 'root_title_underline', 'url_website', 'sphinx_sourcedir', 'has_cpp', 'doclist']:
    tags.add(tag)
