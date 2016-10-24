#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import apsw
import config

class DBConnection:
	'''
	Check the database file and use apsw to connect and optimize
	@para dbfile, database file path
	'''
	def __init__(self, dbfile):
		if not os.path.isfile(dbfile):
			raise Exception('Datbase file %s is not exists' % dbfile)

		self.conn = apsw.Connection(dbfile)
		self.cursor = self.conn.cursor()
		self.cursor.execute("PRAGMA cache_size=8000")
		self.cursor.execute("PRAGMA PAGE_SIZE=4096")
		self.cursor.execute("PRAGMA journal_mode=OFF")
		self.cursor.execute("PRAGMA synchronous=OFF")
		self.cursor.execute("PRAGMA count_changes=OFF")
		self.cursor.execute("PRAGMA temp_store=MEMORY")
		self.cursor.close()

	def __del__(self):
		self.conn.close()

	def cursor(self):
		return self.conn.cursor()


class SQLiteDB:
	'''
	Control the sqlie3 database including update, insert, select
	'''
	conn = DBConnection(config.dbfile)

	def cursor(self):
		'''
		create a connection cursor
		'''
		return self.conn.cursor()

	def execute(self, sql, *args):
		cursor = self.cursor()
		try:
			cursor.execute(sql, args)
		finally:
			cursor.close()

	def query(self, sql, *args):
		cursor = self.cursor()
		try:
			for row in cursor.execute(sql, args):
				yield row
		finally:
			cursor.close()

	def get(self, sql, *args):
		cursor = self.cursor()
		try:
			cursor.execute(sql, args)
			row = cursor.fetchone()
		finally:
			cursor.close()

		return row


class Mapping(SQLiteDB):
	def __init__(self):
		super(Mapping, self).__init__()

	def getGoByXrefKey(self, xref_key):
		sql = (
			"SELECT DISTINCT a.term_id, e.code FROM association AS a"
			" INNER JOIN gene_product AS g ON (a.gene_product_id=g.id)"
			" INNER JOIN dbxref AS d ON (g.dbxref_id = d.id)"
			" INNER JOIN evidence AS e ON (e.association_id = a.id AND e.dbxref_id=d.id)"
			" WHERE d.xref_key=?"
		)
		return list(self.query(sql, xref_key))


	def getGoByAccession(self, accession):
		sql = (
			"SELECT DISTINCT a.term_id, e.code FROM association AS a"
			" INNER JOIN gene_product AS g ON (a.gene_product_id=g.id)"
			" INNER JOIN dbxref AS d ON (g.dbxref_id = d.id)"
			" INNER JOIN evidence AS e ON (e.association_id = a.id AND e.dbxref_id=d.id)"
			" INNER JOIN acc2uniprot AS u ON (u.uniprot = d.xref_key)"
			" WHERE u.acc=?"
		)
		return list(self.query(sql, accession))

