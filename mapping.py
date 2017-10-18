#!/usr/bin/env python
# -*- coding: utf-8 -*-
import attr
import config
#from db import SQLiteConnection
from db import GODatabase

@attr.s
class GOTermMapper:
	'''
	Get go terms and annotation evidence for a gene by using dbxref key in
	go association database, or using NCBI, Ensembl etc. accession number
	'''
	db = attr.ib(init=False)
	terms = attr.ib(init=False)

	@db.default
	def connect_to_db(self):
		return GODatabase(config.GO_DB)

	@terms.default
	def get_go_terms_id(self):
		return {tid: acc for tid, acc in self.db.iter("SELECT * FROM term")}

	def get_go_terms_by_xrefkey(self, xref_key):
		'''
		Get go terms by using dbxref key in go association database
		@para xref_key, maybe uniprot or ncbi accession
		@return list, contains many rows
		'''
		sql = (
			"SELECT DISTINCT a.term_id, a.evidence FROM association AS a"
			" INNER JOIN gene_product AS g ON (g.id=a.gene_product_id)"
			" INNER JOIN dbxref AS d ON (d.id=g.dbxref_id)"
			" WHERE d.xref_key=?"
		)

		return [(self.terms[i], e) for i, e in self.db.iter(sql, xref_key)]

	def covert_acc_to_uniprot(self, acc):
		'''
		Convert the accession from NCBI NR etc. to uniprot accession
		@para acc str, NCBI NR etc. accession
		@return str if accession is exists in database or None
		'''
		sql = "SELECT uniprot FROM acc2uniprot WHERE acc=? LIMIT 1"
		return self.db.get(sql, acc)


	def get_go_terms_by_acc(self, acc):
		'''
		Get go terms by any accession number
		@para acc str, NCBI, Ensembl or Uniprot etc. accession number
		@return list, contains many rows
		'''
		#first, directly search accession in dbxref database 
		terms = self.get_go_terms_by_xrefkey(acc)
		if terms: return terms

		#second, if accession not in dbxref, convert accession to uniprot
		uniprot = self.covert_acc_to_uniprot(acc)
		if not uniprot: return []

		#use the uniprot accession to search dbxref database
		return self.get_go_terms_by_xrefkey(uniprot)


if __name__ == '__main__':
	mapper = GOTermAssignment()
	print mapper.getGoTerms('XP_011216275.1')