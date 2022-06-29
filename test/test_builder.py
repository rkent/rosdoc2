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

"""Test build using pytest."""

import argparse
from html.parser import HTMLParser
import logging
import pathlib
from urllib.parse import urlparse

import pytest
from rosdoc2.verbs.build.impl import main_impl, prepare_arguments

DATAPATH = pathlib.Path('test/data')


@pytest.fixture(scope='module')
def tmp_path(tmpdir_factory):
    """Create a temporary path for use over the entire test."""
    return pathlib.Path(tmpdir_factory.mktemp('test_builder'))


logger = logging.getLogger('test_builder')
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
        # text data we have seen
        self.content = set()
        # href in <a> tags we have seen
        self.links = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append({'tag': tag, 'attrs': attrs})
        if tag == 'a':
            for (name, link) in attrs:
                if name == 'href':
                    self.links.add(link)
                    logger.debug(f'link: {link}')

    def handle_data(self, data):
        data_unwhite = data.strip(' \n')
        if self.tags and data_unwhite:
            self.tags[-1]['data'] = data_unwhite
            # logger.debug(f'tag: {self.tags[-1]}')
            self.content.add(data_unwhite)


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
        assert item in parser.content, \
            f'html has content {item}'

    # test exclusions
    for item in excludes:
        assert item not in parser.content, \
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
            if item == link:
                found_item = link
        assert found_item, \
            f'a link should exist "{item}"'
        link_object = urlparse(found_item)
        if not link_object.scheme:
            # This is a relative link. Look for that file.
            link_path = output_dir / name / link_object.path
        else:
            assert link_object.scheme == 'file', \
                f'link {found_item} should be of type file'
            link_path = pathlib.Path(link_object.path)
        assert link_path.is_file(), \
            f'file represented by {found_item} should exist at {link_path}'


def test_minimum_package(tmp_path):
    pkg_name = 'minimum_package'
    path = tmp_path

    do_build_package(DATAPATH / pkg_name, path)

    includes = [
        pkg_name,
        'Indices and Search',
    ]

    excludes = [
        'Class Hierarchy'
    ]

    do_test_package(pkg_name, path, includes, excludes)


def test_cpp_package(tmp_path):
    pkg_name = 'cpp_package'
    path = tmp_path

    do_build_package(DATAPATH / pkg_name, path)

    includes = [
        pkg_name,
        'Indices and Search',
        'Class Hierarchy',
    ]

    links_exist = [
        'generated/index.html'
    ]

    file_includes = [
        'generated/namespace_cpp_package.html',
    ]

    do_test_package(
        pkg_name, path, includes,
        file_includes=file_includes,
        links_exist=links_exist,
    )
