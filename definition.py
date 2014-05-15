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

sup_vocal = 0
sup_syn = 0
sup_desc = 0
sup_hyp = 0
sup_manual = 0
sup_cache_only = 0
sup_spellbee = 0
sup_pronounce = 0
wrong = []
correct = []
fout = open("/tmp/rm.txt","w");
list_of_sim_all=[]

class bcolors:
	Red = '\033[91m'
	Green = '\033[92m'
	Blue = '\033[94m'
	Cyan = '\033[96m'
	White = '\033[97m'
	Yellow = '\033[93m'
	Magenta = '\033[95m'
	Grey = '\033[90m'
	Black = '\033[90m'
	Default = '\033[99m'

def print_summary():
	print "\n \
		This module can be used to study words in list. \n \
		Usage : \n \
	 	$ "+ sys.argv[0] +" input_file options <start_range> <end_range>\n \
			input_file : text file containing list of words \n \
			options : Options to configure the run as below. \n\
				v : Support vocal \n\
				d : Support description \n\
				h : Support hypernym | hyponym \n\
				m : Support manual mode \n\
				c : Support Cache only mode  \n\
			\n\
			Entered only "+str(len(sys.argv))+" arguments \n\
	" 



def learn_spell(word,retry):
	mp3_file_path = "/home/shingu/workspace/vocab_prep/audio_cache/"+word+".mp3"
	try:
		size = os.path.getsize(mp3_file_path)
	except:
		size = 0
	subprocess.call(["ffplay", "-nodisp", "-autoexit", mp3_file_path],stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
	spell = raw_input()
	retry = retry +1
	if spell == word:
		return
	else:
	 	if(retry == 2):
			print bcolors.Blue + word +"  :: " +subprocess.check_output(["espeak", "-q", "--ipa",'-v', 'en-us', word]).decode('utf-8')+bcolors.White
			return
		else:
			wrong.append(word)
			print bcolors.Red +"                "+subprocess.check_output(["espeak", "-q", "--ipa",'-v', 'en-us', word]).decode('utf-8')+bcolors.White
			learn_spell(word,retry)

def eplay(word,cur):
	espeak_cmd = 'espeak  -s 150 -v en-us+f5 '
	subprocess.call( espeak_cmd +"'"+word+"'", shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

def gplay(word,cur):
	mp3_file_path = "/home/shingu/workspace/vocab_prep/audio_cache/"+word+".mp3"
	retry = 0
	try:
		size = os.path.getsize(mp3_file_path)
	except:
		size = 0
	if((os.path.isfile(mp3_file_path) is False)or (size is 0)):
		if(sup_cache_only is 0):
			while 1:
				retry = retry+1
				print "try %d" %(retry)
				cmd = "wget -q -U Mozilla -O "+mp3_file_path+" \"http://translate.google.com/translate_tts?ie=UTF-8&tl=en&q="+word+"\""
				os.system(cmd)
				if((os.path.getsize(mp3_file_path) is not 0) or (retry is 3)):
					break;
	subprocess.call(["ffplay", "-nodisp", "-autoexit", mp3_file_path],stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
	if(cur is not None):
		print bcolors.Blue + word +"  :: " +subprocess.check_output(["espeak", "-q", "--ipa",'-v', 'en-us', word]).decode('utf-8')

def wndef(word,cur):
	for ss in wn.synsets(word):
		print bcolors.Green + "%20s : %s\n" % (word,ss.definition)
		#eplay(ss.definition, cur)
		time.sleep(0.5)

def print_list(l,col):
	try:
		print "----------------------------------------------------------------------------------------------------"
		if len(l) % 4 != 0:
   			l.append(" ")
   			l.append(" ")
   			l.append(" ")

		split = len(l)/4
		l1 = l[0:split]
		l2 = l[split:2*split]
		l3 = l[2*split:3*split]
		l4 = l[3*split:]
		for word1, word2, word3, word4 in zip(l1,l2, l3, l4):
   			print '%-20s %-20s %-20s %-20s' % (word1, word2, word3, word4)         #python <2.6
		print "----------------------------------------------------------------------------------------------------"
	except:
		pass
def similar_Wrd(word,cur):
	list_of_sim=[]
	for wrd in wn.synsets(word):
		for sim in wrd.lemma_names:
			if sim not in list_of_sim:
				list_of_sim.append(sim)
			if sim not in list_of_sim_all:
				list_of_sim_all.append(sim)
		for hypo in wrd.hyponyms():
			for lemma in hypo.lemma_names:
				if lemma not in list_of_sim:
					list_of_sim.append(lemma)
			if sim not in list_of_sim_all:
				list_of_sim_all.append(lemma)
		if word in list_of_sim:
			list_of_sim.remove(word)
		if word in list_of_sim_all:
			list_of_sim_all.remove(word)

	if(len(list_of_sim)):
		print bcolors.Yellow + "words similar to "+word
		print_list(list_of_sim,4)

def wrd_hyponyms(word,cur):
	list_of_hyponyms = []
	presence = 0
	for wrd in wn.synsets(word):
		for hypo in wrd.hyponyms():
			for lemma in hypo.lemma_names:
				if lemma not in list_of_hyponyms:
					presence = 1
					list_of_hyponyms.append(lemma)
	if(presence):
		print bcolors.Cyan + "hyponyms of "+word
		print_list(list_of_hyponyms,1)

def jdef(word,cur):
	def_file_path = "/home/shingu/workspace/vocab_prep/definition_cache/"+word+".txt"
	retry = 0
	try:
		size = os.path.getsize(def_file_path)
	except:
		size = 0
	if((os.path.isfile(def_file_path) is False) or (size is 0) ):
		if(sup_cache_only is 0):
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
						pass
					try:
						rshort = str(rshort[0])
					except:
						pass
					for rep in replace:
						rlong=rlong.replace(rep,"")
						rshort = rshort.replace(rep,"")
					def_file = open(def_file_path,"w")
					def_file.write("%s\n\n%s\n\n" % (textwrap.fill(rshort, width=100),textwrap.fill(rlong, width=100)))
					print  bcolors.White + "%s\n\n%s\n\n" % (textwrap.fill(rshort, width=100),textwrap.fill(rlong, width=100))
				except:
					pass
				if((os.path.isfile(def_file_path) is not False) or (retry is 3)):
					break;
				print "Vocabulary error for word : %s\n" %(word)
	else:
		def_file = open(def_file_path,"r")
		print "----------------------------------------------------------------------------------------------------"
		print bcolors.White + def_file.read()
		print "----------------------------------------------------------------------------------------------------"

def update_db(word,cur):
#  conn.execute('''CREATE TABLE table_words 
			#(word TEXT NOT NULL,
			# count INT NOT NULL);''')
	cur.execute("Select * from table_words where word = ?", (word,))
	rword=cur.fetchone()
	if rword is None:
		cur.execute("INSERT INTO table_words VALUES (?,?)",(word,0));
	else:
		cur.execute("UPDATE table_words set count = ? where word = ?", (rword[1]+1,word));

def sub_main(word,cur):
	#update_db(word,cur)
	if(sup_vocal):
		gplay(word,cur)
	wndef(word,cur)
	if(sup_desc):
		jdef(word,cur)
	if(sup_hyp):
		similar_Wrd(word,cur)
		#wrd_hyponyms(word,cur)

def rspellbee():
	for entity in wrong:
		gplay(entity[0],None)
		spell = raw_input()
		if spell == entity[0]:
			correct.append(entity)
			wrong.remove(entity)
		else:
			tword = entity[0]
			tcount = entity[1]
			if(tcount > 1):
				print "Failed in :    "+entity[0]
				wrong.remove(entity)
				break
			wrong.remove(entity)
			tentity = (tword, tcount + 1)
			wrong.append(tentity)
			print " :( Wrong\n"
	if(len(wrong) is not 0):
		rspellbee()


if __name__ == "__main__":

	# Input arguments check
	if((len(sys.argv) != 3) and ((len(sys.argv) != 5))):
		print_summary()
		sys.exit()

	# Configuration setup 
	if 'v' in sys.argv[2]:
		sup_vocal = 1

	if 's' in sys.argv[2]:
		sup_syn = 1
	
	if 'd' in sys.argv[2]:
		sup_desc = 1
	
	if 'h' in sys.argv[2]:
		sup_hyp = 1
	
	if 'm' in sys.argv[2]:
		sup_manual = 1
	
	if 'c' in sys.argv[2]:
		sup_cache_only = 1

	if 'spell' in sys.argv[2]:
		sup_spellbee = 1

	if 'pron' in sys.argv[2]:
		sup_pronounce = 1

	studied = 0
	no_of_word = 0

	# Database setup
	conn = sqlite3.connect(r"/home/shingu/workspace/vocab_prep/words.db")
	cur = conn.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS table_words(word TEXT, count INT)")
	#l = WordNetLemmatizer()

	# Try to get the input
	try:
		fp = open(sys.argv[1],'r')
		word_list = fp.read()
	except:
		word_list = sys.argv[1]

	# Count the number of words in the word_list
	for word in word_list.split():
		no_of_word = no_of_word + 1
	print bcolors.White+"Total number of words : %d" %(no_of_word)

	iterator = 0

	if(sup_pronounce):
		for word in word_list.split():
			learn_spell(word,0)

		for word in wrong:
			print bcolors.Red +"                "+word+" :: "+subprocess.check_output(["espeak", "-q", "--ipa",'-v', 'en-us', word]).decode('utf-8')+bcolors.White
		print bcolors.White + "Completed spell learning"
		sys.exit()

	if(sup_spellbee):
		for word in word_list.split():
			if len(wn.synsets(word)) is not 0:
				tcount = 0
				learnt = 0

				entity =(word, tcount)
				wrong.append(entity)
		rspellbee()
		correct = sorted(correct,key=lambda x: x[1],reverse=True)
		for entity in correct:
			if(entity[1] is not 0):
				print "%20s : %d" % (entity[0],entity[1])
		print bcolors.White + "Completed spell bee"
		sys.exit()

	for word in word_list.split():
		if len(wn.synsets(word)) is not 0:
			#rlemma = l.lemmatize(word)
			iterator = iterator + 1
			if(len(sys.argv) is 5):
				if(iterator < int(sys.argv[3])):
					continue
				if(iterator >= int(sys.argv[4])):
					break
			if(sup_manual):
				opt = raw_input( bcolors.White+"Display %3d / %3d %20s  : ? " % (iterator,no_of_word,word))
				if opt == '/':
					sub_main(word.lower(),cur)
				if opt == 'e':
					print bcolors.White + "Completed manually"
					sys.exit()
			else:
				sub_main(word.lower(),cur)
	if(len(list_of_sim_all) is not 0):
		for word in list_of_sim_all:
		   fout.write("%s\n" % (word))
	print bcolors.White + "Completed words"
	conn.commit()
	conn.close()
	sys.exit()
# [ node1, node2, node3, node4, node5 ]
# [ (node1,node2), (node1, node5), (node2,node3),(node3,node4)]
