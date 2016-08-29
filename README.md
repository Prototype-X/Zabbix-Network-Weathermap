# Zabbix-Network-Weathermap

[![Join the chat at https://gitter.im/Prototype-X/Zabbix-Network-Weathermap](https://badges.gitter.im/Prototype-X/Zabbix-Network-Weathermap.svg)](https://gitter.im/Prototype-X/Zabbix-Network-Weathermap?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Code Health](https://landscape.io/github/Prototype-X/Zabbix-Network-Weathermap/master/landscape.svg?style=flat)](https://landscape.io/github/Prototype-X/Zabbix-Network-Weathermap/master)

Network weathermap for Zabbix like [Network Weathermap](http://network-weathermap.com)

###Screenshot ###
![map screenshot](https://cloud.githubusercontent.com/assets/12714643/14538840/63cf2870-0286-11e6-98f2-d67f548a0d54.png)

###Features ###
* Get source data from Zabbix
* Generate YAML config from Zabbix map
* Create image with map in PNG format
* Upload image to Zabbix
* Support for map elements with the type: host, map

###Requrements ###
* Zabbix 3.0 (maybe work with Zabbix 2.0)
* Python 3.4.3 and above
* libs: Pillow, py-zabbix, ruamel.yaml

###Install ###

    sudo apt-get install python3-pip python-pip python3-pil
    sudo pip3 install py-zabbix
    sudo pip install ruamel.yaml
    unzip Zabbix-Network-Weathermap-master.zip -d /opt
    chown -R zabbix:zabbix /opt/Zabbix-Network-Weathermap/*
    chmod a+x /opt/Zabbix-Network-Weathermap/starter.py
    chmod a+x /opt/Zabbix-Network-Weathermap/weathermap.py
    cp /opt/Zabbix-Network-Weathermap/template/userparameter_weathermap.conf /etc/zabbix/zabbix_agentd.d/

* Import template /template/weathermap.xml to zabbix
* Add Template Weathermap to host (for example use host zabbix server)
* Create new user with permissions Zabbix Admin
* User must have read-only or read-write access to hosts and hosts groups present in map
* Go to Zabbix -> Configuration -> Template Weathermap -> Macros:

     {$SCANFILE} - When map config exist. If you change map remove host or change position host, configuration will be updated in accordance with changes on the map.
     
     {$SCANMAP} - First time scan map, config file not exist. Create file with map configuration.
     
     {$UPDATE} - Only create image, like old style Network Weathermap.
     
     {$UPLOAD} - Create and upload image to Zabbix.

* Check Zabbix -> Configuration -> Hosts -> Host with Weathermap template -> Applications -> Weathermap -> Items -> Status

* Create file with map configuration:
        
        weathermap.py -s mapname1 mapnameN -z http://zabbix.example.com -l admin -p admin
    
    OR
    
    Zabbix -> Template Weathermap -> Macros -> {$SCANMAP} -> Value
    
* Open file mapname1.yaml and set hostname and itemin, itemout.

      link-1:
        node1: node-Router
        node2: node-Switch
        name1: R1
        name2: SW1
        width: 15
        hostname: Router
        #itemin/itemout = item key name
        itemin: ifHCInOctets[ge-0/0/0]
        itemout: ifHCOutOctets[ge-0/0/0]

* Create map image and upload it to Zabbix:
    
      
      weathermap.py -m mapname1.yaml -u
  
  OR
  
  Zabbix -> Template Weathermap -> Macros -> {$UPLOAD} -> Value

* Set Zabbix -> Monitoring -> Maps -> mapname1 -> Properties -> Background image -> mapname1


###Scripts note###

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

**starter.py** run weathermap.py and return execution time.

For auto update image or rescan map you can use cron or Template Weathermap.

###Map config ###
        
    %YAML 1.2
    ---
    map:
      name: mapname1
      bgcolor: ''           #background RGB color, default transparent
      fontsize: 10
      width: 1200
      height: 800
    zabbix:
      url: http://zabbix.example.com
      login: admin
      password: admin
    table:                  # show legend and date time
      show: true
      x: 1100
      y: 100
    palette:                # RGB color arrow
    - '#908C8C'
    - '#FFFFFF'
    - '#8000FF'
    - '#0000FF'
    - '#00EAEA'
    - '#00FF00'
    - '#FFFF00'
    - '#FF9933'
    - '#FF0000'
    link:                   # default settings link
      bandwidth: 100        # in Mbits/s
      width: 10             # width arrow in pixels
    node-Router:
      name: Символы         # Get from Zabbix
      label: R1             # For old style Network Weathermap, draw label
      icon: Router64.png    # For old style Network Weathermap, draw icon, if path not exist, use defaults
      x: 625
      y: 225
    node-Router2:
      name: ''
      label: R2
      icon: Router64.png
      x: 625
      y: 225
    node-Switch:
      name: ''
      label: SW1
      icon: Switch64.png
      x: 75
      y: 375
    node-Switch2:
      name: ''
      label: SW2
      icon: Switch64.png
      x: 75
      y: 375
    link-1:
      node1: node-Router
      node2: node-Switch
      name1: ''             # For human readability, get from zabbix
      name2: ''             # For human readability, get from zabbix
      width: 15             # Override default settings in link
      hostname: Router
      itemin: ifHCInOctets[ge-0/0/0]
      itemout: ifHCOutOctets[ge-0/0/0]
    link-2:
      node1: node-Router2
      node2: node-Switch2
      name1: ''
      name2: ''
      bandwidth: 1000        # Override default settings in link
      hostname: Router2
      itemin: ifHCInOctets[ge-0/0/1]
      itemout: ifHCOutOctets[ge-0/0/1]
    ...

Option copy type bool, copy link and nodes in new config, when link and nodes not exist in zabbix map

    link-lyonlz7x:
      node1: node-nridx7c0
      node2: node-uwf443jw
      name1: net1
      name2: net2
      copy: true
      hostname: R10
      itemin: ifHCOutOctets[1/6]
      itemout: ifHCInOctets[1/6]

###Notice ###

Zabbix API performance is low. Zabbix agent run weathermap.py. Weathermap.py can be terminated by timeout, set in
zabbix_agentd.conf.

Decision:

1. Increase the timeout for example: zabbix_agentd.conf set Timeout=10

2. One item to one map in Template Weathermap

3. Use cron to run the scripts

If you need convert from old style config to YAML format, use **converter.py**

    user@pc:~$ converter.py /path-to-old-style-cfg/map.cfg
    user@pc:~$ ls /path-to-old-style-cfg
    map.cfg
    map.yaml
    
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Prototype-X/Zabbix-Network-Weathermap?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
