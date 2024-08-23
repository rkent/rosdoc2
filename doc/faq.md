# Frequently Asked Questions

(or at least questions that I think people might ask)

## Why isn't my package documentation showing on https://docs.ros.org/en/DISTRO/p/PACKAGE_NAME/?

At the moment, packages are added for documentation if they have a `doc:` section in the appropriate location in [rosdistro](https://github.com/ros/rosdistro/). Some reasons your package might not appear include:

- it has no `doc:` section in rosdistro
- the url and version in `doc:` point to a version with no `package.xml` (Some packages have their package.xml generated later from information in CMakeLists.txt)
- **rosdoc2** is failing when it attempts to run the package. You should be able to find the build job for the package on the [ros2 jenkins](https://build.ros2.org/) to investigate.
- you have defined a `conf.py` file for Sphinx, but it generates an error.

**rosdoc2** contributor [rkent](https://github.com/rkent) has a development build of **rosdoc2** rolling packages [here](http://rosdoc2.rosdabbler.com) that tries to overcome many issues keeping packages from being successfully documented by **rosdoc2**. If your package appears there but not in the official location, let's [talk](mailto:kent@caspia.com).

If my issue is ...

### My python package is in a non-standard location?

Change `python_source` in [rosdoc2.yaml](doc/rosdoc2.yaml.md)

### My documentation files are in a non-standard location?

Change `user_doc_dir` in [rosdoc2.yaml](rosdoc2.yaml.md)

### I host documentation externally, and I want that to show as my documentation?

Change `external_doc_url` in [rosdoc2.yaml](rosdoc2.yaml.md). If that documentation includes information on your code internals or API, you could also stop C++ parsing by Doxygen by setting `never_run_doxygen: true`, or stop python parsing by sphinx-autodoc by setting `never_run_sphinx_apidoc: true`, both in [rosdoc2.yaml](rosdoc2.yaml.md).

### Sphinx is crashing on my documentation, but Doxygen works?

Set `disable_breathe: true` and `show_doxygen_html: true` in [rosdoc2.yaml](rosdoc2.yaml.md)

### I want to completely control what **rosdoc2** shows?

Set `sphinx_sourcedir:` to your documentation directory in in [rosdoc2.yaml](rosdoc2.yaml.md), and add your own conf.py and either `index.rst` or `index.rst.jinja` to that directory with the content that you want.

### I want to slightly modify what **rosdoc2** displays?

1) Copy then modify the default [index.rst.jinja](index.rst.md) to a documentation directory (typically `doc/`).
2) Set `sphinx_sourcedir:` to your documentation directory in [rosdoc2.yaml](rosdoc2.yaml.md)

### My package has no code, only documentation. How do I stop code parsing?

This should happen naturally with the default **rosdoc2** configuration. But if you want, you can force **rosdoc2** to avoid C++ parsing by Doxygen by setting `never_run_doxygen: true`, or stop python parsing by sphinx-autodoc by setting `never_run_sphinx_apidoc: true`, both in [rosdoc2.yaml](rosdoc2.yaml.md).
