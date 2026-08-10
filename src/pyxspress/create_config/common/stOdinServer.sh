#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

/opt/QD/venv/bin/xspress_control --config=$SCRIPT_DIR/odin_server.cfg --logging=info --access_logging=ERROR
