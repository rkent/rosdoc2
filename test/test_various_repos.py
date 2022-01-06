# Copyright 2021 R. Kent James <kent@caspia.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile

from catkin_pkg.package import parse_package

# 'pytest_virtualenv' required, supplies virtualenv


def package_smoke_test(package, virtualenv):
    (url, commit, package_relative_path, test_files) = package

    print(f'*** package url: {url} path: {package_relative_path}')
    fp_save = None
    fp_save = tempfile.mkdtemp()
    with tempfile.TemporaryDirectory() as fp_delete:
        fp = fp_save or fp_delete
        print(f'temp directory is {fp}')

        virtualenv.run(['git', '-C', f'{fp}', 'clone', f'{url}', 'repo'])
        repo_path = os.path.join(fp, 'repo')
        package_path = os.path.join(repo_path, package_relative_path)
        package = parse_package(package_path)
        # -q to suppress detached head message
        virtualenv.run(['git', '-C', f'{repo_path}', 'checkout', '-q', f'{commit}'])
        (docs_cr, docs_output, docs_build) = ('docs_cr', 'docs_output', 'docs_build')
        args_str = '['\
            + '"build"'\
            + f', "-p", "{package_path}"'\
            + f', "-c", "{os.path.join(package_path, docs_cr)}"'\
            + f', "-o", "{os.path.join(package_path, docs_output)}"'\
            + f', "-d", "{os.path.join(package_path, docs_build)}"'\
            + ', "--debug"]'
        runme = [
            'python',
            '-c', f'from rosdoc2 import main; main.main({args_str})'
        ]
        outs = virtualenv.run(runme, capture=True)

        # test existence of specified output files and some content
        docs_output_path = os.path.join(package_path, docs_output, package.name)
        for test_file in test_files:
            (filename, test_string) = test_file
            print(f'testing path <{package_path}> filename <{filename}> content <{test_string}>')
            file_path = os.path.join(docs_output_path, filename)
            assert os.path.exists(file_path)
            content = open(file_path).read()
            if test_string:
                if test_string.startswith('!'):
                    assert not test_string[1:] in content
                else:
                    assert test_string in content

        print('--- rosdoc2 output ---')
        print(outs)


# projects to test as tuples of (repo_url, git_commit, package_relative_path, testfiles)
# testfiles is a list of tuples of (filename, text_to_find)
# if text_to_find starts with !, assert that the remainder of the string is NOT present
TEST_PACKAGES = \
    [
        [
            'https://github.com/ros-planning/moveit2.git', '2.3.2', 'moveit_kinematics',
            [
                # Confirm that we find the repository URL
                ('index.html', 'https://github.com/ros-planning/moveit2'),
                # Confirm that rosindex link is found
                ('index.html', 'https://index.ros.org/p/moveit_kinematics'),
                # The index should have the description
                ('index.html', 'Package for all inverse kinematics solvers in MoveIt'),
            ]
        ],
        [
            'https://github.com/rosdabbler/fqdemo.git', 'HEAD', 'fqdemo_nodes',
            [
                # Basic existence of output
                ('index.html', ''),
                # Confirm that rosindex link is NOT found
                ('index.html', '!https://index.ros.org/p/'),
            ]
        ],
    ]


def test_packages(virtualenv):
    """Confirm that rosdoc2 runs to completion in these packages."""
    virtualenv.install_package(f'install {os.getcwd()}', installer='pip')
    for package in TEST_PACKAGES:
        package_smoke_test(package, virtualenv)
