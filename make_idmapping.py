#!/usr/bin/env python
import sys
import gzip
import sqlite3

conn = sqlite3.connect('idmapping.db')
cur = conn.cursor()

sql = "CREATE TABLE acc2uniprot (acc TEXT, uniprot TEXT)"
cur.execute(sql)

types = set(['GI', 'NCBI_TaxID', 'GeneID', 'UniRef100', 'UniRef90', 'UniRef50', 'Gene_ORFName', 'UniProtKB-ID'])

print "Process uniprot idmapping"
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

def e(acc):
	cur.execute("SELECT 1 FROM acc2uniprot WHERE acc=?", (acc,))
	return cur.fetchone()

same = 0
diff = 0
error = 0

print "Process PIR idmapping"
fp = gzip.open(sys.argv[2])
for line in fp:
	cols = line.strip().split("\t")
	if len(cols) != 22:
		error += 1
		continue

	for idx in [2, 3, 5, 6, 8, 9, 13, 16, 17, 18, 20, 21]:
		if e(cols[idx]):
			same += 1
		else:
			diff += 1
			cur.execute(sql, (cols[idx], cols[0]))
fp.close()

cur.execute("REINDEX acc2uniprot")

print "Error Line: %s" % error
print "Same accession: %s" % same
print "Diff accession: %s" % diff
cur.close()
conn.commit()
conn.close()
