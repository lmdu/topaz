#!/usr/bin/evn python
# -*- coding: utf-8 -*-
import os
import attr

from mapping import GOTermMapper

@attr.s
class Annotator(object):
	'''
	Gene ontology annotation according to alignment file and
	extract go terms for gene from go association database
	'''
	alignment_file = attr.ib()
	go_mapper = attr.ib(init=False)

	@alignment_file.validator
	def check_alignment_file(self):
		if not os.path.exists(self.alignment_file):
			raise Exception("** Alignment file %s is not exists**" % self.alignment_file)

	@go_mapper.default
	def get_go_mapping(self):
		return GOTermMapper()

	def get_go_terms(self, acc):
		'''
		extract GO terms for associated gene by similary accession
		@acc, accession number of gene
		'''
		return self.go_mapper.get_go_terms_by_acc(acc)


@attr.s
class Blast2goAnnotator(Annotator):
	'''
	Implementation of Blast2go annotation method
	'''
	pass



@attr.s
class GotchaAnnotator(Annotator):
	'''
	Implementation of Gotcha annotation method
	'''
	pass




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

		self.annotate()

	def annotate(self):
		op = open(self.annotate_out, 'w')
		for alignments in BlastTabularParaser(self.align_out):
			terms = []
			for alignment in alignments:
				terms.extend(self.mapping.getGoTerms(alignment.subject))
			op.write("%s\t%s\n" % (alignment.query, "\t".join(terms)))
		op.close()


		