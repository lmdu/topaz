#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class sdict(dict):
	def __getattr__(self, attr):
		return self.get(attr, None)

	def __missing__(self, attr):
		return None

	def __setattr__(self, attr, value):
		self[attr] = value


class Term(sdict):
	'''
	GO term, contain properties of term in obo file.
	@prop ID, identifier GO:0052715
	@prop name, functional description
	@prop ontology, gene ontology 3 classify BP, CC or MF
	@prop parents, parent terms
	@prop level, shortest distance from root node
	@prop depth, longest distance from root node
	@prop obsolete, the is or not obsolete
	@prop alters, alternative identifiers
	'''
	def add_child(self, child):
		'''
		Add child to term children set
		@para child, GO term id e.g. GO:0052715
		'''
		if 'children' not in self:
			self.children = set()

		self.children.add(child)

	def add_parent(self, parent):
		'''
		Add parent to term parents set
		@para parent, GO term id e.g. GO:0052715
		'''
		if 'parents' not in self:
			self.parents = set()
		
		self.parents.add(parent)

	def add_alter_id(self, _id):
		'''
		Add alternative identifiers to go term
		@para _id, alternative identifier GO:0052715
		'''
		if 'alters' not in self:
			self.alters = set()

		self.alters.add(_id)


class GO(sdict):
	'''
	Gene ontology structure tree with go term node
	'''
	def __iter__(self):
		return self.itervalues()

	def _calc_layer(self):
		'''
		Calculate the number of layers in hierarchy for each GO term
		'''
		def _calc_level(term):
			'''
			Calculate the shortest distance from root in GO hierarchy
			@para term, a term class object
			@return int, term level
			'''
			if term.level is None:
				if not term.parents:
					term.level = 1
				else:
					term.level = min(_calc_level(self[parent]) for parent in term.parents) + 1

			return term.level

		def _calc_depth(term):
			'''
			Calulate the longest distance from root in GO hierarchy
			@para term, a term class object
			@return int, term depth
			'''
			if term.depth is None:
				if not term.parents:
					term.depth = 1
				else:
					term.depth = max(_calc_depth(self[parent]) for parent in term.parents) + 1

			return term.depth

		for term in self:
			_calc_level(term)
			_calc_depth(term)


	def _calc_children(self):
		'''
		Add child to parent children set for each GO term
		'''
		for term in self:
			if term.parents is None:
				continue

			for parent in term.parents:
				self[parent].add_child(term.ID)

	def complete(self):
		'''
		Execute calculating level and depth of term
		put the child to term children set
		'''
		self._calc_children()
		self._calc_layer()


def obo_parser(obo_handler):
	'''
	A generator for extracting each go terms with property
	information from obo file.
	@para obo_handler, open obo file handler
	'''
	namespaces = {'cellular_component': 'CC', 'biological_process': 'BP', 'molecular_function': 'MF'}
	
	term = None

	for line in obo_handler:
		#[Typedef] means last term
		if line.strip().lower() == '[typedef]':
			yield term
			break

		#When [Term] line, check previous term is or not exists
		if line.strip().lower() == '[term]':
			if term:
				yield term
			
			#new term started, create a term object
			term = Term()
			continue

		#parse the term information with field and value and we need
		#id, name, namespace, parents, obsolete and alternative identifier
		if ': ' in line:
			field, value = line.strip().split(': ')[0:2]
			if field == 'id':
				term.ID = value

			elif field == 'name':
				term.name = value

			#replace namespace to abbreviation MF, BP, CC
			elif field == 'namespace':
				term.ontology = namespaces[value]

			#A is_a B meas B is one of parents of A
			elif field == 'is_a':
				term.add_parent(value.split()[0])

			#check the term is obsolete or not
			elif field == 'is_obsolete':
				if value == 'true':
					term.obsolete = True

			#alternative identifiers of term
			elif field == 'alt_id':
				term.add_alter_id(value)

			else:
				pass

def get_go_terms(obo_file="go-basic.obo"):
	'''
	parse the GO obo file and extracted all the GO terms
	@para obo_file, GO obo file path
	@return dict, contains all GO terms
	'''
	if not os.path.isfile(obo_file):
		raise Exception(
			"** Please provide go-basic.obo file **\n"
			"go-basic.obo file can be downloaded from gene ontology website.\n"
			"http://geneontology.org/page/download-ontology"
		)

	terms = GO()
	with open(obo_file) as obo:
		for term in obo_parser(obo):
			terms[term.ID] = term

	terms.complete()
	return terms

if __name__ == '__main__':
	terms = get_go_terms()
	print sum(1 for term in terms if term.level==3 and not term.obsolete)
		
