#!/bin/bash

# This is the procServControl IOC
# This creates a set of PVs for each Odin process to allow
# control of the procServ processes from EPICS.

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

/odin/epics/support/procServControl/iocs/autoProcServControl/bin/linux-x86_64/autoProcServControl $SCRIPT_DIR/proc_serv_ioc.boot
