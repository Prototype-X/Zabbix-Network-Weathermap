#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'

import os
import logging
import configparser
from zabbix import ZabbixAgent
from mapping import Node, Link, Map, Table
from PIL import Image
import base64
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
        self.base = {'zabbix': {'url': str(), 'login': str(), 'password': str()},
                     'map': {'name': str(), 'bgcolor': str(), 'fontsize': '10', 'width': int(), 'height': int()},
                     'table': {'show': False, 'x': int(), 'y': int()},
                     'link': {'width': 10, 'bandwidth': 100},
                     'palette': {'0': '#908C8C', '1': '#FFFFFF', '2': '#8000FF',
                                 '3': '#0000FF', '4': '#00EAEA',
                                 '5': '#00FF00', '6': '#FFFF00',
                                 '7': '#FF6600', '8': '#FF0000'}
                     }

        self.node = {'name': str(), 'label': str(), 'icon': str(), 'x': int(), 'y': int()}
        self.link = {'node1': str(), 'node2': str(), 'name1': str(), 'name2': str(), 'hostname': str(),
                     'itemin': str(), 'itemout': str(), 'width': int(), 'bandwidth': int()}


class ConfigLoader(object):
    def __init__(self, path_cfg):
        self.config = configparser.ConfigParser()
        if self.config.read(path_cfg):
            self.config.read(path_cfg)
        else:
            raise ConfigException('file not found: {0}'.format(path_cfg))
        self.obj_nodes = {}
        self.obj_links = {}
        self.template = ConfigTemplate()
        self.cfg_dict = {}
        self.zbx = None

    def load(self):

        base = self.template.base.copy()
        node = self.template.node.copy()
        link = self.template.link.copy()

        for section in base.keys():
            if not self.config.has_section(section):
                raise ConfigException('section [{0}] is not present in the config'.format(section))

            for option in base[section]:
                if not self.config.has_option(section, option):
                    raise ConfigException('The option: {0} is missing in section: [{1}]'.format(option, section))
                else:
                    base[section][option] = self.config[section][option]

        for name in self.config.sections():
            if 'node-' in name:
                for option in node:
                    if not self.config.has_option(name, option):
                        raise ConfigException('The option: {0} is missing in section: [{1}]'.format(option, name))
                    else:
                        node[option] = self.config[name][option]
                self.obj_nodes[name] = None
                base[name] = node.copy()
                node = node.fromkeys(node)

            if 'link-' in name:
                for option in link:
                    try:
                        link[option] = self.config[name][option]
                    except (configparser.NoOptionError, KeyError):
                        if option == 'width':
                            link['width'] = self.config['link']['width']
                        elif option == 'bandwidth':
                            link['bandwidth'] = self.config['link']['bandwidth']
                        elif not self.config.has_option(name, option):
                            raise ConfigException('The option: {0} is missing in section: [{1}]'
                                                  .format(option, name))
                if link['hostname'] and link['itemin'] and link['itemout']:
                    self.obj_links[name] = None
                base[name] = link.copy()
                link = link.fromkeys(link)
        log.debug('Config dict: %s', base)
        self.cfg_dict = base.copy()
        self.zbx = ZabbixAgent(self.cfg_dict['zabbix']['url'], self.cfg_dict['zabbix']['login'],
                               self.cfg_dict['zabbix']['password'])

        del base
        del node
        del link

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


class ConfigCreate(object):
    def __init__(self, map_data, zbx_agent):
        self.zbx = zbx_agent
        self.map_data = map_data
        self.template = ConfigTemplate()
        self.map_config = configparser.ConfigParser()
        # self.path = str(os.path.dirname(os.path.abspath(__file__)))
        self.dict_call = [self.zbx.get_hostname, self.zbx.get_mapname,
                          self.zbx.get_triggername, self.zbx.get_hostgroupname,
                          self.zbx.get_imagename]
        self.cfg_loader_obj = None

    def create(self):
        elemid_dict = {}
        self.map_config.add_section('zabbix')
        self.map_config['zabbix']['url'] = self.zbx.url
        self.map_config['zabbix']['login'] = self.zbx.login
        self.map_config['zabbix']['password'] = self.zbx.password
        self.map_config.add_section('map')
        self.map_config['map']['name'] = self.map_data['name']
        self.map_config['map']['bgcolor'] = ''
        self.map_config['map']['fontsize'] = self.template.base['map']['fontsize']
        self.map_config['map']['width'] = self.map_data['width']
        self.map_config['map']['height'] = self.map_data['height']
        self.map_config.add_section('table')
        self.map_config['table']['show'] = '0'
        self.map_config['table']['x'] = str(int(self.map_data['width']) - 100)
        self.map_config['table']['y'] = str(int(self.map_data['height']) - 300)
        self.map_config.add_section('palette')
        self.map_config['palette'] = self.template.base['palette']
        self.map_config.add_section('link')
        self.map_config['link'] = self.template.base['link']

        for node in self.map_data['selements']:
            nodeid = node['selementid']
            nodename = self.dict_call[int(node['elementtype'])](node['elementid'])
            elemid_dict[node['selementid']] = nodename

            self.map_config.add_section('node-' + nodeid)
            self.map_config['node-' + nodeid]['name'] = self.dict_call[int(node['elementtype'])](node['elementid'])
            self.map_config['node-' + nodeid]['label'] = ''
            self.map_config['node-' + nodeid]['icon'] = ''
            image_b64code = self.zbx.image_get(node['iconid_off'])
            im = Image.open(BytesIO(base64.b64decode(image_b64code)))
            width, height = im.size
            self.map_config['node-' + nodeid]['x'] = str(int(node['x']) + int(width//2))
            self.map_config['node-' + nodeid]['y'] = str(int(node['y']) + int(height//2))

        for link in self.map_data['links']:
            self.map_config.add_section('link-' + link['linkid'])
            self.map_config['link-' + link['linkid']]['node1'] = 'node-' + link['selementid1']
            self.map_config['link-' + link['linkid']]['node2'] = 'node-' + link['selementid2']
            self.map_config['link-' + link['linkid']]['name1'] = elemid_dict[link['selementid1']]
            self.map_config['link-' + link['linkid']]['name2'] = elemid_dict[link['selementid2']]
            self.map_config['link-' + link['linkid']]['hostname'] = ''
            self.map_config['link-' + link['linkid']]['itemin'] = ''
            self.map_config['link-' + link['linkid']]['itemout'] = ''

        del elemid_dict

    def save(self, path):
        with open(path + '/' + self.map_data['name'] + '.cfg', 'w') as cfg_file:
            self.map_config.write(cfg_file)

    def check_map(self, old_cfg_path):
        old_cfg_path_fn = old_cfg_path + '/' + self.map_data['name'] + '.cfg'
        exist = os.path.exists(old_cfg_path_fn)
        if exist:
            self._compare(old_cfg_path_fn)

    def _compare(self, old_cfg_path_file):

        self.cfg_loader_obj = ConfigLoader(old_cfg_path_file)
        config_old = self.cfg_loader_obj.config

        for section in self.template.base.keys():
            if section == 'zabbix' or section == 'map':
                continue
            for option in self.template.base[section]:
                self.map_config[section][option] = config_old[section][option]

        for section in self.map_config.sections():
            if 'node-' in section:
                if config_old.has_section(section):
                    self.map_config[section]['label'] = config_old[section]['label']
                    self.map_config[section]['icon'] = config_old[section]['icon']
            if 'link-' in section:
                if config_old.has_section(section):
                    self.map_config[section]['hostname'] = config_old[section]['hostname']
                    self.map_config[section]['itemin'] = config_old[section]['itemin']
                    self.map_config[section]['itemout'] = config_old[section]['itemout']
                    if config_old.has_option(section, 'width'):
                        self.map_config[section]['width'] = config_old[section]['width']
                    if config_old.has_option(section, 'bandwidth'):
                        self.map_config[section]['bandwidth'] = config_old[section]['bandwidth']
