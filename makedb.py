#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import csv
import gzip
import time
import textwrap
import argparse

import apsw

#command line arguments
parser = argparse.ArgumentParser(
	prog = 'topazdb',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description =textwrap.dedent('''\
		Create topaz gene ontology (GO) association database, require 3 files: 
		1) go_monthly-assocdb-data.gz http://archive.geneontology.org/latest-full/
		2) idmapping.tb.gz ftp://ftp.pir.georgetown.edu/databases/idmapping/
		3) idmapping.dat.gz ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/'''
	)
)
parser.add_argument('-g',
	help = 'GO asociation annotation file',
	required = True,
	metavar = 'go_monthly-assocdb-data.gz'
)
parser.add_argument('-u',
	help = 'uniprot idmapping file',
	required = True,
	metavar = 'idmapping.dat.gz'
)
parser.add_argument('-p',
	help = 'PIR idmapping file',
	required = True,
	metavar = 'idmapping.tb.gz'
)
parser.add_argument('-o',
	help = 'Output database file name (default: go-xx.db)',
	default = 'go-%s.db' % time.strftime("%Y%m", time.localtime()),
	metavar = 'go.db'
)

options = parser.parse_args()

#check the input file
if not os.path.isfile(options.g):
	raise Exception("** GO annotation file %s is not exists **" % options.g)

if not os.path.isfile(options.u):
	raise Exception("** uniprot idmapping file %s is not exists **" % options.u)

if not os.path.isfile(options.p):
	raise Exception("** PIR idmapping file %s is not exists **" % options.p)

if os.path.exists(options.o):
	raise Exception("** %s database file is exists **" % options.o)


#connect to sqlite3 database
conn = apsw.Connection(options.o)
cur = conn.cursor()

#optimize sqlite3 database speed
#cur.execute("PRAGMA cache_size=8000")
#cur.execute("PRAGMA PAGE_SIZE=4096")
#cur.execute("PRAGMA journal_mode=OFF")
cur.execute("PRAGMA synchronous=OFF")
#cur.execute("PRAGMA count_changes=OFF")
#cur.execute("PRAGMA temp_store=MEMORY")

#open transaction mode
cur.execute("BEGIN;")

#create tables
sql = '''
CREATE TABLE term (
	id INTEGER PRIMARY KEY,
	acc TEXT
);
CREATE TABLE association (
	id INTEGER PRIMARY KEY, 
	term_id INTEGER,
	gene_product_id INTEGER,
	evidence TEXT
);
CREATE TABLE gene_product (
	id INTEGER PRIMARY KEY,
	dbxref_id INTEGER
);
CREATE TABLE dbxref (
	id INTEGER PRIMARY KEY,
	xref_key TEXT COLLATE NOCASE
);
CREATE TABLE acc2uniprot (
	acc TEXT COLLATE NOCASE,
	uniprot TEXT
);
'''
#CREATE TABLE gene_product (
#	id INTEGER PRIMARY KEY,
#	symbol TEXT COLLATE NOCASE,
#	dbxref_id INTEGER,
#	species_id INTEGER,
#	synonym TEXT COLLATE NOCASE
#);
#CREATE TABLE species (
#	id INTEGER PRIMARY KEY,
#	taxonomy INTEGER,
#	genus TEXT COLLATE NOCASE,
#	species TEXT COLLATE NOCASE
#);
cur.execute(sql)


def parse_values(vals):
	'''
	parse the values in sql statement use csv module
	@para vals, a string with multiple group values
	@return list, contains many database rows
	'''
	reader = csv.reader([vals],
		delimiter=',',
		doublequote=False,
		escapechar='\\',
		quotechar="'",
		strict=True
	)

	rows = [] #store all rows
	row = [] #store current row values

	for header_row in reader:
		for column in header_row:
			#NULL column
			if len(column) == 0:
				row.append(column)
				continue
			
			#start of the new row
			if column[0] == '(':
				if len(row) == 0:
					row = [column[1:]]
			
				elif len(row) > 0:
					#check the end of a row
					if row[-1][-1] == ')' and '(' not in row[-1]:
						row[-1] = row[-1][:-1]
						rows.append(row)
						#start a new row
						row = [column[1:]]
			else:
				row.append(column)
		else:
			if row[-1][-2:] == ');':
				row[-1] = row[-1][:-2]
				rows.append(row)

	return rows

#GO annotation evidence code and the custom ID
evidence_codes = dict(
	#Experimental Evidence codes
	EXP = 1,	#Inferred from Experiment
	IDA = 2,	#Inferred from Direct Assay
	IPI = 3,	#Inferred from Physical Interaction 
	IMP = 4,	#Inferred from Mutant Phenotype
	IGI = 5,	#Inferred from Genetic Interaction
	IEP = 6,	#Inferred from Expression Pattern

	#Computational Analysis evidence codes
	
	ISS = 7,	#Inferred from Sequence or structural Similarity
	ISO = 8,	#Inferred from Sequence Orthology
	ISA = 9,	#Inferred from Sequence Alignment
	ISM = 10,	#Inferred from Sequence Model
	IGC = 11,	#Inferred from Genomic Context
	IBA = 12,	#Inferred from Biological aspect of Ancestor
	IBD = 13,	#Inferred from Biological aspect of Descendant
	IKR = 14,	#Inferred from Key Residues
	IRD = 15,	#Inferred from Rapid Divergenc
	RCA = 16,	#Inferred from Reviewed Computational Analysis

	#Author Statement evidence codes
	TAS = 17,	#Traceable Author Statement
	NAS = 18,	#Non-traceable Author Statement

	#Curatorial Statement codes
	IC = 19,	#Inferred by Curator
	ND = 20,	#No biological Data available

	#Automatically-Assigned evidence code
	IEA = 21,	#Inferred from Electronic Annotation

	#Obsolete Evidence Codes
	NR=22	#Not Recorded
)


#Parse GO association file to sqlite database
fp = gzip.open(options.g, 'rb')
for line in fp:
	if not line.startswith("INSERT INTO"): continue
	table = line.split('` VALUES ')[0].split()[-1].strip('`')
	vals = line.partition('` VALUES ')[2]
	vals = parse_values(vals)
	
	if table == 'term':
		rows = [(int(val[0]), val[3].strip("'")) for val in vals]
		cur.executemany("INSERT INTO term VALUES (?,?)", rows)
	
	if table == 'association':
		rows = [(int(val[0]), int(val[1]), int(val[2]), 0) for val in vals]
		cur.executemany("INSERT INTO association VALUES (?,?,?,?)", rows)

	elif table == 'dbxref':
		rows = [(int(val[0]), val[2].strip("'")) for val in vals]
		cur.executemany("INSERT INTO dbxref VALUES (?,?)", rows)

	elif table == 'gene_product':
		rows = [(int(val[0]), int(val[2])) for val in vals]
		cur.executemany("INSERT INTO gene_product VALUES (?,?)", rows)

	#elif table == 'species':
	#	rows = [(int(val[0]), int(val[1]), val[4].strip("'"), val[5].strip("'")) for val in vals]
	#	cur.executemany("INSERT INTO species VALUES (?,?,?,?)", rows)
		
	#elif table == 'gene_product_synonym':
	#	rows = [(val[1].strip("'"), int(val[0])) for val in vals]
	#	cur.executemany("UPDATE gene_product SET synonym=? WHERE id=?", rows)

	elif table == 'evidence':
		rows = [(evidence_codes[val[1].strip("'")], int(val[2])) for val in vals]
		cur.executemany("UPDATE association SET evidence=? WHERE id=?", rows)

	#else:
	#	pass

	#print "INSERT INTO %s %s rows" % (table, len(rows))

fp.close()

print "STEP 2"

#Parse uniprot idmapping file
ID_types = set(['GI', 'NCBI_TaxID', 'GeneID', 'UniRef100', 'UniRef90', 'UniRef50', 'Gene_ORFName', 'UniProtKB-ID'])
rows = []
fp = gzip.open(options.u, 'rb')
for line in fp:
	cols = line.strip().split()
	
	if cols[1] in ID_types:
		continue

	rows.append((cols[2], cols[0]))

	if len(rows) == 10000:
		cur.executemany("INSERT INTO acc2uniprot VALUES (?,?)", rows)
		rows = []
else:
	if rows:
		cur.executemany("INSERT INTO acc2uniprot VALUeS (?,?)", rows)
fp.close()


#Create go annotation database index
sql = '''
CREATE INDEX a1 ON association (gene_product_id);
CREATE INDEX a2 ON association (id, gene_product_id);

CREATE INDEX g1 ON gene_product (dbxref_id);
CREATE INDEX g2 ON gene_product (id, dbxref_id);

CREATE INDEX d1 ON dbxref (xref_key);
CREATE INDEX d2 ON dbxref (id, xref_key);

CREATE INDEX u1 ON acc2uniprot (acc);
'''
cur.execute(sql)


print "STEP 3"

#Check PIR idmapping file
def has_acc(acc):
	'''
	Check the accession is exists in database or not
	@para acc, accession from PIR idmapping.tb file
	@return bool
	'''
	cur.execute("SELECT 1 FROM acc2uniprot WHERE acc=?", (acc,))
	return cur.fetchone()

rows = []
fp = gzip.open(options.p, 'rb')
for line in fp:
	cols = line.strip().split("\t")
	
	if len(cols) != 22:
		continue

	for idx in [2, 3, 5, 6, 8, 9, 13, 16, 17, 18, 20, 21]:
		if not has_acc(cols[idx]):
			rows.append((cols[idx], cols[0]))

	if len(rows) >= 10000:
		cur.executemany("INSERT INTO acc2uniprot VALUES (?,?)", rows)
		rows = []
else:
	if rows:
		cur.executemany("INSERT INTO acc2uniprot VALUES (?,?)", rows)
fp.close()

cur.execute("REINDEX acc2uniprot")

#complete and submit
cur.execute("COMMIT;")
cur.close()
conn.close()
