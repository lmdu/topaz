#!/usr/bin/env python
import sys
import gzip
import sqlite3

conn = sqlite3.connect('idmapping.db')
cur = conn.cursor()

sql = "CREATE TABLE acc2uniprot (acc TEXT, uniprot TEXT)"
cur.execute(sql)

types = set(['GI', 'NCBI_TaxID', 'GeneID', 'UniRef100', 'UniRef90', 'UniRef50', 'Gene_ORFName', 'UniProtKB-ID'])

sql = "INSERT INTO acc2uniprot VALUES (?,?)"
fp = gzip.open(sys.argv[1])
for line in fp:
	cols = line.strip().split()
	if cols[1] in types:
		continue
	cur.execute(sql, (cols[2], cols[0]))
fp.close()

cur.execute("CREATE INDEX u1 ON acc2uniprot(acc)")
cur.execute("CREATE INDEX u2 ON acc2uniprot(uniprot)")
cur.execute("CREATE INDEX u3 ON acc2uniprot(acc, uniprot)")

cur.close()
conn.commit()
conn.close()
