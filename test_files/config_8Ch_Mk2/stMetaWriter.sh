#!/bin/bash

numactl --membind=0 --cpunodebind=0 /odin/python/bin/xspress_meta_writer -w xspress_detector.data.xspress_meta_writer.XspressMetaWriter --sensor-shape 8 4096 --data-endpoints tcp://127.0.0.1:10008,tcp://127.0.0.1:10018,tcp://127.0.0.1:10028,tcp://127.0.0.1:10038 --static-log-fields detector="Xspress3"
