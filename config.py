#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ConfigParser

#Application directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

#Config file name
CONFIG_FILE = 'topaz.conf'

if os.path.isfile(os.path.join(APP_DIR, CONFIG_FILE)):
	cnf = os.path.join(APP_DIR, CONFIG_FILE)

elif os.path.isfile(os.path.join('/etc/topaz', CONFIG_FILE)):
	cnf = os.path.join('/etc/topaz', CONFIG_FILE)

else:
	raise Exception("Topaz configure file %s is not exists" % CONFIG_FILE)

config = ConfigParser.ConfigParser()
config.read(cnf)

dbfile = config.get('General', 'DB')

if __name__ == '__main__':
	print config.get('General', 'DB')