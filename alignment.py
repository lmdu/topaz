#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sh
import time

#Diamond aligner
diamond = sh.Command('diamond').bake(_long_sep=' ')

#blast aligner
blastx = sh.Command('blastx').bake(_long_prefix='-', _long_sep=' ') 
blastp = sh.Command('blastp').bake(_long_prefix='-', _long_sep=' ')


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


class AlignmentRecord(dict):
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


class BlastTabularParaser:
	'''
	Blast tabular output format parser, blast -outfmt 6
	@para tabular, diamond or blast output tabular file with 12 columns
	'''
	def __init__(self, tabular):
		self.tabular = tabular
		if not os.path.isfile(self.tabular):
			raise Exception("** No diamond output file exists **")

		if not os.path.getsize(self.tabular):
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
		with open(self.tabular) as fp:
			for line in fp:
				row = AlignmentRecord(line.strip().split())
				
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