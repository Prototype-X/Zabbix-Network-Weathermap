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
    latency = time.time() - start_time
    print(round(latency, 3), file=sys.stdout)

if __name__ == '__main__':
    main()
