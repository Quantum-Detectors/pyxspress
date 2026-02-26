#!/bin/bash

# TCP relay server to fan out the TCP traffic from the Xspress system
/odin/tools/TcpRelay -s $1 -c $2
