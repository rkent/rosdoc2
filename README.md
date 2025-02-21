# rosdoc2

Command-line tool for generating documentation for ROS 2 packages.

## Overview

**rosdoc2** automatically generates documentation for ROS 2 packages. It will:

- show information from a package's configuration files and standard documents
- parse python and C++ source files, extracting embedded user documentation
- show messages, services, and actions
- show user text documentation written in restructuredText (rst) or markdown

A package author only has to provide information in the form that ros expects it, and **rosdoc2**
will automatically document it without requiring any configuration or rosdoc2-specific information
in the package. But if the author wants to configure customize **rosdoc2**, there are many ways to
do that.

## Quick-start

### Package Users

For package users, **rosdoc2** output is available by package name at "https://docs.ros.org/en/ROS_DISTRO/p/PACKAGE_NAME". So for example,
documentation for the **rclcpp** package "ROS client library in C++" is available for the 'rolling' distribution at [https://docs.ros.org/en/rolling/p/rclcpp/](https://docs.ros.org/en/rolling/p/rclcpp/)

### Package Authors

What you need to do in order to get basic documentation for your package using this tool is.. nothing.

This tool will extract information from your package's `package.xml` manifest file and generate a landing page for you.

If your package is laid out in a [standard way](https://docs.ros.org/en/rolling/The-ROS2-Project/Contributing/Developer-Guide.html#filesystem-layout) then it will automatically run Sphinx and/or Doxygen for you. You simply need to follow good ROS 2 package practices for your package to get automatically documented by **rosdoc2**. That means:

- In your package.xml, include a decent ```description```, and also ```url``` tags that are relevant for your package.
- Include standard files with appropriate content, including 'readme', 'license', 'contributing', 'changelog', 'quality_declaration', and 'package'.
- Make sure that your README file (which can be markdown or restructuredText) gives a good overview of your package.
- Add any additional documentation in a folder ```doc/``` directly below the main package folder (where package.xml is located). This documentation may be in restructuredText or markdown formats.
- Add any message, service, or action definitions in their standard locations (the ```msg/```, ```srv/```, or ```action/``` directory respectively). Add comments in those definition files describing the overall use of the item, and the use of each specific parameter.
- In your source files, document the purpose and parameters of classes and functions using Doxygen standards for C++, and Sphinx standards for python.

If you do the above and do it well, rosdoc2 should provide decent documentation for your package without requiring any rosdoc2-aware customization. But for more advanced cases, see the [customization documentation](doc/customization.md)

## Local Installation and Operation of **rosdoc2**

### Installation

If you are running in an environment where you have [enabled](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debians.html#enable-required-repositories) the ROS apt repositories on your system, you can install **rosdoc2** simply by:
```bash
sudo apt install rosdoc2
```

For more details and other environments, see [Installation](doc/installation.md)

### Build documentation for a ROS 2 package

To generate the documentation for almost any ROS 2 package, run this command replacing the arguments with appropriate directories:

```bash
rosdoc2 build --package-directory ./path/to/my_package_name
```

> [!NOTE]
> Please see [Known Issues](doc/known_issues.md) if failed.

This command will inspect your package and run various documentation tools based on the contents of your package. The `--package-directory` that you specify must contain a single ROS 2 package that has a `package.xml` file.

See the [build documentation](doc/run_rosdoc2.md#build) for more advanced usage.

### Build documentation for multiple ROS 2 packages

You can build with one command the documentation in all packages found in subdirectories with the `scan` command:

```bash
rosdoc2 scan --package-directory ./path/to/parent/directory
```

The command does a build of all packages found in subdirectories of the `--package-directory` directory. Otherwise,
the options and resuls are the same as the `build` command. This command may be useful in building all of the packages
in a single repository for example.

When you run this command, the console output shows a summary of **rosdoc2** activity. The output from each individual package build is available in the build directory (default `docs_build`) as the file PACKAGE_NAME.txt

See the [scan documentation](doc/run_rosdoc2.md#scan) for more advanced usage.

### View documentation for a ROS 2 package built locally

After you build the documentation for a package with the `build` command, there will be a local subdirectory created (default `docs_output`) which contains the documentation. That directory has subdirectories by ROS 2 package name with the rendered html.

You can ask **rosdoc2** to open a browser to view the documentation using the `open` command. Running the default version:

```bash
rosdoc2 open
```

will show the output directory with a package list (assuming you used the default `docs_output`), or you can directly open a package using:

```bash
rosdoc2 open some_package_name
```
See the [open documentation](doc/run_rosdoc2.md#open) for more advanced usage.

### Set up a ROS 2 package to be used with this tool

The purpose of this tool is to automate the execution of the various documentation tools when building documentation for ROS 2 packages.
Additionally, it provides several out-of-the-box behaviors to minimize configuration in the packages and to provide consistency across packages.

It aims to support two main cases:

- zero configuration generation of C++ and Python API documents with a landing page for simple packages
- custom Doxyfile (for C++) and Sphinx index.rst & conf.py file for more extensively configured documentation

The goal for the first case is to allow almost no configuration in packages while still providing some useful documentation, even if there is no Doxyfile, Sphinx conf.py file, or any free form documentation.

The goal for the second case is to allow packages to have free form documentation, additional settings for Doxygen and Sphinx, as well as make it possible for developers to easily invoke Doxygen or Sphinx on their projects manually, without this tool.
In this case, the tool would just automate execution of the tools and provide or override certain additional settings to make it more consistent with other packages, for example configuring the output directory or providing the configuration needed to use cross-references via tag files in Doxygen and inventory files in Sphinx.

See [customization](doc/customization.md) for details.

### Features

The tool aims to enable a few features:

- consistent landing page with basic package information for all packages
- support C++ API documentation extraction via Doxygen
- support Python API documentation extraction via Sphinx
- support free form documentation (prose, tutorial, concept pages, etc) via Sphinx
- support cross-language API cross-referencing via Sphinx using Breathe
- support cross-package documentation cross-referencing between packages via Sphinx
- show message, service, and action sources
- show links to various relevent locations, including both standard as well as autor-specified locations

## Contributing

**rosdoc2** is managed at [this](https://github.com/ros-infrastructure/rosdoc2) github location. To note issues or propose changes, post issues or PRs there.

We also try to add tests for changes, as **rosdoc2** supports a wide variety of edge use cases that are easily broken. See the `test` directory, or [testing](doc/testing.md) for details.

## Frequently Asked Questions

are [here](doc/faq.md)
