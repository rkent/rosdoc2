# Copyright 2020 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
import shutil
import subprocess

from jinja2 import Template
import pkg_resources
import setuptools

from ..builder import Builder
from ..collect_inventory_files import collect_inventory_files
from ..create_format_map_from_package import create_format_map_from_package
from ..generate_interface_docs import generate_interface_docs
from ....slugify import slugify

logger = logging.getLogger('rosdoc2')


def esc_backslash(path):
    """Escape backslashes to support Windows paths in strings."""
    return path.replace('\\', '\\\\') if path else ''


def generate_template_variables(
    intersphinx_mapping_extensions,
    breathe_projects,
    build_context,
    sphinx_sourcedir,
    package_src_directory,
    user_doc_dir,
    standard_docs,
    interface_counts,
    meta_dependencies,
    extra_doc_files,
    doclist,
):
    """Generate the variables used by templates for conf.py and index.rst."""
    package = build_context.package
    template_variables = create_format_map_from_package(package)
    root_title = f'Package {package.name}'

    build_type = build_context.build_type
    always_run_doxygen = build_context.always_run_doxygen
    always_run_sphinx_apidoc = build_context.always_run_sphinx_apidoc
    ament_cmake_python = build_context.ament_cmake_python

    has_python = build_type == 'ament_python' or always_run_sphinx_apidoc or ament_cmake_python
    has_cpp = build_type in ['ament_cmake', 'cmake'] or always_run_doxygen

    # standard urls in a package definition
    url_repository = None
    url_website = None
    url_bugtracker = None
    for url in package.urls:
        if url.type == 'repository':
            url_repository = f'* `Repository <{url.url}>`_'
        if url.type == 'website':
            url_website = f'* `Website <{url.url}>`_'
        if url.type == 'bugtracker':
            url_bugtracker = f'* `Bugtracker <{url.url}>`_'

    # Fix containment folder string for possible Windows paths
    containmentFolder = esc_backslash(
        os.path.normpath(os.path.join(sphinx_sourcedir, 'generated', 'cpp')))

    template_variables.update({
        'always_run_doxygen': build_context.always_run_doxygen,
        'breathe_projects': ',\n'.join(breathe_projects) + '\n    ',
        'containmentFolder': containmentFolder,
        'did_run_doxygen': len(breathe_projects) > 0,
        'build_type': build_context.build_type,
        'exec_depends': [exec_depend.name for exec_depend in package.exec_depends],
        'intersphinx_mapping_extensions': ',\n        '.join(intersphinx_mapping_extensions),
        'package': package,
        'package_authors': ', '.join(set(
            [a.name for a in package.authors] + [m.name for m in package.maintainers]
        )),
        'package_licenses': ', '.join(package.licenses),
        'package_src_directory': esc_backslash(package_src_directory),
        'package_underline': '=' * len(package.name),
        'package_version_short': '.'.join(package.version.split('.')[0:2]),
        'root_title': root_title,
        'root_title_underline': '=' * len(root_title),
        'url_bugtracker': url_bugtracker,
        'url_repository': url_repository,
        'url_website': url_website,
        'sphinx_sourcedir': os.path.abspath(sphinx_sourcedir),
        'has_user_docs': bool(user_doc_dir),
        'has_standard_docs': len(standard_docs) > 0,
        'has_msg_defs': interface_counts['msg'] > 0,
        'has_srv_defs': interface_counts['srv'] > 0,
        'has_cpp': has_cpp,
        'has_python': has_python,
        'has_readme': 'readme' in standard_docs,
        'meta_dependencies': meta_dependencies,
        'extra_doc_files': extra_doc_files,
        'doclist': doclist,
    })

    # Each True template key will be converted into a sphinx tag in conf.py
    tags = []
    for (key, value) in template_variables.items():
        if bool(value):
            tags.append(key)
    template_variables.update({'tags': tags})

    return template_variables


rosdoc2_wrapping_conf_py_preamble = """\
## GENERATED_CONTENT by rosdoc2.verbs.build.builders.SphinxBuilder.
## This conf.py imports the variables from the user defined (or default if none
## was provided) conf.py, extends the settings to support Breathe and Exhale and
## to set up intersphinx mappings correctly, among other things.
# flake8: noqa


import os
import sys

## Set values for variables obtained by running conf.py.
"""

rosdoc2_wrapping_conf_py_template = """
## Based on the rosdoc2 settings, do various things to the settings before
## letting Sphinx continue.

def ensure_global(name, default):
    if name not in globals():
        globals()[name] = default

ensure_global('rosdoc2_settings', {{}})
ensure_global('extensions', [])

if rosdoc2_settings.get('enable_autodoc', True):
    print('[rosdoc2] enabling autodoc', file=sys.stderr)
    extensions.append('sphinx.ext.autodoc')
    # Provide all runtime dependencies to be mocked up
    autodoc_mock_imports = {exec_depends}
    import importlib
    for item in autodoc_mock_imports:
        try:
            importlib.import_module(item)
        except ModuleNotFoundError:
            pass

    # Add the package directory to PATH, so that `sphinx-autodoc` can import it
    sys.path.insert(0, os.path.dirname('{package_src_directory}'))

if rosdoc2_settings.get('enable_intersphinx', True):
    print('[rosdoc2] enabling intersphinx', file=sys.stderr)
    extensions.append('sphinx.ext.intersphinx')

build_type = '{build_type}'
always_run_doxygen = {always_run_doxygen}
is_doxygen_invoked = {did_run_doxygen}

# TODO: We need better description of how 'enable_breathe' and 'enable_exhale' are managed.
#       Default could be None, and if set then generate error if no doxygen.

# By default, the `exhale`/`breathe` extensions should be added if `doxygen` was invoked
if rosdoc2_settings.get('enable_breathe', is_doxygen_invoked):
    # Configure Breathe.
    # Breathe ingests the XML output from Doxygen and makes it accessible from Sphinx.
    # First check that doxygen would have been run
    if is_doxygen_invoked:
        print('[rosdoc2] enabling breathe', file=sys.stderr)
        ensure_global('breathe_projects', {{}})
        breathe_projects.update({{{breathe_projects}}})
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
        ensure_global('exhale_args', {{}})

        default_exhale_specs_mapping = {{
            'page': [':content-only:'],
            **dict.fromkeys(
                ['class', 'struct'],
                [':members:', ':protected-members:', ':undoc-members:']),
        }}

        exhale_specs_mapping = rosdoc2_settings.get(
            'exhale_specs_mapping', default_exhale_specs_mapping)

        from exhale import utils
        exhale_args.update({{
            # These arguments are required.
            "containmentFolder": "{containmentFolder}",
            "rootFileName": "index.rst",
            "rootFileTitle": "{package_name} C/C++ API",
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
            "lexerMapping": {{r".*\\.(md|markdown)$": "md",}},
            "customSpecificationsMapping": utils.makeCustomSpecificationsMapping(
                lambda kind: exhale_specs_mapping.get(kind, [])),
            "verboseBuild": True,
        }})
    else:
        log.info(
            "Cannot enable the 'breathe' extension if 'doxygen' is not invoked."
            "Please enable 'always_run_doxygen' if the package is not an"
            "'ament_cmake' or 'cmake' package.")

if rosdoc2_settings.get('override_theme', True):
    extensions.append('sphinx_rtd_theme')
    html_theme = 'sphinx_rtd_theme'
    print(f"[rosdoc2] overriding theme to be '{{html_theme}}'", file=sys.stderr)

if rosdoc2_settings.get('automatically_extend_intersphinx_mapping', True):
    print(f"[rosdoc2] extending intersphinx mapping", file=sys.stderr)
    if 'sphinx.ext.intersphinx' not in extensions:
        raise RuntimeError(
            "Cannot extend intersphinx mapping if 'sphinx.ext.intersphinx' "
            "has not been added to the extensions")
    ensure_global('intersphinx_mapping', {{
        {intersphinx_mapping_extensions}
    }})

if rosdoc2_settings.get('support_markdown', True):
    print(f"[rosdoc2] adding markdown parser", file=sys.stderr)
    # The `myst_parser` is used specifically if there are markdown files
    # in the sphinx project
    extensions.append('myst_parser')

# Provide tags to conditionally include documentation
for tag in {tags}:
    tags.add(tag)
"""  # noqa: W605

standard_documents_rst = """\
Standard Documents
==================

.. toctree::
   :maxdepth: 1
   :glob:

   standard/*
"""

index_search_rst = """\
Index and Search
================

:ref:`genindex`

:ref:`search`
"""

subdirectory_rst_template = """\
{name}
{name_underline}

.. toctree::
   :maxdepth: 1
   :glob:

   ../{relpath}/*
"""


class SphinxBuilder(Builder):
    """
    Builder for Sphinx.

    Supported keys for the builder_entry_dictionary include:

    - name (str) (required)
      - name of the documentation, used in reference to the content generated by this builder
    - builder (str) (required)
      - required for all builders, must be 'sphinx' to use this class
    - sphinx_sourcedir (str) (optional)
      - directory containing the Sphinx project, i.e. the `conf.py`, the setting
        you would pass to sphinx-build as SOURCEDIR. Defaults to `doc`.
    """

    def __init__(self, builder_name, builder_entry_dictionary, build_context):
        """Construct a new SphinxBuilder."""
        super(SphinxBuilder, self).__init__(
            builder_name,
            builder_entry_dictionary,
            build_context)

        assert self.builder_type == 'sphinx'

        self.sphinx_sourcedir = None
        self.doxygen_xml_directory = None
        configuration_file_path = build_context.configuration_file_path
        if not os.path.exists(configuration_file_path):
            # This can be the case if the default config is used from a string.
            # Use package.xml instead.
            configuration_file_path = self.build_context.package.filename
        configuration_file_dir = os.path.abspath(os.path.dirname(configuration_file_path))
        logger.debug(f'configuration_file_path is {configuration_file_path}')
        # Process keys.
        for key, value in builder_entry_dictionary.items():
            if key in ['name', 'output_dir']:
                continue
            if key == 'sphinx_sourcedir':
                sphinx_sourcedir = os.path.join(configuration_file_dir, value)
                if not os.path.isdir(sphinx_sourcedir):
                    raise RuntimeError(
                        f"Error Sphinx SOURCEDIR '{value}' does not exist relative "
                        f"to '{configuration_file_path}', or is not a directory.")
                self.sphinx_sourcedir = sphinx_sourcedir
            elif key == 'doxygen_xml_directory':
                self.doxygen_xml_directory = value
                # Must check for the existence of this later, as it may not have been made yet.
            else:
                raise RuntimeError(f"Error the Sphinx builder does not support key '{key}'")

    def build(self, *, doc_build_folder, output_staging_directory):
        """Actually do the build."""
        logger.info(f'running sphinx builder with doc_build_folder {doc_build_folder}')
        logger.info(f'specified sphinx_sourcedir is {self.sphinx_sourcedir}')

        # Check that doxygen_xml_directory exists relative to output staging, if specified.
        if self.doxygen_xml_directory is not None:
            # doxygen_xml_directory is defined in defaults, but won't exist if doxygen did not run
            self.doxygen_xml_directory = \
                os.path.join(output_staging_directory, self.doxygen_xml_directory)
            self.doxygen_xml_directory = os.path.abspath(self.doxygen_xml_directory)

            if not os.path.isdir(self.doxygen_xml_directory):
                self.doxygen_xml_directory = None
                logger.info('No doxygen_xml_directory found, apparently doxygen did not run')
                if self.build_context.always_run_doxygen:
                    raise RuntimeError(
                        f"Error the 'doxygen_xml_directory' specified "
                        f"'{self.doxygen_xml_directory}' does not exist.")

        should_run_sphinx_apidoc = \
            self.build_context.build_type == 'ament_python' or \
            self.build_context.ament_cmake_python or \
            self.build_context.always_run_sphinx_apidoc

        # Check if the user provided a sourcedir.
        user_doc_dir = self.sphinx_sourcedir
        if user_doc_dir is not None:
            # We do not need to check if this directory exists, as that was done in __init__.
            logger.info(
                f"Note: the user provided sourcedir for Sphinx '{user_doc_dir}' will be used.")
            # Run the sphinx project in the user_doc_dir
            sphinx_sourcedir = user_doc_dir
        else:
            # If the user does not supply a Sphinx sourcedir, check the standard locations.
            standard_sphinx_sourcedir = self.locate_sphinx_sourcedir_from_standard_locations()
            if standard_sphinx_sourcedir is not None:
                logger.info(
                    'Note: no sourcedir provided, but a Sphinx sourcedir located in the '
                    f"location '{standard_sphinx_sourcedir}' will be used.")
                sphinx_sourcedir = standard_sphinx_sourcedir
            else:
                # If the user does not supply a Sphinx sourcedir, and there is no Sphinx project
                # in the conventional location, i.e. '<package dir>/doc', create a temporary
                # Sphinx project in the doc build directory to enable cross-references.
                # TODO: What is this about?
                logger.info(
                    'Note: no sourcedir provided by the user and no Sphinx sourcedir was found '
                    'in the standard locations, therefore using a default Sphinx configuration.')
                sphinx_sourcedir = None

        doclist = {}
        extra_doc_files = []  # files outside of the documentation directory
        if sphinx_sourcedir is not None:
            generated_path = os.path.join(sphinx_sourcedir, 'generated')
            logger.warn(f'Removing {generated_path}')
            #shutil.rmtree(generated_path, ignore_errors=True)
            os.makedirs(generated_path, exist_ok=True)

            # locate all documentation in package
            for root, directories, files in os.walk(sphinx_sourcedir):
                relpath = os.path.relpath(root, sphinx_sourcedir) or '.'
                # Use forward slash path separators in sphinx documents
                relpath = relpath.replace('\\', '/')
                # ensure a valid documentation file exists
                if 'generated' in relpath:
                    continue
                for file in files:
                    (filename, ext) = os.path.splitext(file)
                    if ext in ['.rst', '.md', '.markdown']:
                        if relpath not in doclist:
                            doclist[relpath] = []
                        doclist[relpath].append(filename)

            logger.debug(f'doclist: {doclist}clear')
            # generate a glob rst document for each directory with documents
            for relpath in doclist:
                logger.debug(f'relpath: {relpath}')
                # directories that will be explicitly listed in index.rst
                if relpath in ['.', 'doc']:
                    continue
                docname = '_' + slugify(relpath)  # This is the name that sphinx uses for the file
                filename = docname + '.rst'
                # 'relpath' becomes the title in output. For documents in the standard 'doc'
                # directory, do not include the 'doc/' prefix
                doctitle = relpath[len('doc/'):] if relpath.startswith('doc/') else relpath
                extra_doc_files.append([doctitle, 'generated/' + docname])
                name_underline = '=' * len(doctitle)
                content = subdirectory_rst_template.format_map(
                    {'name': doctitle, 'name_underline': name_underline, 'relpath': relpath})
                sub_path = os.path.join(sphinx_sourcedir, 'generated', filename)
                with open(sub_path, 'w+') as f:
                    f.write(content)
            logger.debug(f'extra_doc_files: {extra_doc_files}')

        # Collect intersphinx mapping extensions from discovered inventory files.
        inventory_files = \
            collect_inventory_files(self.build_context.tool_options.cross_reference_directory)
        base_url = self.build_context.tool_options.base_url
        intersphinx_mapping_extensions = [
            f"'{package_name}': "
            f"('{base_url}/{package_name}/{inventory_dict['location_data']['relative_root']}', "
            f"'{esc_backslash(os.path.abspath(inventory_dict['inventory_file']))}')"
            for package_name, inventory_dict in inventory_files.items()
            # Exclude ourselves.
            if package_name != self.build_context.package.name
        ]

        package_xml_directory = os.path.dirname(self.build_context.package.filename)
        # If 'python_source' is specified, construct 'package_src_directory' from it
        if self.build_context.python_source is not None:
            package_src_directory = \
                os.path.abspath(os.path.join(
                    package_xml_directory,
                    self.build_context.python_source))
        # If not provided, try to find the package source direcotry
        else:
            package_list = setuptools.find_packages(where=package_xml_directory)
            if self.build_context.package.name in package_list:
                package_src_directory = os.path.abspath(os.path.join(
                    package_xml_directory,
                    self.build_context.package.name))
            else:
                package_src_directory = None

        breathe_projects = []
        if self.doxygen_xml_directory is not None:
            breathe_projects.append(
                f'        "{self.build_context.package.name} Doxygen Project": '
                f'"{esc_backslash(self.doxygen_xml_directory)}"')

        # Generate rst documents for standard documents
        standard_docs = self.locate_standard_documents()
        self.generate_standard_document_files(standard_docs, sphinx_sourcedir)

        # Generate rst documents for interfaces
        interface_counts = generate_interface_docs(
            package_xml_directory,
            self.build_context.package.name,
            os.path.join(sphinx_sourcedir, 'generated')
        )
        logger.info(f'interface_counts: {interface_counts}')

        # Prepare a list of viable metapackage packages
        meta_dependencies = []
        # A meta package has no build dependencies, only exec dependencies
        if len(self.build_context.package.build_depends) == 0:
            for dependency in self.build_context.package.exec_depends:
                if dependency.name in inventory_files:
                    meta_dependencies.append(dependency.name)
                else:
                    logger.warning(
                        f'Meta package dependency {dependency.name} not found in cross_references')
            logger.info(f'Meta dependencies: {meta_dependencies}')

        # Prepare the template variables for formatting strings.
        self.template_variables = generate_template_variables(
            intersphinx_mapping_extensions,
            breathe_projects,
            self.build_context,
            sphinx_sourcedir,
            package_src_directory,
            user_doc_dir,
            standard_docs,
            interface_counts,
            meta_dependencies,
            extra_doc_files,
            doclist
        )

        logger.debug(f'template_variables: {self.template_variables}')
        # Setup rosdoc2 Sphinx file which will include and extend the one in `user_doc_dir`.

        self.ensure_configurations(sphinx_sourcedir)

        self.generate_wrapping_rosdoc2_sphinx_project_into_directory(
            sphinx_sourcedir)

        # Generate a file as target for index and search in toc
        index_and_search_rst_path = os.path.join(
            sphinx_sourcedir, 'generated', 'index_and_search.rst')
        with open(index_and_search_rst_path, 'w+') as f:
            f.write(index_search_rst)

        if should_run_sphinx_apidoc:
            if not package_src_directory or not os.path.isdir(package_src_directory):
                logger.warning(
                    'Could not locate source directory to invoke sphinx-apidoc in. '
                    'If this is package does not have a standard Python package layout, '
                    'please specify the Python source in "rosdoc2.yaml".')
            else:
                output_directory = os.path.join(sphinx_sourcedir, 'generated/python')
                cmd = [
                    'sphinx-apidoc',
                    '-o', os.path.relpath(output_directory, start=sphinx_sourcedir),
                    '-e',  # Document each module in its own page.
                    '-M',  # Put module documentation before submodules
                    '-f',  # Overwrite any existing generated files
                    os.path.abspath(package_src_directory),
                ]
                logger.info(
                    f"Running sphinx-apidoc: '{' '.join(cmd)}' in '{sphinx_sourcedir}'"
                )
                completed_process = subprocess.run(cmd, cwd=sphinx_sourcedir)
                msg = f"sphinx-apidoc exited with return code '{completed_process.returncode}'"
                if completed_process.returncode == 0:
                    logger.info(msg)
                else:
                    raise RuntimeError(msg)

        # Invoke Sphinx-build.
        working_directory = sphinx_sourcedir
        sphinx_output_dir = os.path.abspath(os.path.join(sphinx_sourcedir, 'sphinx_output'))
        cmd = [
            'sphinx-build',
            '-c', os.path.relpath(sphinx_sourcedir, start=working_directory),
            os.path.relpath(sphinx_sourcedir, start=working_directory),
            sphinx_output_dir,
        ]
        logger.info(
            f"Running Sphinx-build: '{' '.join(cmd)}' in '{working_directory}'"
        )

        completed_process = subprocess.run(cmd, cwd=working_directory)
        msg = f"Sphinx-build exited with return code '{completed_process.returncode}'"
        if completed_process.returncode == 0:
            logger.info(msg)
        else:
            raise RuntimeError(msg)

        # Copy the inventory file into the cross-reference directory, but also leave the output.
        inventory_file_name = os.path.join(sphinx_output_dir, 'objects.inv')
        destination = os.path.join(
            self.build_context.tool_options.cross_reference_directory,
            self.build_context.package.name,
            os.path.basename(inventory_file_name))
        logger.info(
            f"Moving inventory file '{inventory_file_name}' into "
            f"cross-reference directory '{destination}'")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(
            os.path.abspath(inventory_file_name),
            os.path.abspath(destination)
        )

        # Create a .location.json file as well, so we can know the relative path to the root
        # of the sphinx content from the package's documentation root.
        data = {
            'relative_root': self.output_dir,
        }
        with open(os.path.abspath(destination) + '.location.json', 'w+') as f:
            f.write(json.dumps(data))
        # Put it with the Sphinx generated content as well.
        with open(os.path.abspath(inventory_file_name) + '.location.json', 'w+') as f:
            f.write(json.dumps(data))

        # Return the directory into which Sphinx generated.
        return sphinx_output_dir

    def ensure_configurations(self, directory):
        """Generate if needed the default project configuration files."""
        os.makedirs(directory, exist_ok=True)

        # if the package provided conf.py, use it
        use_package_conf_py = False
        conf_py = os.path.join(directory, 'conf.py')
        if os.path.exists(conf_py):
            # Check if it is generated.
            with open(conf_py, 'r') as f:
                firstline = f.readline()
            if 'GENERATED_CONTENT' not in firstline:
                logger.info('Using conf.py provided by the package')
                use_package_conf_py = True

        if not use_package_conf_py:
            # Generate conf.py from a template
            # If the package provides index.j2.rst, use it
            conf_j2 = os.path.join(directory, 'conf.j2.py')
            if os.path.exists(conf_j2):
                with open(conf_j2, 'r') as f:
                    conf_j2_template = f.read()
                logger.info('Using conf.j2.py provided by the package')

            # Otherwise, use the default conf.j2.py
            else:
                logger.info('Using a default conf.j2.py')
                conf_j2_template = \
                    pkg_resources.resource_string(__name__, 'templates/conf.j2.py').decode('utf-8')

            conf_py = Template(conf_j2_template).render(self.template_variables)
            conf_py_path = os.path.join(directory, 'conf.py')
            with open(os.path.join(conf_py_path), 'w+') as f:
                f.write(conf_py)

        # If the package provided index.j2.rst, use it
        index_rst = os.path.join(directory, 'index.rst')
        use_package_index_rst = False
        if os.path.exists(index_rst):
            # Check if it is generated.
            with open(index_rst, 'r') as f:
                firstline = f.readline()
            if 'GENERATED_CONTENT' not in firstline:
                logger.info('Using index.rst provided by the package')
                use_package_index_rst = True

        if not use_package_index_rst:
            # Generate index.rst from a template

            # If the package provides index.j2.rst, use it
            index_j2 = os.path.join(directory, 'index.j2.rst')
            if os.path.exists(index_j2):
                with open(index_j2, 'r') as f:
                    index_j2_template = f.read()
                logger.info('Using index.j2.rst provided by the package')

            # Otherwise, use the default index.j2.rst
            else:
                logger.info('Using a default index.j2.rst')
                index_j2_template = pkg_resources.resource_string(
                    __name__, 'templates/index.j2.rst').decode('utf-8')

            index_rst = Template(index_j2_template).render(self.template_variables)
            index_rst_path = os.path.join(directory, 'index.rst')
            with open(os.path.join(index_rst_path), 'w+') as f:
                f.write(index_rst)

    def locate_sphinx_sourcedir_from_standard_locations(self):
        """
        Return the location of a Sphinx project for the package.

        If the sphinx configuration exists in a standard location, return it,
        otherwise return None.  The standard locations are
        '<package.xml directory>/doc/source/conf.py' and
        '<package.xml directory>/doc/conf.py', for projects that selected
        "separate source and build directories" when running Sphinx-quickstart and
        those that did not, respectively.
        If these directories exist but without conf.py, they will be used with a default conf.py
        """
        package_xml_directory = os.path.dirname(self.build_context.package.filename)
        options = [
            package_xml_directory,
            os.path.join(package_xml_directory, 'doc', 'source'),
            os.path.join(package_xml_directory, 'doc'),
            os.path.join(package_xml_directory, 'docs', 'source'),
            os.path.join(package_xml_directory, 'docs'),
        ]
        for option in options:
            conf_py = os.path.join(option, 'conf.py')
            if os.path.isfile(conf_py):
                # Check if it is generated.
                with open(conf_py, 'r') as f:
                    firstline = f.readline()
                if 'GENERATED_CONTENT' not in firstline:
                    return option
            if os.path.isfile(os.path.join(option, 'conf.j2.py')):
                return option

        # Otherwise, use the project root
        return os.path.join(package_xml_directory)

    def generate_wrapping_rosdoc2_sphinx_project_into_directory(
        self,
        directory,
    ):
        """Generate the rosdoc2 sphinx project configuration files."""
        logger.info(f'Generating sphinx project into directory {directory}')
        os.makedirs(directory, exist_ok=True)

        user_conf_py_path = os.path.abspath(os.path.join(directory, 'conf.py'))
        logger.info(f'Using conf.py at path {user_conf_py_path}')
        user_conf_py = open(user_conf_py_path).read()

        # Execute conf.py and get values of variables
        conf_globals = {'logger': logger}
        conf_locals = {}
        exec(user_conf_py, conf_globals, conf_locals)

        # Convert any paths to absolute paths.
        conf_relpath = os.path.relpath(directory)
        for key, value in conf_locals.items():
            if not key.endswith('_path'):
                continue
            if isinstance(value, str):
                conf_locals[key] = os.path.abspath(os.path.join(conf_relpath, value))
            elif isinstance(value, (list, tuple)):
                abs_paths = []
                for item in value:
                    abs_paths.append(os.path.abspath(os.path.join(conf_relpath, item)))
                conf_locals[key] = abs_paths

        # Setup rosdoc2 Sphinx file which will include and extend the one in `sourcedir`.
        wrapped_conf_py = rosdoc2_wrapping_conf_py_preamble
        for key, value in conf_locals.items():
            if isinstance(value, (bool, int, float, list, dict, tuple)):
                wrapped_conf_py += f'{key} = {value}\n'
            elif isinstance(value, str):
                wrapped_conf_py += f'{key} = "{value}"\n'
        wrapped_conf_py += rosdoc2_wrapping_conf_py_template.format_map(self.template_variables)
        with open(os.path.join(directory, 'conf.py'), 'w+') as f:
            f.write(wrapped_conf_py)

    def locate_standard_documents(self):
        """Locate standard documents."""
        names = ['readme', 'license', 'contributing', 'changelog']
        found_paths = {}
        package_xml_directory = os.path.dirname(self.build_context.package.filename)
        package_directory_items = os.listdir(package_xml_directory)
        for item in package_directory_items:
            itempath = os.path.join(package_xml_directory, item)
            if not os.path.isfile(itempath):
                continue
            (basename, ext) = os.path.splitext(item)
            for name in names:
                if name in found_paths:
                    continue
                if basename.lower() == name:
                    filetype = None
                    if ext.lower() == '.md':
                        filetype = 'md'
                    elif ext.lower() == '.rst':
                        filetype = 'rst'
                    else:
                        filetype = 'other'
                    found_paths[name] = {
                        'path': os.path.abspath(package_xml_directory),
                        'filename': item,
                        'type': filetype
                    }
        return found_paths

    def generate_standard_document_files(self, standard_docs, sphinx_sourcedir):
        """Generate rst documents to link to standard documents."""
        sphinx_sourcedir = os.path.abspath(sphinx_sourcedir)
        if len(standard_docs):
            # Create the standards.rst document that will link to the actual documents
            standard_path = os.path.join(sphinx_sourcedir, 'generated', 'standard')
            os.makedirs(standard_path, exist_ok=True)
            standard_documents_rst_path = os.path.join(
                sphinx_sourcedir, 'generated', 'standards.rst')
            with open(standard_documents_rst_path, 'w+') as f:
                f.write(standard_documents_rst)

        for key, standard_doc in standard_docs.items():
            relative_dir = os.path.relpath(standard_doc['path'], standard_path)
            relative_path = os.path.join(relative_dir, standard_doc['filename'])
            # generate the file according to type
            file_contents = f'{key.upper()}\n'
            # using ')' as a header marker to assure the name is the title
            file_contents += ')' * len(key) + '\n\n'
            file_type = standard_doc['type']
            if file_type == 'rst':
                file_contents += f'.. include:: {relative_path}\n'
            elif file_type == 'md':
                file_contents += f'.. include:: {relative_path}\n'
                file_contents += '   :parser: myst_parser.sphinx_\n'
            else:
                file_contents += f'.. literalinclude:: {relative_path}\n'

            with open(os.path.join(standard_path, f'{key.upper()}.rst'), 'w+') as f:
                f.write(file_contents)
