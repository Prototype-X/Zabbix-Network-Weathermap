#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'

import argparse
import logging
import os
import sys

from config import ConfigLoader, ConfigCreate
from zabbix import ZabbixAgent


class WeathermapCLI(object):
    def __init__(self):
        self.root_path = str(os.path.dirname(os.path.abspath(__file__)))
        self.font_path = self.root_path + '/fonts'
        self.font_path_fn = self.root_path + '/fonts/DejaVuSansMono.ttf'
        self.icon_path = self.root_path + '/icons'
        self.cfg_path = self.root_path + '/mapcfgs'
        self.img_path = self.root_path + '/mapimgs'

        self.parser = argparse.ArgumentParser(conflict_handler='resolve', description='Network weathermap for Zabbix')
        self.parser.add_argument('-v', '--version', action='store_true', help='show version')
        self.parser.add_argument('-h', '--help', action='help', help='show help')
        self.parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')

        self.parser.add_argument('-m', '--map', action='store', type=str, help='Config file name')
        self.parser.add_argument('-i', '--img', action='store', type=str, help='Image path')
        self.parser.add_argument('-u', '--upload', action='store_true', help='Image upload to zabbix')

        self.parser.add_argument('-c', '--cfg', action='store', type=str, help='Config path')
        self.parser.add_argument('-a', '--all', action='store_true', help='all')

        self.parser.add_argument('-s', '--scan', action='store', type=str, help='Map name in Zabbix')
        self.parser.add_argument('-z', '--zabbix', action='store', type=str, help='Zabbix server url')
        self.parser.add_argument('-l', '--login', action='store', type=str, help='Login')
        self.parser.add_argument('-p', '--pwd', action='store', help='Password')

        self.args = self.parser.parse_args()
        self._cfg_logging()

        if not vars(self.args):
            self.parser.print_help()
            sys.exit()

        if self.args.version:
            print('Network weathermap 1.0')
            sys.exit()

        if self.args.map:
            self._map_img()
        elif self.args.scan and self.args.zabbix and self.args.login and self.args.pwd:
            self._map_scan()
        else:
            self.parser.print_help()
            sys.exit()

    def _map_scan(self):
        if self.args.cfg:
            self.cfg_path = self.args.cfg
        zbx = ZabbixAgent(self.args.zabbix, self.args.login, self.args.pwd)
        map_data = zbx.scan_map(self.args.scan)
        scan_map = ConfigCreate(map_data, zbx)
        scan_map.create()
        scan_map.check_map(self.cfg_path)
        scan_map.save(self.cfg_path)

    def _map_img(self):
        if self.args.cfg:
            self.cfg_path = self.args.cfg
        if self.args.img:
            self.img_path = self.args.img

        cfg = ConfigLoader(self.cfg_path + '/' + self.args.map)
        cfg.load()
        map_obj = cfg.create_map(self.font_path_fn, self.icon_path)
        map_obj.do()
        map_obj.show()
        map_obj.save_img(self.img_path + '/' + self.args.map[:-4] + '.png')

        if self.args.upload:
            cfg.upload(self.img_path + '/' + self.args.map[:-4] + '.png')

    def _cfg_logging(self):
        """
        Configure logging output format.
        """
        if self.args.debug:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        logformat = '[%(asctime)s] [%(name)s:%(levelname)s] - %(message)s'
        logging.basicConfig(level=loglevel, format=logformat, datefmt='%d/%m/%Y %H:%M:%S')


def main():
    WeathermapCLI()

if __name__ == '__main__':
    main()


# TODO config.py: configparser.ConfigParser().has_section convert to str.lower()
# TODO tests for all classes
# TODO logging for all classes, detail logging
# TODO add new option fontsize in section [map] +
# TODO add new option fontsize in section [node-]
# TODO add new option fontsize in section [link-]
# TODO add new option fontsize in section [table]
# TODO add new option bgcolor in section [map] +
# TODO add table date and time
# TODO class cli with argsparse
# TODO python or bash start script, run weathermap from zabbix agent or item with external check
# TODO arg -a --all
