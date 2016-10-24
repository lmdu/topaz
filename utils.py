#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import coloredlogs

#color the logging output
coloredlogs.install(level='DEBUG')

logging.basicConfig(level=logging.DEBUG,
	format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
)

logging.info

class log:
	def info