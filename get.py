#!/usr/bin/env python
import sys
import sqlite3

conn = sqlite3.connect('go.db')
cur = conn.cursor()

with open(sys.argv[1]) as fh:
	fh.readline()
	for line in fh:
		acc = line.strip().split()[2].split('|')[3].split('.')[0]
		cur.execute("SELECT * FROM dbxref WHERE xref_key=? LIMIT 1", (acc,))
		row = cur.fetchone()
		if row:
			print "%s\t%s" % (row[0], row[1])