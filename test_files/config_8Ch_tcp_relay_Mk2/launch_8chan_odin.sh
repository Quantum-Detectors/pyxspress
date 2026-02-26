#!/usr/bin/bash

# ============================================================
# Launch 8 channel Odin processes
# ============================================================

# Launch from config folder
cd /odin/config

# Odin processes
procServ -P 4001 /odin/config/stOdinServer.sh
procServ -P 4002 /odin/config/stMetaWriter.sh
procServ -P 4003 /odin/config/stControlServer.sh
procServ -P 4004 /odin/config/stLiveViewMerge.sh

# ADOdin
procServ -P 4005 /odin/config/stXspressADOdin.sh

# Frame Reciever and Process pairs
procServ -P 4010 /odin/config/stFrameReceiver1.sh
procServ -P 4011 /odin/config/stFrameProcessor1.sh
procServ -P 4012 /odin/config/stFrameReceiver2.sh
procServ -P 4013 /odin/config/stFrameProcessor2.sh
procServ -P 4014 /odin/config/stFrameReceiver3.sh
procServ -P 4015 /odin/config/stFrameProcessor3.sh
procServ -P 4016 /odin/config/stFrameReceiver4.sh
procServ -P 4017 /odin/config/stFrameProcessor4.sh

# TCP relay servers
procServ -P 8001 /odin/config/stTcpRelay.sh 192.168.0.2:30125 13001
procServ -P 8002 /odin/config/stTcpRelay.sh 192.168.0.3:30125 13002
procServ -P 8003 /odin/config/stTcpRelay.sh 192.168.0.4:30125 13003
procServ -P 8004 /odin/config/stTcpRelay.sh 192.168.0.5:30125 13004

# ProcServControl IOCs
procServ -P 9001 /odin/config/stProcServControl.sh
procServ -P 9002 /odin/config/stOdinProcServControl.sh

cd -
