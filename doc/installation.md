# rosdoc2 Installation

## Using ROS debian packages

If you are running in an environment where you have [enabled](https://docs.ros.org/en/rolling/Installation/Ubuntu-Install-Debs.html) the ROS 2 apt repositories on your system, you can install **rosdoc2** simply by:
```bash
sudo apt install rosdoc2
```

## Using PyPI

In other Linux environments, you can install **rosdoc2** via apt and pip (typically into a [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)):

```bash
# Install prerequisites
sudo apt install doxygen graphviz python3-venv
# Install rosdoc2 in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install rosdoc2
```

## Development version from repository

You can install **rosdoc2** directly from the repository (typically for development purposes):

```bash
# Install prerequisites
sudo apt install doxygen graphviz python3-venv git
# Download the repository
git clone https://github.com/ros-infrastructure/rosdoc2.git
cd rosdoc2
# Install into pip virtual environment (with --editable option)
python3 -m venv venv
source venv/bin/activate
pip install -e rosdoc2
```

## Other operating systems

**rosdoc2** is not tested on Windows, and probably does not work there. Sorry.

It presumably works in RedHat enviroments, but again is untested.
Just adapt the debian-focused instructions above (or submit a PR to fix this documentation!)

