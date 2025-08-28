#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

export LD_LIBRARY_PATH=/odin/xspress/lib
export XSP3READOUT=passive

/odin/prefix/bin/xspressControl -j $SCRIPT_DIR/xspress.json
