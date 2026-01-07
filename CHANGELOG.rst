Changelog
=========

Major changes will be documented in this file.

The format is based on `Keep a Changelog
<https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`_.

0.7.5
-----

Changed:

- Changed master dataset for first card when marker channels are enabled to
  the second real channel instead of the marker channel. This number is then
  more comparable to the counters for the other frame processors.


0.7.4
-----

Added:

- Added master list mode datasets to frame processor configuration files so that
  the frame counter for Odin data increments based on how many memory block
  frames are written (not linked to actual Xspress time frames)


0.7.3
-----

Changed:

- Updated the default Odin data filepath to /tmp so that it is set to a valid
  path when the IOC boots


0.7.2
-----

Added:

- Additional configuration option for using the TCP relay server has been added.
  Odin will connect to the TCP relay server instead of directly to the Xspress
  when enabled. This adds the relay server launch script which is called from
  the main Odin launcher script using procServ.
- Added an option to the List mode listener to listen to the TCP relay server
  instead of the Xspress system directly


0.7.1
-----

Changed:

- Added MC (marker channel) flag to config generation to make the configuration include the option for marker channels in list mode.
  The data is added to the hdf5 data set with the suffix '_A'
- `xspress-view` can open files with marker channel data although it doesn't do anything with it yet.


0.7.0
-----

Added:

- Add CLI option `xspress-list-mode-check` to check the ordering of events in
  a saved Odin list mode acquisition
- Added example MCA data files to test with `xspress-view` GUI

Changed:

- Changed XSP3READOUT variable to frames inside `stControlServer.sh` control
  server launch script to optimise default readout mode for frames
- `xspress-list-mode-decode` now decodes the Python TCP files using HDF5 dataset
  names consistent with the Odin process plugins. This means you can open these
  files using `xspress-view` as with Odin-produced data
- Changed default run flags in IOC boot template to just Scalers and Hist (i.e.
  remove playback)

Fixed:

- Fixed issue with checking the channel of a TCP packet in the ListModeDecoder
  class matches a requested channel


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
