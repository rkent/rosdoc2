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

import os


def create_format_map_from_package(package):
    """Create a dictionary used in format strings using a package object."""
    stripped_description = ' '.join(package.description.split())
    package_directory = os.path.abspath(os.path.dirname(package.filename))
    # Locate possible python src directory
    python_src = None
    if os.path.isdir(os.path.join(package_directory, package.name)):
        python_src = package.name
    elif os.path.isdir(os.path.join(package_directory, f'src/{package.name}')):
        python_src = f'src/{package.name}'
    return {
        'package_name': package.name,
        'package_version': package.version,
        'package_description': stripped_description,
        'package_directory': package_directory,
        'python_src': python_src
    }
