#!/usr/bin/env python
# -*- coding: utf-8 -*-

#diamond alignment tool
diamond = sh.Command('diamond').bake(_long_sep=' ', outfmt=5)

#blast alignment tool
blastx = sh.Command('blastx').bake(_long_prefix='-', _long_sep=' ', outfmt=5)
blastp = sh.Command('blastp').bake(_long_prefix='-', _long_sep=' ', outfmt=5)
makeblastdb = sh.Command('makeblastdb').bake(_long_prefix='-', _long_sep=' ')

#rapsearch alignment tool
prerapsearch = sh.Command('prerapsearch')
rapsearch = sh.Command('rapsearch')


def make_protein_db(aligner, infile, outname):
	'''
	make protein database for input fasta file
	@para aligner, alignment tool
	@para infile, the input protein fasta
	@para outname, the output base name
	'''
	if aligner == 'diamond':
		diamond('makedb', '--in', infile, db=outname)

	elif aligner == 'blast':
		makeblastdb(dbtype='prot', '-in', infile, out=outname)

	elif aligner == 'rapsearch':
		prerapsearch(d=infile, n=outname)

	else:
		pass


class Aligner:
	'''
	@para query, input FASTA file with multiple sequences
	@para out, out file name of alignment
	@para db, protein database file path
	@para cpus, number of CPUs
	@para evalue, expected value 1e-5
	@para seqtype, the query sequence type dna or protein
	@para outfmt, output format 5: blast xml, 6: tabular, 101: SAM
	'''
	def __init__(self, query, out, db, cpus=1, evalue=1e-5, seqtype='dna'):
		self.query = query
		self.out = out
		self.db = db
		self.cpus = cpus
		self.evalue = evalue
		self.seqtype = seqtype

class BlastAligner(Aligner):
	'''
	Align sequence to protein database using blast
	'''
	def execute(self):
		executor = blastx
		if self.seqtype == 'protein':
			executor = blastp

		executor(
			db = self.db,
			query = self.query,
			out = self.out,
			evalue = self.evalue,
			num_threads = self.cpus,
			word_size = 3,
			max_hsps = 20,
			num_alignments = 20
		)

class DiamondAligner(Aligner):
	'''
	Align sequence to protein database using diamond
	'''
	def execute(self):
		executor = 'blastx'
		if self.seqtype == 'protein'
			executor = 'blastp'



		diamond(executor,
			db = self.db,
			query = self.query,
			out = self.out,
			evalue = self.evalue,
			threads = self.cpus,
			sensitive = True,

		)









