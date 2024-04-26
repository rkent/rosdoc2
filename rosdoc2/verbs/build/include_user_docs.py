# Copyright 2024 Open Source Robotics Foundation, Inc.
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

import logging
import os
import shutil

from rosdoc2.slugify import slugify

logger = logging.getLogger('rosdoc2')

documentation_rst_template = """\
Documentation
=============

.. toctree::
   :maxdepth: 1
   :glob:

   *
"""

subdirectory_rst_template = """\
{name}/
{name_underline}=

.. toctree::
   :caption: Documentation in this subdirectory
   :maxdepth: 2
   :glob:

   {name}/*
"""


def locate_documentation(
        package_xml_directory: str, relative_user_doc_dir: str):
    """Return the location of Sphinx documentation for the package.

    Directories searched are 'relative_user_doc_dir' (if specified), else ['doc/', 'doc/source'].
    :param package_xml_directory[str]: absolute path to the package.xml files's directory
    :param relative_user_doc_dir[str or None]:
        If None, look for documentation in standard locations doc/, doc/source/
        Otherwise, start search for documentation in this directory (relative to package.xml)
    :return: [relative_user_doc_dir, doc_directories]
        'relative_user_doc_dir' is the inputted value (if provided), else the root of the docs.
            The root is the highest directory with a conf.py, else the highest level with
            renderable documentation.
        'doc_directories' is a list of relative directories containing renderable documentation.
    """
    options = [
        'doc',
        'doc/source',
    ]
    if not relative_user_doc_dir:
        for option in options:
            if os.path.isfile(os.path.join(package_xml_directory, option, 'conf.py')):
                relative_user_doc_dir = option
                break

    # Also look for directories with renderable files.
    doc_directories = []
    if relative_user_doc_dir:
        options = [relative_user_doc_dir]
    for option in options:
        doc_dir = os.path.join(package_xml_directory, option)
        for root, _, files in os.walk(doc_dir):
            for file in files:
                # ensure a documentation file exists, directories might only contain resources.
                (_, ext) = os.path.splitext(file)
                if ext in ['.rst', '.md', '.markdown']:
                    logger.info(f'Found renderable documentation file in {root} named {file}')
                    relpath = os.path.relpath(root, doc_dir)
                    relpath = relpath.replace('\\', '/')
                    doc_directories.append(relpath)
                    break
        if doc_directories and not relative_user_doc_dir:
            relative_user_doc_dir = option
            break

    if not doc_directories:
        logger.info('no documentation found')

    return relative_user_doc_dir, doc_directories


def include_user_docs(package_xml_directory: str,
                      wrapped_sphinx_directory: str,
                      sphinx_sourcedir: str,
                      ):
    """Locate and prepare user documentation in wrapped_sphinx_directory."""
    # Check if the user provided a sphinx directory, ie a directory with documention.
    # 'user_doc_directory' => absolute location of user documentation.
    relative_user_doc_dir = None
    user_doc_directory = None
    if sphinx_sourcedir:
        if os.path.isdir(sphinx_sourcedir):
            user_doc_directory = sphinx_sourcedir
            relative_user_doc_dir = os.path.relpath(sphinx_sourcedir, package_xml_directory)
            logger.info(
                'The user provided sourcedir for Sphinx '
                f"'{user_doc_directory}' (relative {relative_user_doc_dir}) will be used.")
        else:
            logger.warning(
                f'User-specified sphinx_sourcedir "{sphinx_sourcedir}" does not exist')
            sphinx_sourcedir = None

    # Locate renderable documentation
    found_user_doc_dir, doc_directories = locate_documentation(
        package_xml_directory, relative_user_doc_dir)
    logger.info(f'doc_directories: {doc_directories}')
    if found_user_doc_dir:
        if not sphinx_sourcedir:
            relative_user_doc_dir = found_user_doc_dir
            user_doc_directory = os.path.join(package_xml_directory, found_user_doc_dir)
            logger.info(
                'Note: no sourcedir provided, but a Sphinx sourcedir was located in the '
                f"standard location '{found_user_doc_dir}' and that will be used.")
    else:
        if sphinx_sourcedir:
            logger.warning(
                f"User specified Sphinx directory '{sphinx_sourcedir}' "
                'has no renderable documentation.')
        else:
            logger.info('No renderable user documentation found')

    # if we have user documentation, copy that into the build folder.
    if relative_user_doc_dir:
        sphinx_project_directory = os.path.join(wrapped_sphinx_directory, relative_user_doc_dir)
        try:
            shutil.copytree(user_doc_directory, sphinx_project_directory)
        except OSError as e:
            logger.error(f'Failed to copy documentation content: {e}')
            relative_user_doc_dir = None
            doc_directories = []

    if relative_user_doc_dir:
        # if the documention directory has an index.rst, we will just use that. Otherwise, we will
        # generate it by scanning for renderable documentation
        if not os.path.isfile(os.path.join(sphinx_project_directory, 'index.rst')):
            # generate a glob rst entry for each directory with documents
            for relpath in doc_directories:
                # directories that will be explicitly listed in index.rst
                if relpath == '.':
                    continue
                # This is the name sphinx uses
                docname = '_index_' + slugify(relpath)
                template_map = {
                    'name': relpath,
                    'name_underline': '=' * len(relpath),
                }
                content = subdirectory_rst_template.format_map(template_map)
                sub_path = os.path.join(sphinx_project_directory, docname + '.rst')
                with open(sub_path, 'w+') as f:
                    f.write(content)

                index_path = os.path.join(sphinx_project_directory, 'index.rst')
                with open(index_path, 'w+') as f:
                    f.write(documentation_rst_template)

    return relative_user_doc_dir, doc_directories
