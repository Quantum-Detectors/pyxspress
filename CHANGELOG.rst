Changelog
=========

Major changes will be documented in this file.

The format is based on `Keep a Changelog
<https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`_.


0.5.1
-----

Added:

- Added unit tests for the Odin runtime configuration generation
- Added generation of ADOdin IOC boot script to configure for the correct number
  of Odin data FR/FP pairs

Changed:

- Refactored and renamed create_config modules to be more descriptive


0.5.0
-----

Added:

- Added GitLab CI/CD script with Wheel deployment
- Added warning and user confirmation when using the config generator CLI
  tool when providing an Odin path where the directory name is not 'config'.
  This is because the directory is cleaned when new config is generated.

Changed:

- Initial migration from qd-odin-build repository
- Changed from pipenv to uv for managing the Python environment

Fixed:

- Initialise y_axis as QValueAxis instead of QAbstractAxis as no longer
  instantiable in current versions of Qt 6
