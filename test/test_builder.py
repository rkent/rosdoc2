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

"""testing of builder.py using pytest."""

import argparse
import pathlib

from rosdoc2.verbs.build.impl import main_impl, prepare_arguments

DATAPATH = pathlib.Path('test/data')


def test_basic_package(tmp_path):
    build_dir = tmp_path / 'build'
    output_dir = tmp_path / 'output'
    cr_dir = tmp_path / 'cross_references'
    package_path = DATAPATH / 'minimum_package'

    # Create a top level parser
    parser = prepare_arguments(argparse.ArgumentParser())
    options = parser.parse_args([
        '-p', str(package_path.resolve()),
        '-c', str(cr_dir),
        '-o', str(output_dir),
        '-d', str(build_dir),
    ])

    main_impl(options)
