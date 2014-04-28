#!/usr/bin/env python

import sys					# for system io
import sqlite3					# for DB Activities
import urllib2					# for url parssing et al
import textwrap					# To limit o/p characters per line
import subprocess				# To invoke espeak
import time
import os
from nltk.corpus import wordnet as wn		# Wordnet DB
from nltk.stem.wordnet import WordNetLemmatizer	# To Obtain Lemma
from BeautifulSoup import BeautifulSoup		

def print_summary():
	print "\n \
		This module can be used to study words in list. \n \
		Usage : \n \
	 	$ "+ sys.argv[0] +" input_file \n \
			input_file : text file containing list of words \
	" 
def eplay(word):
	espeak_cmd = 'espeak  -s 150 -v en-us+f5 '
	subprocess.call( espeak_cmd +"'"+word+"'", shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

def gplay(word):
	mp3_file_path = "/home/shingu/workspace/vocab_prep/audio_cache/"+word+".mp3"
	if(os.path.isfile(mp3_file_path) is False):
		cmd = "wget -q -U Mozilla -O "+mp3_file_path+" \"http://translate.google.com/translate_tts?ie=UTF-8&tl=en&q="+word+"\""
		os.system(cmd)
	subprocess.call(["ffplay", "-nodisp", "-autoexit", mp3_file_path],stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

def wndef(word):
	for ss in wn.synsets(word):
		print "%20s : %s\n" % (word,ss.definition)
		time.sleep(0.5)
def similar_Wrd(word):
	for ss in wn.synsets(word):
		print(ss.lemma)
#print ss.similar_tos()
    		for sim in ss.similar_tos():
        		print('    {}'.format(sim))

def jdef(word):
	def_file_path = "/home/shingu/workspace/vocab_prep/definition_cache/"+word+".txt"
	if(os.path.isfile(def_file_path) is False):
  		url="http://www.vocabulary.com/dictionary/"+word
		try:
			response = urllib2.urlopen(url)
			replace = ["\"","<i>","</i>","<p class=long>","<p class=short>","</p>"]
			html = response.read()
			soup = BeautifulSoup(html)
			rshort = soup.findAll(attrs={"class" : "short"})
			rlong = soup.findAll(attrs={"class" : "long"})
			try:
				rlong = str(rlong[0])
			except:
				print "Long decode failed"
			try:
				rshort = str(rshort[0])
			except:
				print "Short decode failed"
			for rep in replace:
				rlong=rlong.replace(rep,"")
				rshort = rshort.replace(rep,"")
			def_file = open(def_file_path,"w")
			def_file.write("%s\n\n%s\n\n" % (textwrap.fill(rshort, width=100),textwrap.fill(rlong, width=100)))
			print "%s\n\n%s\n\n" % (textwrap.fill(rshort, width=100),textwrap.fill(rlong, width=100))
		except:
			print "Vocabulary error for word : %s\n" %(word)
	else:
		def_file = open(def_file_path,"r")
		print "----------------------------------------------------------------------------------------------------"
		print def_file.read()
		print "----------------------------------------------------------------------------------------------------"


if __name__ == "__main__":

	# Input arguments check
	if(len(sys.argv) != 2):
		print_summary()
		sys.exit()

	known = 0
	studied = 0
	words = 0

	l = WordNetLemmatizer()

	try:
		fp = open(sys.argv[1],'r')
		wlist = fp.read()
		get_opt=1
	except:
		wlist = sys.argv[1]
		get_opt=0
		opt='m'

	for word in wlist.split():
		words = words + 1
	print "Total words : %d" %(words)

	for word in wlist.split():
		if len(wn.synsets(word)) is not 0:
			rlemma = l.lemmatize(word)
			if(get_opt):
				opt = raw_input( "Display %s : %s?  :   " % (word,l.lemmatize(word)))
			gplay(word.lower())
			wndef(word.lower())
			jdef(word.lower())
			#similar_Wrd(word.lower())
			if opt == 's':
				studied = studied+1
				for ss in wn.synsets(word):
					print "%20s : %s\n" % (word,ss.definition)
					eplay(ss.definition)
					time.sleep(0.5)
			if opt == 'e':
			  	print "Current streak : %d %d" % (studied,known)
				sys.exit()
			else:
				known = known+1

	
	print "Current streak : %d %d" % (studied,known)
	sys.exit()
