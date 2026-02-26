#!/bin/bash

# This is the Xspress ADOdin IOC process

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

ADODIN_DIR=/odin/epics/support/ADOdin
IOC_DIR=$ADODIN_DIR/iocs/xspress

$IOC_DIR/bin/linux-x86_64/xspress $IOC_DIR/bin/linux-x86_64/stxspress.boot
