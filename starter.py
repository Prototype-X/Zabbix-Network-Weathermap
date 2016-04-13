#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'
import time
import sys
import subprocess


def main():
    start_time = time.time()
    cli = ['/opt/Zabbix-Network-Weathermap/weathermap.py']
    cli.extend(sys.argv[1:])
    subprocess.call(cli)
    latency = round(time.time() - start_time, 3)
    print(latency)

if __name__ == '__main__':
    main()
