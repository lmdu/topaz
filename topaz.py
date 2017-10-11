#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse

def annotate(args):
	print args

def make_blast_db(args):
	print args

def make_diamond_db(args):
	pass

def command_arguments():
	'''
	command line arguments
	'''
	parser = argparse.ArgumentParser(
		prog = 'topaz',
		description='Topaz aligns transcripts to protein database and performs GO and KEGG annotation'
	)
	parser.add_argument('-v', '--version',
		action='version',
		version='%(prog)s v0.1.0'
	)

	subparsers = parser.add_subparsers(help="sub-command help")

	annotate_parser = subparsers.add_parser('annotate',
		help = "Align query sequence to database"
	)
	annotate_parser.set_defaults(func=annotate)
	annotate_parser.add_argument('-a', '--aligner',
		help = 'alignment tool for alignming sequence to database (default: diamond)',
		choices = ['diamond', 'blast', 'rapsearch'],
		default = 'diamond',
		metavar = 'aligner'
	)
	annotate_parser.add_argument('-d', '--db', 
		help = 'database name (nr, nt, swissprot etc.)',
		required = True,
		metavar = 'database path'
	)
	annotate_parser.add_argument('-q', '--query',
		help = 'input query fasta file',
		required = True,
		metavar = 'fasta'
	)
	annotate_parser.add_argument('-t', '--type', 
		help='query sequence type, dna or protein (default: dna)',
		choices = ['dna', 'protein'],
		default = 'dna',
		metavar = 'type'
	)
	annotate_parser.add_argument('-o', '--outdir',
		help = 'output directory',
		required = True,
		metavar = 'outdir'
	)
	annotate_parser.add_argument('-e', '--evalue',
		help='maximum expected value like blast (default: 1e-5)',
		type = float,
		default = 1e-5,
		metavar = 'evalue'
	)
	annotate_parser.add_argument('-p', '--threads',
		help = 'number of CPU threads (default: 1)',
		type = int,
		default = 1,
		metavar = 'threads'
	)
	annotate_parser.add_argument('-s', '--sensitive',
		action = 'store_true',
		help = 'use sensitive mode for diamond'
	)

	#make blast database
	makedb_parser = subparsers.add_parser('makedb',
		help = "Make protein alignment database"
	)
	makedb_parser.set_defaults(func=make_blast_db)
	makedb_parser.add_argument('-a', '--aligner',
		help = 'alignment tool to be used',
		metavar = 'aligner'
	)
	makedb_parser.add_argument('-i', '--in',
		help = 'Input protein fasta file',
		metavar = 'fasta'
	)
	makedb_parser.add_argument('-o', '--out',
		help = 'Name of database to be created',
		metavar = 'dbname'
	)

	#make diamond database
	makego_parser = subparsers.add_parser('makego',
		help = "Make GO annotation database"
	)
	makego_parser.set_defaults(func=make_diamond_db)
	makego_parser.add_argument('-i', '--in',
		help = 'Input protein fasta file',
		metavar = 'fasta'
	)
	makego_parser.add_argument('-o', '--out',
		help = 'Name of Diamond database to be created',
		metavar = 'dbname'
	)

	return parser.parse_args()

if __name__ == '__main__':
	#align_to_database()
	options = command_arguments()
	options.func(options)
	
	