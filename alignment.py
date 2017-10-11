#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sh
import time

from toolkit import *


class Aligner:
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
	def __init__(self, query, outfile, db='nr', threads=1, evalue=1e-5, sensitive=False,
				seqtype='dna'):
		pass

class Diamond(Aligner):
	def __init__(self):
		pass

class Blast(Aligner):
	def __init__(self):
		pass





def diamond(query, out, db='nr', threads=1, evalue=1e-5, cover=None, 
		sensitive=False, seqtype='dna', targets=20, outfmt=6):
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