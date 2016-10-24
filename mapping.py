#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import apsw
#import config

class DBConnection:
	'''
	Check the database file and use apsw to connect and optimize
	@para dbfile, database file path
	'''
	def __init__(self, dbfile):
		self.dbfile = dbfile
		
		#check the database file is exists or not
		if not os.path.isfile(self.dbfile):
			raise Exception('Datbase file %s is not exists' % self.dbfile)

		#connect to database file
		self.conn = apsw.Connection(self.dbfile)

		#optimize the sqlite3 database
		cursor = self.cursor()
		cursor.execute("PRAGMA cache_size=8000;")
		cursor.execute("PRAGMA PAGE_SIZE=4096;")
		cursor.execute("PRAGMA journal_mode=OFF;")
		cursor.execute("PRAGMA synchronous=OFF;")
		cursor.execute("PRAGMA count_changes=OFF;")
		cursor.execute("PRAGMA temp_store=MEMORY;")
		cursor.close()

	def __del__(self):
		self.conn.close()

	def cursor(self):
		'''
		create a new cursor for execute sql statements
		@return sqlite3 cursor
		'''
		return self.conn.cursor()


class SQLiteDB:
	'''
	Control the sqlie3 database including update, insert, select
	'''
	#connect to database file
	#conn = DBConnection(config.dbfile)
	conn = DBConnection('go-201610.db')

	def cursor(self):
		'''
		create a connection cursor
		'''
		return self.conn.cursor()

	def execute(self, sql, *args):
		'''
		execute a sql statement with or without arguments
		@para sql str, a sql statement
		@para rgs tuple, arguments
		'''
		cursor = self.cursor()
		try:
			cursor.execute(sql, args)
		finally:
			cursor.close()

	def query(self, sql, *args):
		'''
		execute a sql statement with or without arguments and
		return the fetched all rows
		@para str, a sql statement
		@para args tuple, arguments
		@return list, all rows fetched
		'''
		cursor = self.cursor()
		try:
			cursor.execute(sql, args)
			rows = cursor.fetchall()
		finally:
			cursor.close()

		return rows

	def get(self, sql, *args):
		'''
		execute a sql statement with or without arguments and
		return the fetched all rows
		@para sql str, a sql statement
		@para args tuple, arguments
		@return a column in feched row 
		'''
		cursor = self.cursor()
		try:
			cursor.execute(sql, args)
			row = cursor.fetchone()
		finally:
			cursor.close()

		return row[0] if row else None


class Mapping(SQLiteDB):
	'''
	Get go terms and annotation evidence for a gene by using dbxref key in
	go association database, or using NCBI, Ensembl etc. accession number
	'''
	def getGoByXrefKey(self, xref_key):
		'''
		Get go terms by using dbxref key in go association database
		@para xref_key str, maybe uniprot accession
		@return list, contains many rows
		'''
		sql = (
			"SELECT DISTINCT a.term_id, e.code FROM association AS a"
			" INNER JOIN evidence AS e ON (e.association_id=a.id)"
			" INNER JOIN gene_product AS g ON (g.id=a.gene_product_id)"
			" INNER JOIN dbxref AS d ON (d.id=g.dbxref_id)"
			" WHERE d.xref_key=?"
		)

		return self.query(sql, xref_key)

	def getGoByAccession(self, acc):
		'''
		Get go terms by using NCBI or other database accession number
		@para acc str, accession number maybe from NCBI
		@return list, contains many rows
		'''
		sql = (
			"SELECT DISTINCT a.term_id, e.code FROM association AS a"
			" INNER JOIN evidence AS e ON (e.association_id=a.id)"
			" INNER JOIN gene_product AS g ON (g.id=a.gene_product_id)"
			" INNER JOIN dbxref AS d ON (d.id=g.dbxref_id)"
			" INNER JOIN acc2uniprot AS u ON (u.uniprot=d.xref_key)"
			" WHERE u.acc=?"
		)

		return self.query(sql, acc)

	def convertAccessionToUniprot(self, acc):
		'''
		Convert the accession from NCBI NR etc. to uniprot accession
		@para acc str, NCBI NR etc. accession
		@return str if accession is exists in database or None
		'''
		sql = "SELECT uniprot FROM acc2uniprot WHERE acc=? LIMIT 1"
		return self.get(sql, acc)


	def getGoTerms(self, acc):
		'''
		Get go terms by any accession number
		@para acc str, NCBI, Ensembl or Uniprot etc. accession number
		@return list, contains many rows
		'''
		#first, directly search accession in dbxref database 
		terms = self.getGoByXrefKey(acc)
		if terms:
			return terms

		#second, if accession not in dbxref, convert accession to uniprot
		uniprot = self.convertAccessionToUniprot(acc)
		if uniprot is None:
			return []

		#use the uniprot accession to search dbxref database
		return self.getGoByXrefKey(uniprot)


if __name__ == '__main__':
	DB = Mapping()
	with open(sys.argv[1]) as fh:
		fh.readline()
		for line in fh:
			cols = line.strip().split('\t')
			gene = cols[0]
			acc = cols[2].split()[0].split('|')[-2]
			terms = DB.getGoTerms(acc)
			for term in terms:
				print "%s\t%s\t%s\t%s" % (gene, acc, term[0], term[1])