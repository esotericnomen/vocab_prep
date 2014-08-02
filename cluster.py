#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys					# for system io
import datetime
import sqlite3					# for DB Activities
import urllib2					# for url parssing et al
import textwrap					# To limit o/p characters per line
import subprocess				# To invoke espeak
import time
import os
from nltk.corpus import wordnet as wn		# Wordnet DB
from nltk.stem.wordnet import WordNetLemmatizer	# To Obtain Lemma
from BeautifulSoup import BeautifulSoup
import goslate
import re
from pattern.en import conjugate, pluralize, singularize, comparative, superlative, suggest

rpath = "/home/shingu/workspace/vocab_prep/"
#rpath = "/home/rajkumar.r/backup/workspace/users/raj/vocab_prep/"
#tdef_file = open("/home/shingu/rtrt","w")


def similar_Wrd(word):
	list_of_sim=[]
	#print "Running similar_Wrd for %s" %(word)
	for wrd in wn.synsets(word):
		#print "%s in lemma_names" %(wrd)
		for sim in wrd.lemma_names:
			if sim not in list_of_sim:
				#print "%s not in list_of_sim" %(sim)
				if sim in sword_list and sim not in completed_list:
					#print "%s is in sword_list" %(sim)
					list_of_sim.append(sim)
				else:
					pass
					#print "%s is not in sword_list" %(sim)
			else:
				pass
				#print "%s is in list_of_sim" %(sim)
		#print "\n\n\n%s in hyponyms" %(wrd)
		for hypo in wrd.hyponyms():
			for lemma in hypo.lemma_names:
				if lemma not in list_of_sim:
					#print "%s not in list_of_sim" %(lemma)
					if lemma in sword_list and lemma not in completed_list:
						#print "%s is in sword_list" %(lemma)
						list_of_sim.append(lemma)
					else:
						pass
						#print "%s is not in sword_list" %(lemma)
				else:
					pass
					#print "%s is in list_of_sim" %(lemma)
		if word in list_of_sim:
			list_of_sim.remove(word)
	return list_of_sim

rword_list = []
sword_list = []
completed_list = []
if __name__ == "__main__":

	# Try to get the input
	try:
		fp = open(sys.argv[1],'r')
		word_list = fp.read()
	except:
		word_list = sys.argv[1]

	no_of_word = 0
	# Count the number of words in the word_list
	for word in word_list.split():
		sword_list.append(word)
	for word in sword_list:
		list_of_sim = similar_Wrd(word)
		entity = (word, 0, 0, list_of_sim)
		rword_list.append(entity)
		print "%s" %(word)
		for sim in list_of_sim:
			if sim in sword_list:
				sword_list.remove(sim)
			print "%s" %(sim)
			completed_list.append(sim)
		completed_list.append(word)
		#sys.exit();
		no_of_word = no_of_word + 1
	#print "Total number of words : %d" %(no_of_word)

