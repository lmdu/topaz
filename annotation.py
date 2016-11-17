#!/usr/bin/evn python
# -*- coding: utf-8 -*-
from mapping import Mapping
from diamond import DiamondResultParaser


class Annotation:
	'''
	Assign GO terms to query sequence by subject accession number
	and output to annotation file
	@para diamond_output, diamond output file with tab format
	@para annotate_output, GO term annotation output file 
	'''
	def __init__(self, diamond_output, annotate_output):
		self.diamond_output = diamond_output
		self.annotate_output = annotate_output

		#create a mapping instance
		self.mapper = Mapping()

	def annotate(self):
		for alignments in DiamondResultParaser(self.diamond_output):
			query = alignments[0].query
			for alignment in alignments:
				


		