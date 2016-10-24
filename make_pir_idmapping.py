#!/usr/bin/env python
import sys
import gzip
import sqlite3

conn = sqlite3.connect('idmapping.db')
cur = conn.cursor()

def e(acc):
	cur.execute("SELECT 1 FROM acc2uniprot WHERE acc=?", (acc,))
	return cur.fetchone()

same = 0
diff = 0
error = 0
step = 0

fp = gzip.open(sys.argv[1])
for line in fp:
	step += 1
	cols = line.strip().split("\t")
	if len(cols) != 22:
		error += 1
		continue

	for idx in [2, 3, 5, 6, 8, 9, 13, 16, 17, 18, 20, 21]:
		if e(cols[idx]):
			same += 1
		else:
			diff += 1
			cur.execute("INSERT INTO acc2uniprot VALUES (?,?)", (cols[idx], cols[0]))

	if step % 1000 == 0:
		print "Same: %s\tDiff: %s\tError: %s" % (same, diff, error)

fp.close()

cur.execute("REINDEX acc2uniprot")

print "Error Line: %s" % error
print "Same accession: %s" % same
print "Diff accession: %s" % diff
cur.close()
conn.commit()
conn.close()
