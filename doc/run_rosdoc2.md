# Detailed description of rosdoc2 run options

## build
```
usage: rosdoc2 build [-h] --package-path PACKAGE_PATH [--build-directory BUILD_DIRECTORY] [--install-directory INSTALL_DIRECTORY]
                     [--cross-reference-directory CROSS_REFERENCE_DIRECTORY] [--base-url BASE_URL] [--output-directory OUTPUT_DIRECTORY]
                     [--doc-build-directory DOC_BUILD_DIRECTORY] [--debug]
```
Build the documentation of a ROS package
```
options:
  -h, --help            show this help message and exit
  --package-path PACKAGE_PATH, -p PACKAGE_PATH
                        path to the ROS package
  --build-directory BUILD_DIRECTORY, -b BUILD_DIRECTORY
                        UNUSED, to be removed at some time after September 1st, 2024
  --install-directory INSTALL_DIRECTORY, -i INSTALL_DIRECTORY
                        install directory of the package
  --cross-reference-directory CROSS_REFERENCE_DIRECTORY, -c CROSS_REFERENCE_DIRECTORY
                        directory containing cross reference files, like tag files and inventory files
  --base-url BASE_URL, -u BASE_URL
                        The base url where the package docs will be hosted, used to configure tag files.
  --output-directory OUTPUT_DIRECTORY, -o OUTPUT_DIRECTORY
                        directory to output the documenation artifacts into
  --doc-build-directory DOC_BUILD_DIRECTORY, -d DOC_BUILD_DIRECTORY
                        directory to setup build prefix
  --debug               enable more output to debug problems
```
## open
```
usage: rosdoc2 open [-h] [package_output_directory]
```
Open the documentation that was built in a web browser
```
positional arguments:
  package_output_directory
                        (optional) path to the built documentation (default "docs_output") OR package name

options:
  -h, --help            show this help message and exit
```

## scan
```
usage: rosdoc2 scan [-h] --package-path PACKAGE_PATH [--build-directory BUILD_DIRECTORY] [--install-directory INSTALL_DIRECTORY] [--cross-reference-directory CROSS_REFERENCE_DIRECTORY] [--base-url BASE_URL]
                    [--output-directory OUTPUT_DIRECTORY] [--doc-build-directory DOC_BUILD_DIRECTORY] [--debug] [--yaml-extend YAML_EXTEND] [--timeout TIMEOUT] [--max-packages MAX_PACKAGES]
```
Scan subdirectories looking for packages, then build those packages.
```
options:
  -h, --help            show this help message and exit
  --package-path PACKAGE_PATH, -p PACKAGE_PATH
                        path to the ROS package
  --build-directory BUILD_DIRECTORY, -b BUILD_DIRECTORY
                        UNUSED, to be removed at some time after September 1st, 2024
  --install-directory INSTALL_DIRECTORY, -i INSTALL_DIRECTORY
                        install directory of the package
  --cross-reference-directory CROSS_REFERENCE_DIRECTORY, -c CROSS_REFERENCE_DIRECTORY
                        directory containing cross reference files, like tag files and inventory files
  --base-url BASE_URL, -u BASE_URL
                        The base url where the package docs will be hosted, used to configure tag files.
  --output-directory OUTPUT_DIRECTORY, -o OUTPUT_DIRECTORY
                        directory to output the documenation artifacts into
  --doc-build-directory DOC_BUILD_DIRECTORY, -d DOC_BUILD_DIRECTORY
                        directory to setup build prefix
  --debug               enable more output to debug problems
  --yaml-extend YAML_EXTEND, -y YAML_EXTEND
                        Extend rosdoc2.yaml
  --timeout TIMEOUT, -t TIMEOUT
                        maximum time in seconds allowed per package
  --max-packages MAX_PACKAGES, -m MAX_PACKAGES
                        maximum number of packages to process
```

## default_config
```
usage: rosdoc2 default_config [-h] --package-path PACKAGE_PATH
```
Create a default rosdoc2 config file in a package
```
options:
  -h, --help            show this help message and exit
  --package-path PACKAGE_PATH, -p PACKAGE_PATH
                        path to the ROS package
```