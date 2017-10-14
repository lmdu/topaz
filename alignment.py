#!/usr/bin/env python
# -*- coding: utf-8 -*-
import attr

from command import *


@attr.s
class AlignmentRecord(object):
	'''
	alignment result record with 12 columns and convert each
	column to correct data type
	@para query, query sequence id
	@para subject, subject sequence id
	@para identity, similarity identity
	@para matches, alignment length
	@para mismatch, mismatches
	@para gapopen, gap opens
	@para qstart, query start
	@para qend', query end
	@para sstart' subject start
	@para send', subject end
	@para evalue', alignment evalue
	@para score', alignment bit score
	'''
	query = attr.ib()
	subject = attr.ib()
	identity = attr.ib(convert=float)
	matches = attr.ib(convert=int)
	mismatch = attr.ib(convert=int)
	gapopen = attr.ib(convert=int)
	qstart = attr.ib(convert=int)
	qend = attr.ib(convert=int)
	sstart = attr.ib(convert=int)
	send = attr.ib(convert=int)
	evalue = attr.ib(convert=float)
	score = attr.ib(convert=float)

	@classmethod
	def from_string(cls, record):
		cols = record.strip().split('\t')
		return cls(*cols)


@attr.s
class AlignmentParaser(object):
	'''
	A generator for parsing alignment tabular result to
	get each record in output tabular file
	@para alignment_fh, alignment file handler
	'''
	alignment_fh = attr.ib()
	query_name = attr.ib(init=False)
	prev_record = attr.ib(init=False)

	#@alignment_file.validator
	#def check_alignment_file(self, attribute, value):
	#	if not os.path.isfile(value):
	#		raise Exception("** %s alignment is not exists **" % value)

	#	if not os.path.getsize(value):
	#		raise Exception("** No alignment record in file %s **" % value)
	
	@query_name.default
	def get_first_query(self):
		for line in self.alignment_fh:
			if line[0] == '#' or not line.strip():
				continue
			self.prev_record = AlignmentRecord.from_string(line)
			return self.prev_record.query

	def __iter__(self):
		return self

	def next(self):
		rows = [self.prev_record]

		for line in self.alignment_fh:
			row = AlignmentRecord.from_string(line)
			
			if row.query != self.query_name and rows:
				self.prev_record = row
				self.query_name = row.query
				return rows
			
			rows.append(row)

		if rows and self.prev_record is not None:
			self.prev_record = None
			return rows

		raise StopIteration


@attr.s
class Aligner(object):
	'''
	@para query, input FASTA file with multiple sequences
	@para outdir, output directory
	@para db, protein database file path
	@para cpus, number of CPUs
	@para evalue, expected value 1e-5
	@para seqtype, the query sequence type dna or protein
	@para mode, only used by diamond and rapsearch, fast or sensitive
	'''
	query = attr.ib()
	db = attr.ib()
	outdir = attr.ib()
	cpus = attr.ib(default=1)
	evalue = attr.ib(default=1e-5)
	seqtype = attr.ib(default='dna')
	mode = attr.ib(default='sensitive')
	
	outfile = attr.ib()
	
	@outfile.default
	def get_output_file(self):
		'''
		create a output result file in the outdir
		'''
		aligner = self.__class__.__name__.split('Aligner')[0].lower()
		outname = "%s_aligned_to_%s.out" % (aligner, os.path.basename(self.db))
		return os.path.join(self.outdir, outname)


@attr.s
class BlastAligner(Aligner):
	'''
	Align sequence to protein database using blast
	'''
	def execute(self):
		aligner = blastx
		if self.seqtype == 'protein':
			aligner = blastp

		aligner(
			"-num_threads", self.cpus,
			"-word_size", 3,
			"-max_hsps", 20,
			"-num_alignments", 20,
			outfmt = 6,
			db = self.db,
			query = self.query,
			out = self.outfile,
			evalue = self.evalue
		)

	@staticmethod
	def make_blast_db(infile, outfile):
		'''
		make protein database for blast aligner
		@para infile, the input protein fasta
		@para outfile, the output file with basename
		'''
		return makeblastdb('-in', infile, dbtype='prot', out=outfile)


@attr.s
class DiamondAligner(Aligner):
	'''
	Align sequence to protein database using diamond
	'''
	def execute(self):
		aligner = diamond.blastx
		if self.seqtype == 'protein':
			aligner = diamond.blastp
		
		flag = self.mode == 'sensitive'
	
		aligner(
			outfmt = 6,
			db = self.db,
			query = self.query,
			out = self.outfile,
			evalue = self.evalue,
			threads = self.cpus,
			sensitive = not flag,
			more_sensitive = flag
		)

	@staticmethod
	def make_diamond_db(infile, outfile):
		'''
		make protein database for blast aligner
		@para infile, the input protein fasta
		@para outfile, the output file with basename
		'''
		return diamond.makedb('--in', infile, db=outfile)


@attr.s
class RAPSearchAligner(Aligner):
	'''
	Align sequence to protein database using rapsearch2	
	'''
	def execute(self):
		types = {'dna': 'n', 'protein': 'a'}
		modes = {'fast': 't', 'sensitive': 'f'}
		rapsearch(
			q = self.query,
			d = self.db,
			o = self.outfile,
			z = self.cpus,
			e = self.evalue,
			t = types[self.seqtype],
			a = modes[self.mode],
			s = 'f',
			b = 0
		)
		os.rename("%s.m8" % self.outfile, self.outfile)

	@staticmethod
	def make_rapsearch_db(infile, outfile):
		'''
		make protein database for rapsearch2 aligner
		@para infile, the input protein fasta
		@para outfile, the output file with basename
		'''
		return prerapsearch(d=infile, n=outfile)


@attr.s
class Alignment(Aligner):
	'''
	@para aligner, the alignment tool to be used
	@para query, input FASTA file with multiple sequences
	@para outdir, output directory
	@para db, protein database file path
	@para cpus, number of CPUs
	@para evalue, expected value 1e-5
	@para seqtype, the query sequence type dna or protein
	@para mode, only used by diamond and rapsearch, fast or sensitive
	'''
	aligner = attr.ib()
	query = attr.ib()
	db = attr.ib()
	outdir = attr.ib()
	cpus = attr.ib(default=1)
	evalue = attr.ib(default=1e-5)
	seqtype = attr.ib(default='dna')
	mode = attr.ib(default='sensitive')

	aligners = attr.ib(
		default = dict(
			blast = BlastAligner,
			diamond = DiamondAligner,
			rapsearch = RAPSearchAligner
		),
		init = False
	)

	@property
	def execute(self):
		'''
		get alingment tool specified by user
		'''
		return self.aligners[self.aligner]

	def run_alignment(self):
		'''
		start alignment and return proccess object
		'''
		return self.execute(
			query = self.query,
			db = self.db,
			outdir = self.outdir,
			cpus = self.cpus,
			evalue = self.evalue,
			seqtype = self.seqtype,
			mode = self.mode
		)


if __name__ == '__main__':
	with open('blast_aligned_to_sp.out') as fh:
		for records in AlignmentParaser(fh):
			for record in records:
				print record
				break

