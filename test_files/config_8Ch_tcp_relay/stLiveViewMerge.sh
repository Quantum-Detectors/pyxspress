#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

/odin/python/bin/xspress_live_merge --sub_ports 15500,15501,15502,15503
