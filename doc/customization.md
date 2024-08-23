# Customization of your ROS 2 Package to Work With rosdoc2

**rosdoc2** has a number of customization hooks that can assist packages with special requirements. For example:
- Change the default location for python or documentation files
- Ask **rosdoc2** to display your externally-hosted documentation, rather than try to render files in the doc/ directory.
- disable or enable automatic documentation of C++ or python code, in spite of your package contents.
- Show the Doxygen html output for C++ rather than the sphinx/breathe version that **rosdoc2** prefers

See the [FAQ](faq.md) for suggestions on specic common customization.

The hooks that **rosdoc2** provides for customization are:
- the `rosdoc2.yaml` file. See the [rosdoc2.yaml](rosdoc2.yaml.md) for details.
- the Sphinx `conf.py` file. See [conf.py customization](conf.py.md) for details.
- the index file that controls what is shown by **rosdoc2** See [index.rst customization](index.rst.md) for details.
- the `Doxyfile` used by Doxygen to parse C++ files for documentation. See [Doxyfile customization](Doxyfile.md) for details.

## Packages with C/C++ API Documentation

The tool uses information from your package's `package.xml` manifest file, and assumes the source files with documentation to be extracted are all in the `include` folder of your packages, based on the package layout conventions for ROS 2:

https://docs.ros.org/en/rolling/The-ROS2-Project/Contributing/Developer-Guide.html#filesystem-layout

The generation of C++ documentation using Doxygen is triggered either by the build type being `ament_cmake` or `cmake`, or by `always_run_doxygen` set in `rosdoc2.yaml`.

You should not have to customize this for rosdoc2 however. If ROS 2 builds your C++ package, then **rosdoc2** should document it.

**rosdoc2** uses Doxygen to parse the C++ into machine-readable xml, the uses the python packages breathe and exhale to process that into restructuredText that can be merged with other documentation into the final **rosdoc2** output.

Doxygen also generates displayable html, and that is also available for your package, but is not normally linked. For example, the package `rclcpp` that normally shows sphinx-and-breathe-generated C++ (here)[https://docs.ros.org/en/rolling/p/rclcpp/generated/index.html] also has the 'Doxygen' html available at (https://docs.ros.org/en/rolling/p/rclcpp/generated/doxygen/html/)[https://docs.ros.org/en/rolling/p/rclcpp/generated/doxygen/html/] In unusual cases (like if breathe or exhale is crashing), it might be preferable to show the Doxygen html, either by itself or along with the sphinx link. The Doxygen html link is enabled using `show_doxygen_html: true` in [rosdoc2.yaml](rosdoc2.yaml.md).

For details on configuring Doxygen to parse your C++ files, [see the Doxygen documentation](https://www.doxygen.nl/)

## Packages with Python API Documentation

The tool looks for python files in a subdirectory of your package matching the package name. It also supports by the alternate layout of src/PACKAGE_NAME. This can also be customized by setting `python_source` in [rosdoc2.yaml](rosdoc2.yaml.md)

Python source files are parsed by sphinx-autodoc, which generated restructuredText files that are merged with other documentation files into the final **rosdoc2** documentation.

**rosdoc2** assumes that your package contains python if:
- your buildtype is `ament_python` or
- you have `<buildtool_depend>ament_cmake_python</buildtool_depend>` in your package.xml, or
- you have specified `always_run_sphinx_apidoc` in [rosdoc2.yaml](rosdoc2.yaml.md)

You should not have to customize this for rosdoc2 however. If ROS 2 builds your python, rosdoc2 should also document it.

For details on using Sphinx for documentation, see [their documentation.](https://www.sphinx-doc.org/)

## Packages with ROS 2 Messages and other kinds of Interfaces

**rosdoc2** will simply show the source of your message, services, and action files in the standard locations. Nothing to customize here!
