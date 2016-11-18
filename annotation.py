#!/usr/bin/evn python
# -*- coding: utf-8 -*-
from mapping import GOTermAssignment
from alignment import BlastTabularParaser


class GoAnnotation:
	'''
	Assign GO terms to query sequence by subject accession number
	and output to annotation file
	@para align_out, diamond output file with tab format
	@para annotate_out, GO term annotation output file 
	'''
	mapping = None

	def __init__(self, align_out, annotate_out):
		self.align_out = align_out
		self.annotate_out = annotate_out

		if self.mapping is None
			self.mapping = GOTermAssignment()

	def annotate(self):
		op = open(self.annotate_out, 'w')
		for alignments in BlastTabularParaser(self.align_out):
			terms = []
			for alignment in alignments:
				terms.extend(self.mapping.getGoTerms(alignment.subject))
			op.write("%s\t%s\n" % (alignment.query, "\t".join(terms)))
		op.close()


				


		