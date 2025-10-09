import logging
import os

import requests

logger = logging.getLogger('rosdoc2')


def download_cross_references(cross_reference_directory, package, base_url, include_tags=False):
    """Download cross-reference files for a package."""
    # Generate dependencies.
    dependencies = set()
    for deptype in ['build_depends', 'exec_depends', 'doc_depends']:
        for dep in package[deptype]:
            dependencies.add(dep.name)
    logger.info(f'Collecting cross references for dependencies: {dependencies}')
    # intersphinx objects.inv
    for dep in dependencies:
        deppath = os.path.join(cross_reference_directory, f'{dep}.inv')
        if os.path.exists(deppath) and os.path.exists(deppath + '.location.json'):
            continue
        objects_url = os.path.join(base_url, dep, 'objects.inv')
        location_url = objects_url + '.location.json'
        objects_response = requests.get(objects_url)
        if not objects_response.ok:
            logger.warning(f"Could not find objects.inv for package '{dep}' at '{objects_url}'")
            continue
        location_response = requests.get(location_url)
        if not location_response.ok:
            logger.warning(
                f"Could not find objects.inv location data for package '{dep}'"
                + f" at '{location_url}'")
            continue
        inv_file_path = os.path.join(cross_reference_directory, dep, 'objects.inv')
        os.makedirs(os.path.dirname(inv_file_path), exist_ok=True)
        with open(inv_file_path, 'wb') as f:
            f.write(objects_response.content)
        location_json_path = inv_file_path + '.location.json'
        with open(location_json_path, 'w') as f:
            f.write(location_response.text)
        logger.info(f"Downloaded objects.inv for package '{dep}' from '{objects_url}'")
    # Doxygen tag files.
    if include_tags:
        for dep in dependencies:
            tagpath = os.path.join(cross_reference_directory, f'{dep}.tag')
            if os.path.exists(tagpath) and os.path.exists(tagpath + '.location.json'):
                continue
            # Check if package is hosted on docs.ros.org if we don't have a tag file
            # for it already.
            tag_url = os.path.join(base_url, dep, 'generated', 'doxygen', f'{dep}.tag')
            location_url = tag_url + '.location.json'
            tag_response = requests.get(tag_url)
            if not tag_response.ok:
                logger.warning(f"Could not find tag file for package '{dep}' at '{tag_url}'")
                continue
            location_response = requests.get(location_url)
            if not location_response.ok:
                logger.warning(
                    f"Could not find tag file location data for package '{dep}'"
                    + f" at '{location_url}'")
                continue
            tag_file_path = os.path.join(cross_reference_directory, dep, f'{dep}.tag')
            os.makedirs(os.path.dirname(tag_file_path), exist_ok=True)
            with open(tag_file_path, 'wb') as f:
                f.write(tag_response.content)
            location_json_path = tag_file_path + '.location.json'
            with open(location_json_path, 'w') as f:
                f.write(location_response.text)
            logger.info(f"Downloaded tag file for package '{dep}' from '{tag_url}'")
