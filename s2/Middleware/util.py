# -*- coding = utf-8 -*-
# @Time: 2022/7/4 16:07
# @File: util.PY
import sys

from subscribe_client import clt_id, clt_username, clt_password
from car import Car


# {"lat": 31.18269116, "lat_semi": "N", "lon": 120.4479978, "lon_semi": "E", "date": "050822", "time": "000001.0"
# "angel": "18.7", "speed": "0.0"}

def run_1_car():
    vehicle1 = Car('02', 'Truck')
    # set socket host:port and aliyun host, port and connection info
    vehicle1.set_aliyun_username(clt_id, clt_username, clt_password)
    vehicle1.thread_run()

    input_val = input()
    if input_val == 'exit':
        vehicle1.thread_terminate()
        sys.exit(0)
