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

"""testing of builder.py using pytest"""

import argparse
from html.parser import HTMLParser
import pathlib

from rosdoc2.verbs.build.impl import prepare_arguments, main_impl

DATAPATH = pathlib.Path('test/data')

class htmlParser(HTMLParser):
    """Minimal html parsing collecting tags"""
    def __init__(self):
        super().__init__()
        self.tags = []
        self.content = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append({'tag': tag, 'attrs': attrs})

    def handle_data(self, data):
        data_black = data.strip(' \n')
        if self.tags and data_black:
            self.tags[-1]['data'] = data_black.lower()
            print(self.tags[-1])
            self.content.add(data_black.lower())


def test_minimal_package(tmp_path):
    # Testing of an empty as possible package
    PKG_NAME = 'minimum_package'
    build_dir = tmp_path / 'build'
    output_dir = tmp_path / 'output'
    cr_dir = tmp_path / "cross_references"
    package_path = DATAPATH / PKG_NAME

    # Create a top level parser
    parser = prepare_arguments(argparse.ArgumentParser())
    options = parser.parse_args([
        '-p', str(package_path.resolve()),
        '-c', str(cr_dir),
        '-o', str(output_dir),
        '-d', str(build_dir),
    ])

    main_impl(options)

    index_path = output_dir / PKG_NAME / 'index.html'
    # smoke test
    assert index_path.is_file(),\
        'html index file exists'

    # read and parse the index file
    index_content = index_path.read_text()
    assert len(index_content) > 0, \
        "index.html is not empty"

    parser = htmlParser()
    parser.feed(index_content)

    # package name exists (as a link)
    assert PKG_NAME in parser.content, \
        'package name exists in html'

    assert 'project documentation' not in parser.content, \
        'A package with no documents should not have a project documentation line'

    assert 'repository' not in parser.content, \
        'Has no repository text'
    
    assert 'website' not in parser.content, \
        'Has no website text'

    assert 'bugtracker' not in parser.content, \
        'Has no bugtracker text'

def test_full_package(tmp_path):
    # Test of a full-featured cmake package
    PKG_NAME = 'full_package'
    build_dir = tmp_path / 'build'
    output_dir = tmp_path / 'output'
    cr_dir = tmp_path / "cross_references"
    package_path = DATAPATH / PKG_NAME

    # Create a top level parser
    parser = prepare_arguments(argparse.ArgumentParser())
    options = parser.parse_args([
        '-p', str(package_path.resolve()),
        '-c', str(cr_dir),
        '-o', str(output_dir),
        '-d', str(build_dir),
    ])

    main_impl(options)

    index_path = output_dir / PKG_NAME / 'index.html'
    # smoke test
    assert index_path.is_file(),\
        'html index file exists'

    # read and parse the index file
    index_content = index_path.read_text()
    assert len(index_content) > 0, \
        "index.html is not empty"

    parser = htmlParser()
    parser.feed(index_content)

    assert 'repository' in parser.content, \
        'Has repository text'
    
    assert 'website' in parser.content, \
        'Has website text'

    assert 'bugtracker' in parser.content, \
        'Has bugtracker text'
