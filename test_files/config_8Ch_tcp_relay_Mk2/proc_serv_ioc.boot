epicsEnvSet "EPICS_CA_MAX_ARRAY_BYTES", '7000000'
epicsEnvSet "EPICS_TS_MIN_WEST", '0'

epicsEnvSet "PROCSERVCONTROL", "/odin/epics/support/procServControl"

# Device initialisation
# ---------------------

dbLoadDatabase "${PROCSERVCONTROL}/iocs/autoProcServControl/dbd/autoProcServControl.dbd"

autoProcServControl_registerRecordDeviceDriver(pdbbase)

# Odin ports
drvAsynIPPortConfigure("OdinServerPort", "localhost:4001", 100, 0, 0)
drvAsynIPPortConfigure("OdinMetaPort", "localhost:4002", 100, 0, 0)
drvAsynIPPortConfigure("ControlServerPort", "localhost:4003", 100, 0, 0)
drvAsynIPPortConfigure("OdinLVPort", "localhost:4004", 100, 0, 0)
drvAsynIPPortConfigure("ADOdinPort", "localhost:4005", 100, 0, 0)
drvAsynIPPortConfigure("OdinFR1Port", "localhost:4010", 100, 0, 0)
drvAsynIPPortConfigure("OdinFP1Port", "localhost:4011", 100, 0, 0)
drvAsynIPPortConfigure("OdinFR2Port", "localhost:4012", 100, 0, 0)
drvAsynIPPortConfigure("OdinFP2Port", "localhost:4013", 100, 0, 0)
drvAsynIPPortConfigure("OdinFR3Port", "localhost:4014", 100, 0, 0)
drvAsynIPPortConfigure("OdinFP3Port", "localhost:4015", 100, 0, 0)
drvAsynIPPortConfigure("OdinFR4Port", "localhost:4016", 100, 0, 0)
drvAsynIPPortConfigure("OdinFP4Port", "localhost:4017", 100, 0, 0)


# Final ioc initialisation
# ------------------------

# PVs for control
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-01, PORT=OdinServerPort"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-02, PORT=OdinMetaPort"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-03, PORT=ControlServerPort"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-04, PORT=OdinLVPort"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-05, PORT=OdinFR1Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-06, PORT=OdinFP1Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-07, PORT=OdinFR2Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-08, PORT=OdinFP2Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-09, PORT=OdinFR3Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-10, PORT=OdinFP3Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-11, PORT=OdinFR4Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSP-ODN-12, PORT=OdinFP4Port"
dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template","P=XSPRESS, PORT=ADOdinPort"

seq(procServControl, "P=XSP-ODN-01")
seq(procServControl, "P=XSP-ODN-02")
seq(procServControl, "P=XSP-ODN-03")
seq(procServControl, "P=XSP-ODN-04")
seq(procServControl, "P=XSP-ODN-05")
seq(procServControl, "P=XSP-ODN-06")
seq(procServControl, "P=XSP-ODN-07")
seq(procServControl, "P=XSP-ODN-08")
seq(procServControl, "P=XSP-ODN-09")
seq(procServControl, "P=XSP-ODN-10")
seq(procServControl, "P=XSP-ODN-11")
seq(procServControl, "P=XSP-ODN-12")
seq(procServControl, "P=XSPRESS")

iocInit

# Post-IOC init
# -------------

dbpf "XSP-ODN-01:IOCNAME" "Odin server"
dbpf "XSP-ODN-02:IOCNAME" "Odin meta writer"
dbpf "XSP-ODN-03:IOCNAME" "Odin control server"
dbpf "XSP-ODN-04:IOCNAME" "Odin live view"
dbpf "XSP-ODN-05:IOCNAME" "Odin frame receiver 1"
dbpf "XSP-ODN-06:IOCNAME" "Odin frame processor 1"
dbpf "XSP-ODN-07:IOCNAME" "Odin frame receiver 2"
dbpf "XSP-ODN-08:IOCNAME" "Odin frame processor 2"
dbpf "XSP-ODN-09:IOCNAME" "Odin frame receiver 3"
dbpf "XSP-ODN-10:IOCNAME" "Odin frame processor 3"
dbpf "XSP-ODN-11:IOCNAME" "Odin frame receiver 4"
dbpf "XSP-ODN-12:IOCNAME" "Odin frame processor 4"
dbpf "XSPRESS:IOCNAME" "Xspress ADOdin"
