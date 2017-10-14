#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sh
import attr

#diamond alignment tool
diamond = sh.diamond.bake(
	_long_sep = ' '
)

#blast alignment tool
blastx = sh.blastx.bake(
	_long_prefix = '-',
	_long_sep = ' '
)
blastp = sh.blastp.bake(
	_long_prefix = '-',
	_long_sep = ' '
)
makeblastdb = sh.makeblastdb.bake(
	_long_prefix='-',
	_long_sep=' '
)

#rapsearch alignment tool
prerapsearch = sh.prerapsearch
rapsearch = sh.rapsearch

