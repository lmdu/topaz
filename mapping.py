#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from db import SQLiteConnection

class GOTermAssignment:
	'''
	Get go terms and annotation evidence for a gene by using dbxref key in
	go association database, or using NCBI, Ensembl etc. accession number
	'''
	_db = None
	_terms = None
	
	@property
	def db(self):
		'''
		check sqlite is connected or not and if not connect
		'''
		if self._db is None:
			self._db = SQLiteConnection(config.GO_DB)
		return self._db

	def term(self, _id):
		if self._terms is None:
			self._terms = {_id: acc for _id, acc in self.db.query("SELECT * FROM term")}
		return self._terms[_id]

	def getGoByXrefKey(self, xref_key):
		'''
		Get go terms by using dbxref key in go association database
		@para xref_key str, maybe uniprot accession
		@return list, contains many rows
		'''
		sql = (
			"SELECT DISTINCT a.term_id, a.evidence FROM association AS a"
			" INNER JOIN gene_product AS g ON (g.id=a.gene_product_id)"
			" INNER JOIN dbxref AS d ON (d.id=g.dbxref_id)"
			" WHERE d.xref_key=?"
		)

		return [(self.term(i), e) for i, e in self.db.query(sql, xref_key)]

	def convertAccessionToUniprot(self, acc):
		'''
		Convert the accession from NCBI NR etc. to uniprot accession
		@para acc str, NCBI NR etc. accession
		@return str if accession is exists in database or None
		'''
		sql = "SELECT uniprot FROM acc2uniprot WHERE acc=? LIMIT 1"
		return self.db.get(sql, acc)


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
	mapper = GOTermAssignment()
	print mapper.getGoTerms('XP_011216275.1')