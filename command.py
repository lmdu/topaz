#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sh
import attr

#diamond alignment tool
diamond = sh.Command('diamond').bake(
	_long_sep = ' ', 
	outfmt = 5
)

#blast alignment tool
blastx = sh.Command('blastx').bake(
	_long_prefix = '-',
	_long_sep = ' ',
	outfmt = 5
)
blastp = sh.Command('blastp').bake(
	_long_prefix = '-',
	_long_sep = ' ',
	outfmt = 5
)
makeblastdb = sh.Command('makeblastdb').bake(
	_long_prefix='-',
	_long_sep=' '
)

#rapsearch alignment tool
prerapsearch = sh.Command('prerapsearch')
rapsearch = sh.Command('rapsearch').bake(u=1)


@attr.s
class Aligner(object):
	'''
	@para query, input FASTA file with multiple sequences
	@para outdir, output directory
	@para db, protein database file path
	@para cpus, number of CPUs
	@para evalue, expected value 1e-5
	@para seqtype, the query sequence type dna or protein
	@para outfmt, output format 5: blast xml, 6: tabular, 101: SAM
	'''
	query = attr.ib()
	outdir = attr.ib()
	db = attr.ib()
	cpus = attr.ib(default=1)
	evalue = attr.ib(default=1e-5)
	seqtype = attr.ib(default='dna')
	
	outfile = attr.ib()
	
	@outfile.default
	def get_output_file(self):
		'''
		create a output result file in the outdir
		'''
		outname = "%s_aligned_to_%s.out" % (self.aligner, os.path.basename(self.db)) 
		return os.path.join(self.outdir, outname)

	@classmethod
	def makedb(cls, infile, outfile):
		'''
		make protein database for input fasta file
		@para aligner, alignment tool
		@para infile, the input protein fasta
		@para outfile, the output file with basename
		'''
		aligner = cls.aligner.default

		if aligner == 'diamond':
			diamond('makedb', '--in', infile, db=outfile)

		elif aligner == 'blast':
			makeblastdb(dbtype='prot', '-in', infile, out=outfile)

		elif aligner == 'rapsearch':
			prerapsearch(d=infile, n=outfile)

		else:
			pass


@attr.s
class BlastAligner(Aligner):
	'''
	Align sequence to protein database using blast
	'''
	aligner = attr.ib(default='blast', init=False)

	def execute(self):
		executor = blastx
		if self.seqtype == 'protein':
			executor = blastp

		return executor(
			db = self.db,
			query = self.query,
			out = self.outfile,
			evalue = self.evalue,
			num_threads = self.cpus,
			word_size = 3,
			max_hsps = 20,
			num_alignments = 20
		)


@attr.s
class DiamondAligner(Aligner):
	'''
	Align sequence to protein database using diamond
	'''
	aligner = attr.ib(default='diamond', init=False)
	sensitive = attr.ib(default=False)

	def execute(self):
		executor = 'blastx'
		if self.seqtype == 'protein'
			executor = 'blastp'
		
		flag = '--sensitive'
		if self.sensitive:
			flag = '--more-sensitive'
	
		return diamond(executor,
			db = self.db,
			query = self.query,
			out = self.out,
			evalue = self.evalue,
			threads = self.cpus,
			flag
		)


@attr.s
class RAPSearchAligner(Aligner):
	aligner = attr.ib(default='rapsearch', init=False)

	def execute(self):
		types = {'dna': 'n', 'protein': 'a'}
		self.seqtype = types[self.seqtype]

		return rapsearch(
			q = self.query,
			d = self.db,
			o = self.outfile,
			z = self.cpus,
			e = self.evalue,
			t = self.seqtype,
			s = 'f'
		)






