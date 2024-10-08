# Copyright 2024 R. Kent James <kent@caspia.com>
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

from .impl import main
from .impl import prepare_arguments

__all__ = [
    'entry_point_data',
]

entry_point_data = {
    'verb': 'scan',
    'description': 'Scan subdirectories looking for packages, then build those packages.',
    # Called for execution, given parsed arguments object
    'main': main,
    # Called first to setup argparse, given argparse parser
    'prepare_arguments': prepare_arguments,
}
