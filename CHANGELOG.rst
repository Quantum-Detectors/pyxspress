Changelog
=========

Major changes will be documented in this file.

The format is based on `Keep a Changelog
<https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`_.


0.6.0
-----

Changed:

- FP JSON config now generated using Jinja2 template
- Changed list mode datasets per channel from `raw_{ch}` to separate out each
  field:

  - `{ch}_time_frame` for the time frame
  - `{ch}_time_stamp` for the time stamp
  - `{ch}_event_height` for the event height
  - `{ch}_reset_flag` to show if the event describes a reset

- Changed default filename to `example` without HDF5 extension as this parameter
  is treated as a prefix rather than a full path.
- Acquisition script now checks the detector's acquire mode and only sets
  chunking if in MCA mode.
- The list mode plugin frame size is now set to be the same number of elements as
  the a single chunk in the HDF dataset. Data would be lost if these values did not
  match (in terms of number of elements, not bytes)
- Updated the xspress list file reader to support the new separate datasets format

Fixed:

- Acquisition script now uses number of cards of system to calculate the expected
  number of images saved


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
