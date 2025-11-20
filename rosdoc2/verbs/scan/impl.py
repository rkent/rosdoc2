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

import logging
import multiprocessing as mp
import os
import signal
import sys
import threading
import time

from catkin_pkg.packages import find_packages_allowing_duplicates
from rosdoc2.verbs.build.impl import main as build_main
from rosdoc2.verbs.build.impl import prepare_arguments as build_prepare_arguments

mp.set_start_method('spawn', force=True)

logging.basicConfig(
    format='[%(name)s] [%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger('rosdoc2')
logger_scan = logging.getLogger('rosdoc2.scan')

# Setting the MAX_PACKAGES to a smaller value may be useful in debugging
# this module, to reduce run time or isolate sections that cause hangs.
MAX_PACKAGES = 10000
WATCHDOG_TIMEOUT = 15 * 60  # Seconds


def main(options):
    """Execute the program, catching errors."""
    try:
        return main_impl(options)
    except Exception as e:  # noqa: B902
        if options.debug:
            raise
        else:
            sys.exit(str(e))


class Struct:
    """Wrap argparse options to allow copies."""

    def __init__(self, **entries):
        """Create a dictionary from option entries."""
        self.__dict__.update(entries)


def prepare_arguments(parser):
    """Add command-line arguments to the argparse object."""
    # Wrap the builder arguments to include their choices.
    build_prepare_arguments(parser)

    # Additional options for scan
    parser.add_argument(
        '--timeout',
        '-t',
        default=WATCHDOG_TIMEOUT,
        help='maximum time in seconds allowed per package (default: %(default)s)',
    )
    parser.add_argument(
        '--max-packages',
        '-m',
        default=MAX_PACKAGES,
        help='maximum number of packages to process (default: %(default)s)'
    )
    parser.add_argument(
        '--subprocesses',
        '-s',
        default=None,
        help='number of subprocesses to use, defaults to os.cpu_count()'
    )
    return parser


def _clocktime():
    return time.strftime('%H:%M:%S')


def package_impl(package, options, had_timeout):
    """Execute for a single package."""
    import logging
    package_path = os.path.dirname(package.filename)
    options.package_path = package_path
    return_value = 100
    message = 'Unknown error'
    start = time.time()

    # Generate the doc build directory.
    os.makedirs(options.doc_build_directory, exist_ok=True)

    # remap output
    outfile = open(os.path.join(options.doc_build_directory, f'{package.name}.txt'), 'w')
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = outfile
    sys.stderr = outfile
    logging.basicConfig(
        format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
        level=logging.INFO, stream=outfile, force=True)
    logger = logging.getLogger('rosdoc2.scan')
    logger.info(f'Begin processing {package.name} using PID {os.getpid()} at {_clocktime()}')

    try:
        # run rosdoc2 for the package
        build_main(options)
        return_value = 0
        message = 'OK'
    except RuntimeError as e:
        return_value = 1
        message = type(e).__name__ + ' ' + str(e)
    except KeyboardInterrupt as e:
        return_value = 2
        if had_timeout.is_set():
            e = TimeoutError(f'Package {package.name} PID {os.getpid()} timed out after '
                             f'{"{:.3f}".format(time.time() - start)} seconds')
        message = type(e).__name__ + ' ' + str(e)
    except BaseException as e:  # noqa: B902
        return_value = 3
        message = type(e).__name__ + ' ' + str(e)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        elapsed_time = '{:.3f}'.format(time.time() - start)
        if return_value != 0:
            print(f'{_clocktime()} Package {package.name} using PID {os.getpid()} '
                  f'failed {return_value}: {message}',
                  flush=True)
            logger.error(f'Package {package.name} using PID {os.getpid()} '
                         f'failed {return_value}: {message}')
        else:
            print(f'{_clocktime()} Package {package.name} succeeded using PID {os.getpid()} '
                  f'in {elapsed_time} seconds', flush=True)
            logger.info(f'Completed rosdoc2 build for {package.name} '
                        f'in {elapsed_time} seconds')
        if not outfile.closed:
            outfile.close()
        return (package, return_value, message)


def package_worker(queues_and_options):
    """Worker process for package processing."""
    logger = logging.getLogger(f'rosdoc2.scan.{os.getpid()}')
    # The parent logger will be set in package_impl to capture to a file.
    # We want this logger independent, to sys.stderr.
    logger.propagate = False
    formatter = logging.Formatter(fmt='[%(name)s] [%(levelname)s] %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.WARNING)
    logger.debug(f'Worker started at {_clocktime()}')
    package_name = 'None'

    package_queue, results_queue, options = queues_and_options
    had_timeout = threading.Event()

    def watchdog(package):
        """Kill the process after a timeout."""
        had_timeout.set()

        # We want to catch the KeyboardInterrupt in the main thread, but eventually
        # we kill the process to stop any remaining child processes.
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2)
        os.kill(os.getpid(), signal.SIGKILL)

    package = package_queue.get()
    if package is None:
        logger.debug('Worker exiting due to None package')
    else:
        package_name = package.name
        logger.debug(f'Worker for {package_name} began processings at {_clocktime()}')
        watchdog_timer = threading.Timer(float(options.timeout), watchdog, args=(package,))
        watchdog_timer.start()
        try:
            # The real work
            results_queue.put(package_impl(package, options, had_timeout))
            logger.info(f'Worker for {package_name} finished at {_clocktime()}')
        except KeyboardInterrupt:
            if had_timeout.is_set():
                # The watchdog timer triggered
                logger.info(f'Worker for {package_name} timed out')
            else:
                # A real keyboard interrupt, time to exit
                logger.info(f'Worker for {package_name} interrupted, exiting')
        except BaseException as e:  # noqa: B902:
            logger.warning(f'Worker for {package_name} caught exception: '
                           f'{type(e).__name__} {str(e)}')
        finally:
            watchdog_timer.cancel()
            logger.debug(f'Worker for {package_name} exiting at {_clocktime()}')


def main_impl(options):
    """Execute the program."""
    package_queue = mp.Queue()
    results_queue = mp.Queue()
    options = Struct(**options.__dict__)

    if options.install_directory is not None:
        logger.warning(
            'The --install-directory option (-i) is unused '
            'and will be removed in a future version')

    # Locate the packages to document.
    found_packages = find_packages_allowing_duplicates(options.package_path)
    packages_by_name = {}
    count = 0
    for pkg in found_packages.values():
        count += 1
        if count >= int(options.max_packages):
            break
        if pkg.name not in packages_by_name:
            packages_by_name[pkg.name] = pkg
        else:
            logger_scan.warning(
                f'Duplicate package name <{pkg.name}> found at {pkg.filename} '
                f'and {packages_by_name[pkg.name].filename}. '
                'Using the first occurrence.')
    if len(packages_by_name) == 0:
        logger_scan.error(f'No packages found in subdirectories of {options.package_path}')
        exit(1)
    subprocesses = int(options.subprocesses) if options.subprocesses is not None \
        else os.cpu_count()
    packages_total = len(packages_by_name)
    packages_done = 0
    needs = {}
    needed_by = {}
    package_names = set()
    for package in packages_by_name.values():
        package_names.add(package.name)
        needs[package.name] = set()
        needed_by[package.name] = set()
    for package in packages_by_name.values():
        for dep in package.build_depends + package.exec_depends + package.doc_depends:
            if package.name in package_names and dep.name in package_names:
                needed_by[dep.name].add(package.name)
                needs[package.name].add(dep.name)

    logger_scan.info(f'Processing {packages_total} total packages')
    failed_packages = []
    added_packages = set()
    active_packages = set()

    with mp.Manager() as manager:
        package_queue = manager.Queue()
        results_queue = manager.Queue()
        with mp.Pool(processes=subprocesses, maxtasksperchild=1) as pool:
            logger_scan.info(f'Starting {subprocesses} worker processes')
            # Start the workers
            pool.map_async(package_worker,
                           ((package_queue, results_queue, options) for _ in range(subprocesses)))
            # process packages with no remaining dependencies
            logger_scan.info('Beginning package processing')
            while len(packages_by_name) > 0:
                try:
                    packages = []
                    for package in packages_by_name.values():
                        if package.name in added_packages:
                            continue
                        if len(needs[package.name]) == 0 and package.name not in added_packages:
                            packages.append(package)
                            added_packages.add(package.name)
                    for package in packages:
                        package_queue.put(package)
                        active_packages.add(package.name)
                        logger_scan.info(f'Adding {package.name} for processing '
                                         f'({package_queue.qsize()} packages queued)')

                    (package, returns, message) = results_queue.get()
                    active_packages.remove(package.name)
                    packages_done += 1
                    if returns != 0:
                        logger_scan.warning(f'{package.name} ({packages_done}/{packages_total})'
                                            f' returned {returns}: {message}')
                        failed_packages.append((package, returns, message))
                    else:
                        logger_scan.info(
                            f'{package.name} successful ({packages_done}/{packages_total})')
                    # Remove this package from the needs of others
                    packages_by_name.pop(package.name)
                    for name in needed_by[package.name]:
                        if package.name in needs[name]:
                            needs[name].remove(package.name)
                    # Start a new worker if there are still packages to do
                    if len(packages_by_name) > 0:
                        pool.apply_async(
                            package_worker,
                            args=((package_queue, results_queue, options),))
                    logger_scan.info(
                        f'Progress: done: {packages_done} total: {packages_total} '
                        f'queue size: {package_queue.qsize()} active: {len(active_packages)}')

                    # Check for dependency cycles
                    if len(packages_by_name) > 0 and len(active_packages) == 0:
                        logger_scan.warning('Dependency cycle detected among remaining packages: '
                                            f'{list(packages_by_name.keys())}')
                        logger_scan.warning('Remaining dependencies will be ignored.')
                        logger_scan.warning('This may cause missing crosslinks.')
                        for package in packages_by_name.values():
                            needs[package.name].clear()

                except KeyboardInterrupt:
                    logger_scan.info('Scan interrupted, terminating workers')
                    break
                except BaseException as e:  # noqa: B902
                    logger_scan.error(f'Scan caught exception: {type(e).__name__} {str(e)}')

    logger_scan.info('scan finished')

    if len(failed_packages) > 0:
        print(f'{len(failed_packages)} packages failed:')
        for failed in failed_packages:
            (package, returns, message) = failed
            print(f'{package.name}: retval={returns}: {message}')
    if len(packages_by_name) > 0:
        print(f'unprocessed packages: {list(packages_by_name.keys())}')
    else:
        print('All packages succeeded')
