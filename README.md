# Zabbix-Network-Weathermap
[![Code Health](https://landscape.io/github/Prototype-X/Zabbix-Network-Weathermap/master/landscape.svg?style=flat)](https://landscape.io/github/Prototype-X/Zabbix-Network-Weathermap/master)

Network weathermap for Zabbix like [Network Weathermap](http://network-weathermap.com)

###Features ###
* Get source data from Zabbix
* Generate map config from Zabbix map
* Create image with map in PNG format
* Upload image to Zabbix

###Requrements ###
* Zabbix 3.0 (maybe work with Zabbix 2.0)
* Python 3.4.3 and above
* libs: Pillow, py-zabbix

###Install ###

    sudo apt-get install python3-pip python3-pil
    sudo pip3 install py-zabbix
    unzip Zabbix-Network-Weathermap-master.zip -d /opt
    chown -R zabbix:zabbix /opt/Zabbix-Network-Weathermap/*
    chmod a+x /opt/Zabbix-Network-Weathermap/starter.py
    chmod a+x /opt/Zabbix-Network-Weathermap/weathermap.py
    cp /opt/Zabbix-Network-Weathermap/template/userparameter_weathermap.conf /etc/zabbix/zabbix_agentd.d/

* import template /template/weathermap.xml to zabbix
* add Template Weathermap to host (for example use host zabbix server)
* create new user with permissions Zabbix Admin
* user must have read-only or read-write access to hosts and hosts groups present in map

###Screenshot ###
![map screenshot](https://cloud.githubusercontent.com/assets/12714643/14538840/63cf2870-0286-11e6-98f2-d67f548a0d54.png)

###Scripts ###

Default path:

**/opt/Zabbix-Network-Weathermap/mapcfgs - map config dir**

**/opt/Zabbix-Network-Weathermap/mapimgs - map images dir**

**/opt/Zabbix-Network-Weathermap/icons - map icons dir**


    usage: weathermap.py [-v] [-h] [-d] [-m MAP [MAP ...]] [-i IMG] [-u] [-c CFG] [-s SCAN [SCAN ...]] [-f]
                         [-z ZABBIX] [-l LOGIN] [-p PWD]

    Network weathermap for Zabbix

    optional arguments:
    -v, --version                             show version
    -h, --help                                show help
    -d, --debug                               Enable debug mode
    -m MAP [MAP ..], --map MAP [MAP ..]       Config file names
    -i IMG, --img IMG                         Image path
    -u, --upload                              Image upload to zabbix
    -c CFG, --cfg CFG                         Config path
    -s SCAN [SCAN ..], --scan SCAN [SCAN ..]  Map names in Zabbix
    -f, --file                                Zabbix authentication from map config file
    -z ZABBIX, --zabbix ZABBIX                Zabbix server url
    -l LOGIN, --login LOGIN                   Login
    -p PWD, --pwd PWD                         Password

starter.py run weathermap.py and return execution time.

For example, map name test_map.

Map scanning for the first time, map config file not exist

      weathermap.py -s test_map -z http://zabbix.example.com -l admin -p admin

After execution will be created file /opt/Zabbix-Network-Weathermap/mapcfgs/test_map.cfg

Open file test_map.cfg and set hostname and itemin, itemout.

    [link-1]
    node1 = node-Router
    node2 = node-Switch
    name1 =
    name2 =
    width = 15
    hostname = Router
    #itemin/itemout = item key name
    itemin = ifHCInOctets[ge-0/0/0]
    itemout = ifHCOutOctets[ge-0/0/0]

Create map image and upload it in Zabbix

    weathermap.py -m test_map.cfg -u


Set Zabbix -> Monitoring -> Maps -> test_map -> Properties -> Background image -> test_map

For auto update image or rescan map you can use cron or Template Weathermap.

###Map config ###

Option copy type bool, copy link and nodes in new config, when link and nodes not exist in zabbix map

    [link-123sd34]
    node1 = node-3434rert
    node2 = node-sertgreg
    name1 = netw
    name2 = IPTV
    copy = 1
    hostname = D-Link-A
    itemin = ifHCOutOctets[1/6]
    itemout = ifHCInOctets[1/6]

###Notice ###
Zabbix API performance is low. Zabbix agent run weathermap.py. Weathermap.py can be terminated by timeout, set in
zabbix_agentd.conf.

Decision:
1. Increase the timeout for example: zabbix_agentd.conf set Timeout=10
2. One item to one map in Template Weathermap
3. Use cron to run the scripts

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Prototype-X/Zabbix-Network-Weathermap?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
