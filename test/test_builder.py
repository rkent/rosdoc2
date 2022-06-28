# Copyright 2022 Open Source Robotics Foundation, Inc.
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

"""Test builder.py using pytest."""

import argparse
from html.parser import HTMLParser
import logging
import pathlib
from urllib.parse import urlparse

import pytest
from rosdoc2.verbs.build.impl import main_impl, prepare_arguments

DATAPATH = pathlib.Path('test/data')
METAPATH = DATAPATH / 'meta'


@pytest.fixture(scope='module')
def tmp_path(tmpdir_factory):
    """Create a temporary path for use over the entire test."""
    return pathlib.Path(tmpdir_factory.mktemp('test_builder'))


@pytest.fixture(scope='module')
def many_path(tmp_path):
    """Generate 'once' documentation over all packages under DATAPATH."""
    do_build_package(METAPATH, tmp_path)
    return tmp_path


logger = logging.getLogger('rosdoc2')
formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class htmlParser(HTMLParser):
    """Minimal html parsing collecting tags."""

    def __init__(self):
        super().__init__()
        self.tags = []
        # data we have seen
        self.content = set()
        # href in <a> tags we have seen
        self.links = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append({'tag': tag, 'attrs': attrs})
        if tag == 'a':
            for (name, link) in attrs:
                if name == 'href':
                    self.links.add(link)

    def handle_data(self, data):
        data_black = data.strip(' \n')
        if self.tags and data_black:
            self.tags[-1]['data'] = data_black.lower()
            logger.debug(f'tag: {self.tags[-1]}')
            self.content.add(data_black.lower())


def do_build_package(package_path, path) -> None:
    build_dir = path / 'build'
    output_dir = path / 'output'
    cr_dir = path / 'cross_references'

    # Create a top level parser
    parser = prepare_arguments(argparse.ArgumentParser())
    options = parser.parse_args([
        '-p', str(package_path),
        '-c', str(cr_dir),
        '-o', str(output_dir),
        '-d', str(build_dir),
    ])
    logger.info(f'*** Building package(s) at {package_path} with options {options}')

    # run rosdoc2 on the package
    main_impl(options)


def do_test_package(
    name,
    work_path,
    includes=[],
    excludes=[],
    file_includes=[],
    file_excludes=[],
    links_exist=[],
) -> None:
    """Test that package documentation exists and includes/excludes certain text.

    :param str work_path: path where generated files will be placed
    :param list[str] includes: lower case text found in index.html data
    :param list[str] excludes: lower case text not found in index.html data
    :param list[str] file_includes: path to files
        (relative to root index.html directory) of files that should exist
    :param list[str] file_excludes: path to files
        (relative to root index.html directory) of files that should not exist
    :param list[str] links_exist: Confirm that 1) a link exists containing this text, and
        2) the link is a valid file
    """
    logger.info(f'*** Testing package {name} work_path {work_path}')
    output_dir = work_path / 'output'

    # tests on the main index.html
    index_path = output_dir / name / 'index.html'

    # smoke test
    assert index_path.is_file(),\
        'html index file exists'

    # read and parse the index file
    #
    # The package title html has a permalink icon at the end which is
    # a unicode character. For some reason, on Windows this character generates
    # a unicode error in Windows, though it seems to work fine
    # in the browser. So ignore unicode errors.
    with index_path.open(mode='r', errors='replace') as f:
        index_content = f.read()
    assert len(index_content) > 0, \
        'index.html is not empty'

    parser = htmlParser()
    parser.feed(index_content)

    # test inclusions
    for item in includes:
        assert item.lower() in parser.content, \
            f'html has content {item}'

    # test exclusions
    for item in excludes:
        assert item.lower() not in parser.content, \
            f'html does not have content {item}'

    # file inclusions
    for item in file_includes:
        path = output_dir / name / item
        assert path.is_file(), \
            f'file {item} should exist'

    # file exclusions
    for item in file_excludes:
        path = output_dir / name / item
        assert not path.is_file(), \
            f'file {item} should not exist'

    # look for links
    for item in links_exist:
        found_item = None
        for link in parser.links:
            if item in link:
                found_item = link
        assert found_item, \
            f'a link should exist containing the string {item}'
        link_object = urlparse(found_item)
        assert link_object.scheme == 'file', \
            f'link {found_item} should be of type file'
        link_path = pathlib.Path(link_object.path)
        assert link_path.is_file(), \
            f'file represented by {found_item} should exist'


def test_meta_dependencies(many_path):
    """Build dependencies to the meta package."""
    path = many_path
    # This packages are rebuilt, as the first time they do not have
    # links from pervious builds to these packages.
    do_build_package(METAPATH / 'meta_package', path)

    includes = ['Dependencies of this Meta Package']
    links_exist = ['full_package/index.html']
    do_test_package('meta_package', path, includes, links_exist=links_exist)


# At this point, the full set of packages are built
def test_minimal_package(tmp_path):
    path = tmp_path
    # Testing of an empty as possible package
    PKG_NAME = 'minimum_package'
    do_build_package(DATAPATH / PKG_NAME, path)

    includes = [
        PKG_NAME,
        'Index and Search',
    ]

    excludes = [
        'project documentation',
        'repository',
        'website',
        'bugtracker',
        'project documentation',
        'instructions',
        'full_package package',
        'c/c++ api',
        'Service Definitions',
        'Message Definitions',
        'Package API',
    ]

    do_test_package(PKG_NAME, path, includes, excludes)


def test_full_package(many_path):
    # Test of a full-featured cmake package
    PKG_NAME = 'full_package'

    includes = [
        PKG_NAME,
        'Index and Search',
        'repository',
        'website',
        'bugtracker',
        'project documentation',
        'instructions',
        'full_package package',
        'c/c++ api',
        # Author from package.xml via default conf.j2.py
        '© copyright 2022, some one  (apache license 2.0).',
        # From default index.j2.rst
        'Package API',
        'Standard Documents',
        'Service Definitions',
        'Message Definitions',
        # Additional documentation in subdirectories
        'morestuff',
        'morestuff/more_of_more'
    ]

    excludes = []
    file_includes = [
        'generated/cpp/index.html',
        'generated/cpp/file_include_full_package_iamcpp.hpp.html',
        'generated/standard/CHANGELOG.html',
        'generated/standard/CONTRIBUTING.html',
        'generated/standard/LICENSE.html',
        'generated/standard/README.html',
        'generated/message_definitions.html',
        'generated/service_definitions.html',
        'generated/msg/NumPwrResult.html',
        'generated/srv/NodeCommand.html',
    ]
    file_excludes = [
        'idonotexist.html',  # just a smoke test of the excludes function
    ]
    do_test_package(PKG_NAME, many_path, includes, excludes, file_includes, file_excludes)


def test_user_conf_files(tmp_path):
    # User provides configuration files
    PKG_NAME = 'user_conf_files'
    path = tmp_path
    do_build_package(DATAPATH / PKG_NAME, path)
    includes = [
        PKG_NAME,
        'c/c++ api',
        '© copyright 2021, conf.py author  (apache license 2.0).',  # from conf.py
        # from index.rst
        'testing of index.rst',
        # From index.rst
        'Packages API',
    ]

    excludes = [
    ]
    file_includes = [
        'generated/cpp/index.html',
        'generated/cpp/file_nonstandard_include_user_conf_files_iamcpp.hpp.html',
    ]
    file_excludes = []
    do_test_package(PKG_NAME, path, includes, excludes, file_includes, file_excludes)


def test_user_conf_templates(tmp_path):
    # User provides configuration templates
    PKG_NAME = 'user_conf_templates'
    path = tmp_path
    do_build_package(DATAPATH / PKG_NAME, path)

    includes = [
        PKG_NAME,
        'c/c++ api',
        '© copyright 2021, conf.j2.py author  (apache license 2.0).',  # from conf.j2.py
        'testing of index.j2.rst',  # from index.j2.rst
        # From index.j2.rst
        'Packageses API',
    ]

    excludes = []
    file_includes = [
        'generated/cpp/index.html',
        'generated/cpp/file_nonstandard_include_user_conf_templates_iamcpp.hpp.html',
    ]
    file_excludes = []
    do_test_package(PKG_NAME, path, includes, excludes, file_includes, file_excludes)


def test_only_messages(many_path):
    # A package that only has message definitions
    PKG_NAME = 'only_messages'

    includes = [
        'Project Documentation',
        'Standard Documents',
        'Package API',
        'Message Definitions',
        'NumPwrResult',
    ]
    excludes = []

    do_test_package(PKG_NAME, many_path, includes, excludes)
