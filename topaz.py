#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse

def command_arguments():
	'''
	command line arguments
	'''
	parser = argparse.ArgumentParser(
		prog = 'topaz',
		description='Topaz aligns transcripts to protein database and performs GO and KEGG annotation'
	)
	parser.add_argument('-d', '--db', 
		help='protein database name',
		required=True,
		metavar='database'
	)
	parser.add_argument('-q', '--query',
		help='input query transcripts fasta file',
		required=True,
		metavar='fasta'
	)
	parser.add_argument('-t', '--type', 
		help='query sequence type, dna or protein (default: dna)',
		choices = ['dna', 'protein'],
		default = 'dna',
		metavar = 'type'
	)
	parser.add_argument('-o', '--outdir',
		help='output directory',
		required=True,
		metavar='outdir'
	)
	parser.add_argument('-e', '--evalue',
		help='maximum expected value like blast (default: 1e-5)',
		type=float,
		default=1e-5,
		metavar='evalue'
	)
	parser.add_argument('-i', '--rank',
		help='rank cutoff for valid hits from alignment result (default: 5)',
		type=int,
		default=5,
		metavar='rank'
	)
	parser.add_argument('-p', '--threads',
		help='number of CPU threads (default: 1)',
		type=int,
		default=1,
		metavar='threads'
	)
	parser.add_argument('-s', '--sensitive',
		action='store_true',
		help='use sensitive mode'
	)
	parser.add_argument('-c', '--coverage',
		help='minimal percent of the query sequence that overlaps the subject sequence',
		type=int,
		metavar='coverage'
	)
	parser.add_argument('-v', '--version',
		action='version',
		version='%(prog)s v0.1.0'
	)

	return parser.parse_args()

if __name__ == '__main__':
	#align_to_database()
	options = command_arguments()
	
	