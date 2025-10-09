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

logger = logging.getLogger('rosdoc2')


def collect_tag_files(cross_reference_directory, package):
    """Collect all Doxygen tag files for a package."""
    # Generate dependencies.
    dependencies = set()
    for deptype in ['build_depends', 'exec_depends', 'doc_depends']:
        for dep in package[deptype]:
            dependencies.add(dep.name)
    logger.info(f'Collecting tag files for dependencies: {dependencies}')

    tag_files = {}
    for dep in dependencies:
        tag_file_path = os.path.join(cross_reference_directory, dep, f'{dep}.tag')
        location_json_path = tag_file_path + '.location.json'
        if not os.path.exists(tag_file_path) or not os.path.exists(location_json_path):
            continue
        location_data = None
        with open(location_json_path, 'r+') as f:
            location_data = json.loads(f.read())
        tag_files[dep] = {
            'tag_file': tag_file_path,
            'location_data': location_data,
        }
    return tag_files
