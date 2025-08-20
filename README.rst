pyxspress
=========

|code_ci| |coverage|

Python utility module for Xspress Odin.

- Used to generate Odin runtime configuration, ADOdin IOC boot file
  and EDM procServ control screen for Odin processes
- Provides some utility scripts for running acquisitions and viewing
  captured data


Installation
------------

This is installed using the scripts from qd-odin-build which deploy
the Wheel on the target server and then create a virtual environment
in the Odin installation directory with the module installed.


Dependencies
------------

Only Python module dependencies required. This module currently targets
and is tested on Python 3.11, but should work on newer versions.


Usage
-----

When installed the following entry points are available:

- `xspress-acquire`: basic MCA acquisition using ADOdin with file saving
- `xspress-create-config`: generate Xspress Odin runtime configuration,
  ADOdin IOC boot file and procServ control screen for an Xspress system
- `xspress-list-mode-listener`: can listen to X3X2 list mode TCP endpoints
  and save the binary data directly to disk.
- `xspress-list-mode-decode`: used to decode the saved list mode binary data
  and can either plot decoded time frames or save the data to a simpler HDF5
  format.
- `xspress-plot`: basic MCA plotting of saved HDF5 data
- `xspress-view`: GUI application to browse MCA and list mode data


Project layout
--------------

The project structure is as follows:

- src - module source code
- test_files - test Xspress Odin data files
- tests - unit test source code


Development setup
-----------------

This repository has swapped to using `uv` for managing the virtual environment.

We can create the virtual environment using:

.. code-block:: bash

  $ uv venv --python 3.11


We can then install the dependencies including optional group dependencies:

.. code-block:: bash

  $ uv pip install --group cli
  $ uv pip install --group dev


The dependencies can be locked and/or synced:

.. code-block:: bash

  $ uv lock
  $ uv sync


You can also specify a Python version with --python.

The virtual environment is then accessible via the `uv run ...` commands.

This includes running the linting, type-checking and test tools:

.. code-block:: bash

  $ uv run ruff check
  $ uv run ruff format
  $ uv run mypy
  $ uv run pytest


Entry points and scripts are also run using the same command, e.g.:

.. code-block:: bash

  $ uv run xspress-create-config


CI/CD
-----

This project uses CI/CD for testing and deploying the Python Wheel.
The pipeline is separated into the following stages:

- Build
- Deploy


Build
#####

This runs for every commit (although some are skipped if more than one is pushed
at the same time). This will run all unit tests, perform linting and type
checking and checks that documentation builds without errors.


Deploy
######

This runs when a tag is pushed. It builds and deploys a Python Wheel to the
GitLab package registry.


Licences
--------

This module makes use of other Python packages which may need us to provide
a notice to end-users when distributing the software. The `pip-licenses`
module helps us check which dependencies we are using and is installed with
the development requirements.

This can then be run with:

.. code-block:: bash

  $ uv run pip-licenses


You will want to only provide information for the installation licences, which
can be obtained from installing the dependencies using without the group
`--dev` flag.


Change log
----------

See `CHANGELOG`_ for notable changes and fixes.


To do
-----

See the Issues section on the GitLab repository for a list of features and bugs.

.. _CONTRIBUTING:
  https://gitlab.com/qd-xspress3/pyxspress/-/blob/main/CONTRIBUTING.rst

.. _CHANGELOG:
  https://gitlab.com/qd-xspress3/pyxspress/-/blob/main/CHANGELOG.rst


.. |code_ci| image:: https://gitlab.com/qd-xspress3/pyxspress/badges/main/pipeline.svg
  :target: https://gitlab.com/qd-xspress3/pyxspress/-/pipelines
  :alt: Code CI

.. |coverage| image:: https://gitlab.com/qd-xspress3/pyxspress/badges/main/coverage.svg
  :target: https://gitlab.com/qd-xspress3/pyxspress/-/commits/main
  :alt: Coverage
