#!/bin/bash

# This is the odinprocservcontrol soft IOC for controlling all Odin
# processes through procServControl.

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

/odin/python/bin/odinprocservcontrol $SCRIPT_DIR/odin_proc_serv_ioc.yaml
