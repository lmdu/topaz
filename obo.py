#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import attr

@attr.s
class Term(object):
	'''
	GO term, contain properties of term in obo file.
	@para ID, identifier GO:0052715
	@para name, functional description
	@para namespace, gene ontology 3 classify BP, CC or MF
	@para obsolete, the is or not obsolete
	'''
	ID = attr.ib(init=False)
	name = attr.ib(init=False)
	namespace = attr.ib(init=False)
	obsolete = attr.ib(default=False, init=False)
	alters = attr.ib(default=attr.Factory(set), init=False)
	parents = attr.ib(default=attr.Factory(set), init=False)
	
	#level, shortest distance from root node
	level = attr.ib(default=None, init=False)
	
	#prop depth, longest distance from root node
	depth = attr.ib(default=None, init=False)

@attr.s
class DAG(object):
	terms = attr.ib(default=attr.Factory(dict), init=False)

	def add_term(self, term):
		self.terms[term.ID] = term

	def get_term(self, term_id):
		return self.terms[term_id]

	def __iter__(self):
		for term_id in self.terms:
			yield self.get_term(term_id)

	def __len__(self):
		return len(self.terms)

	def __contains__(self, item):
		return item in self.terms

	def calc_term_level(self, term_id):
		'''
		Calculate the shortest distance from root in GO hierarchy
		@para term_id, a term id
		@return int, term level
		'''
		term = self.get_term(term_id)
		if term.level is None:
			if not term.parents:
				term.level = 1
			else:
				term.level = min(self.calc_term_level(parent) for parent in term.parents) + 1

		return term.level

	def calc_term_depth(self, term_id):
		'''
		Calulate the longest distance from root in GO hierarchy
		@para term_id, a term id
		@return int, term depth
		'''

		term = self.get_term(term_id)

		if term.depth is None:
			if not term.parents:
				term.depth = 1
			else:
				term.depth = max(self.calc_term_depth(parent) for parent in term.parents) + 1

		return term.depth

	def calc_layers(self):
		for term_id in self.terms:
			self.calc_term_depth(term_id)
			self.calc_term_level(term_id)


@attr.s
class OBOParser(object):
	obo_file = attr.ib()
	obo_fh = attr.ib(init=False)
	
	@obo_file.validator
	def check_obo_file(self, attr, value):
		if not os.path.isfile(value):
			raise Exception(
				"** Please provide go-basic.obo file **\n"
				"go-basic.obo file can be downloaded from gene ontology website.\n"
				"http://geneontology.org/page/download-ontology"
			)

	@obo_fh.default
	def open_obo_file(self):
		'''
		open obo file and read to [Term]
		'''
		fh = open(self.obo_file)
		for line in fh:
			if line.startswith('[Term]'):
				break
		return fh

	def __del__(self):
		if self.obo_fh:
			self.obo_fh.close()

	def __iter__(self):
		return self

	def get_category(self, namespace):
		categories = {
			'cellular_component': 'CC',
			'biological_process': 'BP',
			'molecular_function': 'MF',
			'external': None
		}

		return categories[namespace]

	def next(self):
		term = Term()
		for line in self.obo_fh:

			line = line.strip()
			#[Typedef] means last term
			if line == '[Typedef]':
				self.obo_fh.seek(0, 2)
				return term

			#When [Term] line, check previous term is or not exists
			if line == '[Term]':
				return term

			#parse the term information with field and value and we need
			#id, name, namespace, parents, obsolete and alternative identifier
			if line[0:3] == 'id:':
				term.ID = line[4:]

			elif line[0:5] == 'name:':
				term.name = line[6:]

			elif line[0:10] == 'namespace:':
				term.namespace = self.get_category(line[11:])

			elif line[0:5] == 'is_a:':
				term.parents.add(line[6:16])

			elif line[0:12] == 'is_obsolete:':
				term.obsolete = True

			elif line[0:7] == 'alt_id:':
				term.alters.add(line[8:])

		raise StopIteration


if __name__ == '__main__':
	obofile = r'D:\research\topaz\go-basic.obo'
	dag = DAG()
	for term in OBOParser(obofile):
		dag.add_term(term)
	
	dag.calc_layers()

	for term in dag:
		if term.level == 2 and not term.obsolete:
			print "%s\t%s" % (term.ID, term.name)
