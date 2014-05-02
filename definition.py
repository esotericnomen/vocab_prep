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
	retry = 0
	try:
		size = os.path.getsize(mp3_file_path)
	except:
		size = 0
	if((os.path.isfile(mp3_file_path) is False)or (size is 0)):
		while 1:
			retry = retry+1
			print "try %d" %(retry)
			cmd = "wget -q -U Mozilla -O "+mp3_file_path+" \"http://translate.google.com/translate_tts?ie=UTF-8&tl=en&q="+word+"\""
			os.system(cmd)
			if((os.path.getsize(mp3_file_path) is not 0) or (retry is 3)):
				break;
	subprocess.call(["ffplay", "-nodisp", "-autoexit", mp3_file_path],stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
	print subprocess.check_output(["espeak", "-q", "--ipa",'-v', 'en-us', word]).decode('utf-8')

def wndef(word):
	for ss in wn.synsets(word):
		print "%20s : %s\n" % (word,ss.definition)
		time.sleep(0.5)

def similar_Wrd(word):
	list_of_sim=[]
	for wrd in wn.synsets(word):
		for sim in wrd.lemma_names:
			if sim not in list_of_sim:
				list_of_sim.append(sim)
	print "words similar to "+word
	print "----------------------------------------------------------------------------------------------------"
	cols = 4
	split=[list_of_sim[i:i+len(list_of_sim)/cols] 
	for i in range(0,len(list_of_sim),len(list_of_sim)/cols)]
	for row in zip(*split):
		print "".join(str.ljust(i,20) for i in row)
	print "----------------------------------------------------------------------------------------------------"


def jdef(word):
	def_file_path = "/home/shingu/workspace/vocab_prep/definition_cache/"+word+".txt"
	retry = 0
	try:
		size = os.path.getsize(def_file_path)
	except:
		size = 0
	if((os.path.isfile(def_file_path) is False) or (size is 0) ):
  		url="http://www.vocabulary.com/dictionary/"+word
		while 1:
			retry = retry+1
			print "try %d" %(retry)
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
			if((os.path.isfile(def_file_path) is not False) or (retry is 3)):
				break;
	else:
		def_file = open(def_file_path,"r")
		print "----------------------------------------------------------------------------------------------------"
		print def_file.read()
		print "----------------------------------------------------------------------------------------------------"

def update_db(word,curr):
#  conn.execute('''CREATE TABLE table_words 
			#(word TEXT NOT NULL,
			# count INT NOT NULL);''')
	cur.execute("Select * from table_words where word = ?", (word,))
	rword=cur.fetchone()
	if rword is None:
		cur.execute("INSERT INTO table_words VALUES (?,?)",(word,0));
	else:
		cur.execute("UPDATE table_words set count = ? where word = ?", (rword[1]+1,word));

if __name__ == "__main__":

	# Input arguments check
	if((len(sys.argv) != 2) and (len(sys.argv) != 5)):
		print_summary()
		sys.exit()

	known = 0
	studied = 0
	words = 0

	conn = sqlite3.connect(r"/home/shingu/workspace/vocab_prep/words.db")
	cur = conn.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS table_words(word TEXT, count INT)")
	l = WordNetLemmatizer()

	try:
		fp = open(sys.argv[1],'r')
		wlist = fp.read()
		if(int(1) == int(sys.argv[4])):
			get_opt=1
		else:
			get_opt=0
			opt='u'
	except:
		wlist = sys.argv[1]
		get_opt=0
		opt='m'

	for word in wlist.split():
		words = words + 1
	print "Total words : %d" %(words)

	count = 0
	for word in wlist.split():
		if len(wn.synsets(word)) is not 0:
			rlemma = l.lemmatize(word)
			count = count+1
			if(len(sys.argv) is 5):
				if(count < int(sys.argv[2])):
					continue
				if(count >= int(sys.argv[3])):
					break
			if(get_opt):
				opt = raw_input( "Display %s : %s?  :   " % (word,l.lemmatize(word)))
			update_db(word.lower(),cur)
			gplay(word.lower())
			wndef(word.lower())
			jdef(word.lower())
			similar_Wrd(word.lower())
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
	conn.commit()
	conn.close()
	sys.exit()
