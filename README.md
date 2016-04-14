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
* Python 3
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

###Screenshot ###
![map screenshot](https://cloud.githubusercontent.com/assets/12714643/14538840/63cf2870-0286-11e6-98f2-d67f548a0d54.png)

###Man ###
