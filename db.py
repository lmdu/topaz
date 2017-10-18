#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import attr
import sqlite3

@attr.s
class GODatabase(object):
	'''
	Gene ontology association annotation database
	@dbfile, database file path
	'''
	dbfile = attr.ib()
	conn = attr.ib(init=False)
	cursor = attr.ib(init=False)

	@dbfile.validator
	def check_db_file(self):
		if not os.path.isfile(self.dbfile):
			raise Exception('Datbase file %s is not exists' % self.dbfile)

	@conn.default
	def connect_to_db(self):
		return sqlite3.connect(self.dbfile)

	@cursor.default
	def get_cursor(self):
		return self.conn.cursor()

	def __del__(self):
		self.cursor.close()
		self.conn.close()

	def submit(self):
		self.conn.commit()

	def iter(self, sql, args=None):
		for row in self.cursor.execute(sql, args):
			yield row

	def get(self, sql, args=None):
		for row in self.cursor.execute(sql, args):
			return row[0]

	def gets(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()


class SQLiteConnection:
	'''
	Check the database file and use apsw to connect and optimize
	@para dbfile, database file path
	'''
	def __init__(self, dbfile):
		#check the database file is exists or not
		
		
		#connect to database file
		self.conn = apsw.Connection(dbfile)
		
		#optimize the sqlite3 database and speed up select and insert
		self.optimizeDatabase()

		#default open the trasaction mode
		self.beginTrasaction()

	def __enter__(self):
		self.cursor = self.conn.cursor()
		return self.cursor

	def __exit__(self, *exc):
		self.cursor.close()

	def __del__(self):
		self.conn.close()

	def optimizeDatabase(self):
		'''
		use pragma command to optimize the sqlite3 database
		'''
		sql = (
			"PRAGMA cache_size=8000;"
			"PRAGMA PAGE_SIZE=4096;"
			"PRAGMA journal_mode=OFF;"
			"PRAGMA synchronous=OFF;"
			"PRAGMA count_changes=OFF;"
			"PRAGMA temp_store=MEMORY;"
		)
		self.execute(sql)

	def beginTrasaction(self):
		self.execute("BEGIN TRANSACTION;")

	def execute(self, sql, *args):
		'''
		execute a sql statement
		@para sql str, sql statement
		@para args tuple, arguments
		'''
		with self as db:
			db.execute(sql, args)
	
	def query(self, sql, *args):
		'''
		a generator for sql query results
		@para sql str, sql statement
		@para args tuple, arguments
		@return list, a row
		'''
		with self as db:
			for row in db.execute(sql, args):
				yield row

	def get(self, sql, *args):
		'''
		get value by executing sql statement
		@para sql str, sql statement
		@para args tuple, arguments
		@return the first column of a row
		'''
		with self as db:
			db.execute(sql, args)
			row = db.fechone()
		return row[0] if row else row
