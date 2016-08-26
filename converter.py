#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'

import argparse
import configparser
import logging
import yaml
from collections import OrderedDict
import sys
import os
# from mapping import Palette, Singleton

log = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Palette(metaclass=Singleton):
    def __init__(self):
        self.palette = ['#908C8C', '#FFFFFF', '#8000FF', '#0000FF', '#00EAEA', '#00FF00', '#FFFF00', '#FF9933',
                        '#FF0000']
        self.palette_default = ('#908C8C', '#FFFFFF', '#8000FF', '#0000FF', '#00EAEA', '#00FF00', '#FFFF00',
                                '#FF9933', '#FF0000')
        log.debug('Object singleton Palette created')

    def reset(self):
        self.palette = list(self.palette_default)


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

    # def __str__(self):
    #     return str(self.message).format(self.error)


class ConfigTemplateYaml(metaclass=Singleton):
    """ This is config template. DO NOT MODIFY THIS OBJECT."""

    def __init__(self):
        self.template = {'zabbix': {'url': str(), 'login': str(), 'password': str()},
                         'map': {'name': str(), 'bgcolor': str(), 'fontsize': 10, 'width': int(), 'height': int()},
                         'table': {'show': False, 'x': int(), 'y': int()},
                         'link': {'width': 10, 'bandwidth': 100},
                         'palette': Palette().palette,
                         'node-': {'name': str(), 'label': str(), 'icon': str(), 'x': int(), 'y': int()},
                         'link-': {'node1': str(), 'node2': str(), 'name1': str(), 'name2': str(), 'copy': '0',
                                   'hostname': str(), 'itemin': str(), 'itemout': str(), 'width': int(),
                                   'bandwidth': int()}
                         }
        log.debug('Object singleton ConfigTemplateYaml created')


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
                                 '7': '#FF9933', '8': '#FF0000'}
                     }

        self.node = {'name': str(), 'label': str(), 'icon': str(), 'x': int(), 'y': int()}
        self.link = {'node1': str(), 'node2': str(), 'name1': str(), 'name2': str(), 'copy': '0', 'hostname': str(),
                     'itemin': str(), 'itemout': str(), 'width': int(), 'bandwidth': int()}
        log.debug('Object ConfigTemplate created')


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
        log.debug('Object ConfigLoader created')

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
                        elif option == 'copy':
                            pass
                        elif not self.config.has_option(name, option):
                            raise ConfigException('The option: {0} is missing in section: [{1}]'
                                                  .format(option, name))
                if link['hostname'] and link['itemin'] and link['itemout']:
                    self.obj_links[name] = None
                base[name] = link.copy()
                link = link.fromkeys(link)
        log.debug('Config dict: %s', base)
        self.cfg_dict = base.copy()

        print(self.cfg_dict)
        del base
        del node
        del link
        return self.cfg_dict


class ConfigConvert(object):
    def __init__(self, cfg_dict: dict):
        self.cfg_dict = cfg_dict
        self.template = ConfigTemplateYaml().template
        self.setup_yaml()
        self.palette_convert()
        log.debug('Object ConfigCreate created')

    def palette_convert(self):
        palette_new = list([self.cfg_dict['palette'][str(i)] for i in range(0, 9)])
        print(palette_new)
        self.cfg_dict['palette'] = palette_new

    @staticmethod
    def setup_yaml():
        """ StackOverflow Driven Development
        http://stackoverflow.com/a/8661021 """

        def represent_dict_order(yaml_self, data):
            return yaml_self.represent_mapping('tag:yaml.org,2002:map', data.items())

        yaml.add_representer(OrderedDict, represent_dict_order)

    @staticmethod
    def _dict_to_orderdict(cfg: dict) -> OrderedDict:
        cfg_order = OrderedDict()
        cfg_templ = OrderedDict([('map', ('name', 'bgcolor', 'fontsize', 'width', 'height')),
                                 ('zabbix', ('url', 'login', 'password')),
                                 ('table', ('show', 'x', 'y')),
                                 ('palette', None),
                                 ('link', ('bandwidth', 'width')),
                                 ('node-', ('name', 'label', 'icon', 'x', 'y')),
                                 ('link-',
                                  ('node1', 'node2', 'name1', 'name2', 'copy', 'hostname', 'itemin', 'itemout'))])

        for cfg_sect in cfg_templ:

            if cfg_sect == 'node-':
                for node in sorted([node for node in cfg.keys() if cfg_sect in node]):
                    cfg_order[node] = OrderedDict()
                    for cfg_opt in cfg_templ[cfg_sect]:
                        if cfg_opt == 'icon' and cfg_opt not in cfg[node]:
                            continue
                        if cfg_opt == 'label' and cfg_opt not in cfg[node]:
                            continue
                        cfg_order[node][cfg_opt] = cfg[node][cfg_opt]
                continue

            if cfg_sect == 'link-':
                for link in sorted([link for link in cfg.keys() if cfg_sect in link]):
                    cfg_order[link] = OrderedDict()
                    for cfg_opt in cfg_templ[cfg_sect]:
                        if cfg_opt == 'copy' and cfg_opt not in cfg[link]:
                            continue
                        if cfg_opt == 'width' and cfg_opt not in cfg[link]:
                            continue
                        if cfg_opt == 'bandwith' and cfg_opt not in cfg[link]:
                            continue
                        cfg_order[link][cfg_opt] = cfg[link][cfg_opt]
                continue

            cfg_order[cfg_sect] = OrderedDict()
            if cfg_sect == 'palette':
                cfg_order[cfg_sect] = cfg[cfg_sect]
                continue

            for cfg_opt in cfg_templ[cfg_sect]:
                if cfg_sect == 'map' and cfg_opt == 'bgcolor' and cfg_opt not in cfg[cfg_sect]:
                    continue
                cfg_order[cfg_sect][cfg_opt] = cfg[cfg_sect][cfg_opt]
        print(cfg_order)
        return cfg_order

    def save(self, path: str):
        cfg = self._dict_to_orderdict(self.cfg_dict)
        with open(path + '/' + self.cfg_dict['map']['name'] + '.yaml', 'w') as cfg_file:
            try:
                yaml.dump(cfg, cfg_file, explicit_start=True, explicit_end=True, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)


def main():
    root_path = str(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(conflict_handler='resolve', description='Convert to yaml')
    parser.add_argument('cfg', action='store', type=str, help='Old style config file')
    args = parser.parse_args()
    if args.cfg:
        cfg_dict = ConfigLoader(args.cfg).load()
        cfg_yaml = ConfigConvert(cfg_dict)
        cfg_yaml.save(root_path)
    else:
        sys.exit()

if __name__ == '__main__':
    main()
