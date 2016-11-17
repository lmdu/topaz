#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import psutil
import subprocess

class FastaUtil:
	'''
	Accept a fasta file and check the fasta and calculate the total,
	N50, mean, median length and number of sequences
	@para fasta, the path of the input fasta file
	'''
	def __init__(self, fasta):
		self.fasta = fasta

		if not os.path.isfile(self.fasta):
			raise Exception(" ** Please provide right query FASTA file **")

		if not self.isFasta():
			raise Exception(" ** The input file is not fasta format file **")

		self.lengths = []
		self.gc = 0


	def isFasta(self):
		'''
		Get first fasta record header and check > to verify fasta format
		@return bool, True if is right fasta or False
		'''
		with open(self.fasta) as fh:
			if fh.readline()[0] == '>':
				return True

		return False

	def getSeqCounts(self):
		'''
		Get total number of sequences in the query fasta file
		@return int, no. of sequences
		'''
		if self.lengths:
			return len(self.lengths)

		with open(self.fasta) as fh:
			return sum(1 for line in fh if line[0] == '>')

	def getSeqLengths(self):
		'''
		Get the lengths of all sequences and GC counts in fasta
		@return list, contains lengths of all sequneces
		'''
		if self.lengths:
			return self.lengths

		contig = 0
		with open(self.fasta) as fh:
			for line in fh:
				line = line.strip()
				
				if not line:
					continue

				if line[0] == '>':
					if contig:
						self.lengths.append(contig)
					
					contig = 0

				else:
					contig += len(line)
					self.gc += line.upper().count('G')
					self.gc += line.upper().count('c')
			else:
				self.lengths.append(contig)

		return self.lengths

	def getSeqTotalLength(self):
		'''
		Get total length of all sequences in fasta
		return int, bp
		'''
		return sum(self.getSeqLengths())

	def getSeqGCContent(self):
		'''
		Get the GC content of sequences in fasta
		@return float, GC content
		'''
		total = float(self.getSeqTotalLength())
		return round(self.gc/total*100, 2)

	def getSeqAverageLength(self):
		'''
		Get the average length of the sequences in fasta
		@return int, average length
		'''
		total = float(self.getSeqTotalLength())
		return int(round(total/self.getSeqCounts()))

	def getSeqAssessVal(self, percent=0.5):
		'''
		Get transcripts assembly assessment value N10, N50, N90
		@para percent float, a percentage value
		@return int, a transcript length
		'''
		lengths = self.getSeqLengths()
		lengths.sort(reverse=True)

		cutoff = self.getSeqTotalLength() * percent
		accumulate = 0
		
		for length in lengths:
			accumulate += length
			if accumulate >= cutoff:
				return length


class Diamond:
	'''
	invoke diamond program to align sequences to NR, SWISS-PROT etc. protein database
	diamond is a alternative program to blast for protein alignment
	'''
	def __init__(self, query, out, db='nr', threads=1, evalue=1e-5, cover=None, 
		sensitive=False, _type='dna', targets=20, outfmt=6):
		'''
		@para query, input FASTA file with multiple sequences
		@para out, diamond out file name
		@para db, protein databases
		@para threads, number of threads for diamond
		@para evalue, expected value 1e-5
		@para cover, percentage of query cover
		@para sensitive, if True open more sensitive alignment mode
		@para _type, the query sequence type dna or protein
		@para targets, output max target seqs
		@para outfmt, output format 5: blast xml, 6: tabular, 101: SAM
		'''
		#parameters that required
		self.query = query
		self.out = out
		self.db = db
		self.type = _type
		self.threads = threads
		self.evalue = evalue
		self.targets = targets
		self.cover = cover
		self.outfmt = outfmt
		self.sensitive = sensitive

		#start the alignment task
		self._execute()

	@property
	def command(self):
		'''
		Generate command list with options
		'''
		cmd = ['diamond']

		if self.type == 'dna':
			cmd.append('blastx')

		else:
			cmd.append('blastp')

		cmd.extend([
			'--query', self.query,
			'--out', self.out,
			'--db', self.db,
			'--threads', str(self.threads),
			'--evalue', str(self.evalue),
			'--max-target-seqs', str(self.targets),
			'--outfmt', str(self.outfmt)
		])

		#open more sensitive alignment mode, default sensitive mode
		if self.sensitive:
			cmd.append('--more-sensitive')

		else:
			cmd.append('--sensitive')

		#set query cover
		if self.cover is not None:
			cmd.extend(['--query-cover', self.cover])

		return cmd

	def _execute(self):
		'''
		Execute diamond program to start alignment
		'''
		proc = psutil.Popen(self.command, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		if proc.returncode != 0:
			raise Exception("** Diamond throw error: %s**" % stderr)


class DiamondAlignmentRecord(dict):
	'''
	Store diamond result record with 12 columns and convert each
	column to correct data type
	@para cols, columns in diamond tabular output file each line
	'''
	fields = [
		('query', str), 		#query sequence id
		('subject', str),		#subject sequence id
		('identity', float),	#similarity identity
		('length', int),		#alignment length
		('mismatch', int),		#mismatches
		('gapopen', int),		#gap opens
		('qstart', int),		#query start
		('qend', int),			#query end
		('sstart', int),		#subject start
		('send', int),			#subject end
		('evalue', float),		#alignment evalue
		('bitscore', float)		#alignment bit score
	]
	
	def __init__(self, cols):
		for idx, val in enumerate(self.fields):
			field, func = val
			self[field] = func(cols[idx])

	def __getattr__(self, attr):
		return self[attr]

	def __eq__(self, other):
		return self.subject == other.subject


class DiamondResultParaser:
	'''
	Diamond output result file parser
	@para diamond_output, diamond output tabular file with 12 columns
	'''
	def __init__(self, diamond_output):
		self.diamond_output = diamond_output
		if not os.path.isfile(self.diamond_output):
			raise Exception("** No diamond output file exists **")

		if not os.path.getsize(self.diamond_output):
			raise Exception("** No diamond output or no sequence align to database **")

	def __iter__(self):
		return self.parser()

	def parser(self):
		'''
		A generator for parse each record in diamond output tabular file
		@return a list contains all alignments for a query
		'''
		query = None
		rows = []
		with open(self.diamond_output) as fp:
			for line in fp:
				row = DiamondAlignmentRecord(line.strip().split())
				
				if row.query != query and rows:
					yield rows
					rows = []
					query = row.query
				
				if row not in rows:
					rows.append(row)

			yield rows


if __name__ == '__main__':
	task = Diamond('panda_blood_transcripts.fa', 'topaz.test.out', 'sp', threads=5)

	#for row in DiamondResultParaser('panda_diamond.out'):
	#	print row
	#	for k in row:
	#		print "%s\t%s" % (k, row[k])
	#	break