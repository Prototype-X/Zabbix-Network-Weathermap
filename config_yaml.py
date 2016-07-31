#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'


import yaml
from collections import OrderedDict
import os
import logging
import configparser
from zabbix import ZabbixAgent
from mapping import Node, Link, Map, Table, Palette
from PIL import Image
import base64
import random
from io import BytesIO

log = logging.getLogger(__name__)


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

    # def __str__(self):
    #     return str(self.message).format(self.error)


class ConfigTemplate(object):
    """ This is config template dict. DO NOT MODIFY THIS OBJECT."""
    def __init__(self):
        self.template = {'zabbix': {'url': str(), 'login': str(), 'password': str()},
                         'map': {'name': str(), 'bgcolor': str(), 'fontsize': 10, 'width': int(), 'height': int()},
                         'table': {'show': False, 'x': int(), 'y': int()},
                         'link': {'width': 10, 'bandwidth': 100},
                         'palette': Palette().palette_default,
                         'node-': {'name': str(), 'label': str(), 'icon': str(), 'x': int(), 'y': int()},
                         'link-': {'node1': str(), 'node2': str(), 'name1': str(), 'name2': str(), 'copy': '0',
                                   'hostname': str(), 'itemin': str(), 'itemout': str(), 'width': int(),
                                   'bandwidth': int()}
                         }
        log.debug('Object ConfigTemplate created')


class ConfigLoader(object):
    def __init__(self):

        self.template = ConfigTemplate().template
        self.cfg_dict = {}
        self.zbx = None
        self.obj_nodes = {}
        self.obj_links = {}
        log.debug('Object ConfigLoader created')

    def load(self, path_cfg):
        with open(path_cfg, 'r') as stream:
            try:
                self.cfg_dict = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        log.debug('Config loaded')

    def check(self):
        for cfg_sect in self.template:
            if cfg_sect == 'node-':
                for node in sorted([node for node in self.cfg_dict.keys() if cfg_sect in node]):
                    for cfg_opt in self.template[cfg_sect]:
                        try:
                            self.cfg_dict[node][cfg_opt]
                        except KeyError:
                            if cfg_opt == 'icon':
                                self.cfg_dict[node][cfg_opt] = str()
                                continue
                            if cfg_opt == 'label':
                                self.cfg_dict[node][cfg_opt] = str()
                                continue
                            raise ConfigException('The option: {0} is missing in section: [{1}]'
                                                  .format(cfg_sect, cfg_opt))

            if cfg_sect == 'link-':
                for link in sorted([link for link in self.cfg_dict.keys() if cfg_sect in link]):
                    for cfg_opt in self.template[cfg_sect]:
                        try:
                            self.cfg_dict[link][cfg_opt]
                        except KeyError:
                            if cfg_opt == 'copy':
                                self.cfg_dict[node][cfg_opt] = False
                                continue
                            if cfg_opt == 'width':
                                self.cfg_dict[node][cfg_opt] = int()
                                continue
                            if cfg_opt == 'bandwith':
                                self.cfg_dict[node][cfg_opt] = int()
                                continue
                            raise ConfigException('The option: {0} is missing in section: [{1}]'
                                                  .format(cfg_sect, cfg_opt))

            if cfg_sect == 'palette':
                if len(self.cfg_dict[cfg_sect]) != 9:
                    raise ConfigException('Error in section {0}, number elements not equal 9'.format(cfg_sect))
                continue

            for cfg_opt in self.template[cfg_sect]:
                try:
                    self.cfg_dict[cfg_sect][cfg_opt]
                except KeyError:
                    if cfg_sect == 'map' and cfg_opt == 'bgcolor':
                        self.cfg_dict[cfg_sect][cfg_opt] = str()
                    raise ConfigException('The option: {0} is missing in section: [{1}]'.format(cfg_sect, cfg_opt))
        log.debug('Config check: Ok')

    def create_map(self, font_path_fn, icon_path):
        palette = [self.cfg_dict['palette'][key] for key in sorted(self.cfg_dict['palette'])]
        fontsize = int(self.cfg_dict['map']['fontsize'])

        for node in self.obj_nodes.keys():
            x = int(self.cfg_dict[node]['x'])
            y = int(self.cfg_dict[node]['y'])
            label = self.cfg_dict[node]['label']
            icon = self.cfg_dict[node]['icon']
            self.obj_nodes[node] = (Node(font_path_fn, icon_path, x=x, y=y, label=label, icon=icon, fontsize=fontsize))

        for link in self.obj_links.keys():
            node1 = self.obj_nodes[self.cfg_dict[link]['node1']]
            node2 = self.obj_nodes[self.cfg_dict[link]['node2']]
            bandwidth = int(self.cfg_dict[link]['bandwidth'])
            width = int(self.cfg_dict[link]['width'])
            hostname = self.cfg_dict[link]['hostname']
            item_in = self.cfg_dict[link]['itemin']
            item_out = self.cfg_dict[link]['itemout']
            self.obj_links[link] = (Link(font_path_fn, node1, node2, bandwidth=bandwidth, width=width,
                                         palette=palette, fontsize=fontsize))
            data_in, data_out = self.zbx.get_item_data2(hostname, item_in, item_out)
            self.obj_links[link].data(in_bps=data_in, out_bps=data_out)

        if int(self.cfg_dict['table']['show']):
            table = Table(font_path_fn, x=int(self.cfg_dict['table']['x']), y=int(self.cfg_dict['table']['y']),
                          palette=palette)
        else:
            table = None

        map_width = int(self.cfg_dict['map']['width'])
        map_height = int(self.cfg_dict['map']['height'])
        if self.cfg_dict['map']['bgcolor']:
            map_bgcolor = self.cfg_dict['map']['bgcolor']
        else:
            map_bgcolor = None
        map_obj = Map(self.obj_links.values(), self.obj_nodes.values(), table=table, len_x=map_width,
                      len_y=map_height, bgcolor=map_bgcolor)
        return map_obj

    def upload(self, img_path_fn):
        self.zbx.image_to_zabbix(img_path_fn, self.cfg_dict['map']['name'])
