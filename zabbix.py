#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'

import logging
from pyzabbix import ZabbixAPI
import base64

log = logging.getLogger(__name__)


class ZbxException(Exception):
    def __init__(self, message):
        self.message = message


class ZabbixAgent(object):

    def __init__(self, url, login, password):
        self.url = url
        self.login = login
        self.password = password
        self.zbx_api = ZabbixAPI(url=url, use_authenticate=False, user=login, password=password)
        log.debug('API ver. %s', self.api_ver())

    def get_item_data(self, hostname, item):
        hostid = self.zbx_api.host.get(filter={'name': hostname}, output='shorten')[0]['hostid']
        log.debug('hostID %s', hostid)
        if not hostid:
            raise ZbxException("hostname: {} not found".format(hostname))

        item_data = self.zbx_api.item.get(filter={'hostid': hostid, 'key_': item}, output=['lastvalue'])
        log.debug('itemID %s', hostid)
        if not item_data:
            raise ZbxException('item: {} not found'.format(item))

        if len(item_data) > 1:
            raise ZbxException('return items expected one item')
        return int(item_data[0]['lastvalue'])

    def get_item_data2(self, hostname, item_in, item_out):
        hostid = self.zbx_api.host.get(filter={'name': hostname}, output='shorten')[0]['hostid']
        log.debug('hostID %s', hostid)
        if not hostid:
            raise ZbxException("hostname: {} not found".format(hostname))

        item_in_data = self.zbx_api.item.get(filter={'hostid': hostid, 'key_': item_in}, output=['lastvalue'])
        log.debug('itemID %s', hostid)
        if not item_in_data:
            raise ZbxException('item: {} not found'.format(item_in))

        item_out_data = self.zbx_api.item.get(filter={'hostid': hostid, 'key_': item_out}, output=['lastvalue'])
        log.debug('itemID %s', hostid)
        if not item_in_data:
            raise ZbxException('item: {} not found'.format(item_out))

        if len(item_in_data) > 1:
            raise ZbxException('return items expected one item: {}'.format(item_in_data))

        if len(item_out_data) > 1:
            raise ZbxException('return items expected one item: {}'.format(item_out_data))

        return int(item_in_data[0]['lastvalue']), int(item_out_data[0]['lastvalue'])

    def api_ver(self):
        return self.zbx_api.api_version()

    def scan_map(self, map_name):
        map_data = self.zbx_api.map.get(filter={'name': map_name},
                                        selectSelements=['elementid', 'selementid', 'elementtype', 'iconid_off',
                                                         'x', 'y'],
                                        selectLinks=['selementid1', 'selementid2', 'linkid']
                                        )
        if not map_data:
            raise ZbxException('map: {} not found'.format(map_name))

        if len(map_data) > 1:
            raise ZbxException('return mapss expected one map')
        return map_data[0]

    def scan_map_all(self):
        maps_data = self.zbx_api.map.get(selectSelements=['elementid', 'selementid', 'elementtype', 'iconid_off',
                                                          'x', 'y'],
                                         selectLinks=['selementid1', 'selementid2', 'linkid'])
        if not maps_data:
            raise ZbxException('maps not found')

        if len(maps_data) > 1:
            raise ZbxException('return maps expected one map')
        return maps_data

    def get_hostname(self, hostid):
        hostname = self.zbx_api.host.get(hostids=hostid, output=['host'])

        if not hostname:
            raise ZbxException('hostname not found')

        if len(hostname) > 1:
            raise ZbxException('return hostnames expected one hostname')

        return hostname[0]['host']

    def get_mapname(self, mapid):
        mapname = self.zbx_api.map.get(sysmapids=mapid, output=['name'])

        if not mapname:
            raise ZbxException('map name not found')

        if len(mapname) > 1:
            raise ZbxException('return map names expected one map name')

        return mapname[0]['name']

    def get_triggername(self, triggerid):
        triggername = self.zbx_api.trigger.get(triggerid=triggerid, output=['description'])

        if not triggername:
            raise ZbxException('trigger name not found')

        if len(triggername) > 1:
            raise ZbxException('return trigger names expected one trigger name')

        return triggername[0]['description']

    def get_hostgroupname(self, groupid):
        hostgroupname = self.zbx_api.hostgroup.get(groupids=groupid, output=['name'])

        if not hostgroupname:
            raise ZbxException('hostgroup name not found')

        if len(hostgroupname) > 1:
            raise ZbxException('return hostgroup names expected one hostgroup name')

        return hostgroupname[0]['name']

    def get_imagename(self, imageid):
        imagename = self.zbx_api.image.get(imageids=imageid, output=['name'])

        if not imagename:
            raise ZbxException('image name not found')

        if len(imagename) > 1:
            raise ZbxException('return image names expected one image name')

        return imagename[0]['name']

    def image_to_zabbix(self, pathfn, zbx_img_name):
        with open(pathfn, 'rb') as img:
            b64img = base64.b64encode(img.read()).decode()
        image_data = self.zbx_api.image.get(filter={'name': zbx_img_name})
        if not image_data:
            self.zbx_api.image.create(name=zbx_img_name, imagetype=2, image=b64img)
        else:
            self.zbx_api.image.update(imageid=image_data[0]['imageid'], image=b64img)

    def image_get(self, imageid):
        image_data = self.zbx_api.image.get(imageids=imageid, select_image=True)
        return image_data[0]['image']
