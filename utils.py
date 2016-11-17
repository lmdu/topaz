#!/usr/bin/env python
# -*- coding: utf-8 -*-
#GO annotation evidence code and the custom ID
evidence_codes = [
	#(code, ID, rank)
	#Experimental Evidence codes
	('EXP', 1, 5),		#Inferred from Experiment
	('IDA', 2, 5),		#Inferred from Direct Assay
	('IPI', 3, 5),		#Inferred from Physical Interaction 
	('IMP', 4, 5),		#Inferred from Mutant Phenotype
	('IGI', 5, 5),		#Inferred from Genetic Interaction
	('IEP', 6, 3),		#Inferred from Expression Pattern

	#Computational Analysis evidence codes
	('ISS', 7, 3),		#Inferred from Sequence or structural Similarity
	('ISO', 8, 3),		#Inferred from Sequence Orthology
	('ISA', 9, 3),		#Inferred from Sequence Alignment
	('ISM', 10, 3),		#Inferred from Sequence Model
	('IGC', 11, 2),		#Inferred from Genomic Context
	('IBA', 12, 3),		#Inferred from Biological aspect of Ancestor
	('IBD', 13, 3),		#Inferred from Biological aspect of Descendant
	('IKR', 14, 3),		#Inferred from Key Residues
	('IRD', 15, 3),		#Inferred from Rapid Divergenc
	('RCA', 16, 4),		#Inferred from Reviewed Computational Analysis

	#Author Statement evidence codes
	('TAS', 17, 4),		#Traceable Author Statement
	('NAS', 18, 3),		#Non-traceable Author Statement

	#Curatorial Statement codes
	('IC', 19, 4),		#Inferred by Curator
	('ND', 20, 1),		#No biological Data available

	#Automatically-Assigned evidence code
	('IEA', 21, 1),		#Inferred from Electronic Annotation

	#Obsolete Evidence Codes
	('NR', 22, 0)		#Not Recorded
]

class EvidenceCode(dict):
	def __init__(self):


	def __getattr__(self, attr):
		return self[attr]
