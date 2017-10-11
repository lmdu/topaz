#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

#Diamond aligner
diamond = sh.Command('diamond').bake(_long_sep=' ', outfmt=5)

#blast aligner
blastx = sh.Command('blastx').bake(_long_prefix='-', _long_sep=' ', outfmt=5)
blastp = sh.Command('blastp').bake(_long_prefix='-', _long_sep=' ', outfmt=5)
makeblastdb = sh.Command('makeblastdb').bake(_long_prefix='-', _long_sep=' ')

#rapsearch
prerapsearch = sh.Command('prerapsearch')
rapsearch = sh.Command('rapsearch')
