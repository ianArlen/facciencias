from pybtex.database.input import bibtex
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import re
from time import time
from os import scandir, getcwd

import bibtexparser



def is_letters(text,i):	
	if ord(text[i])>=65 and ord(text[i])<=90:	return True
	if ord(text[i])>=97 and ord(text[i])<=122:	return True
	return False

def affiliations(text):
	l_affiliations = []
	word = ''
	for i in range(0,len(text)):
		if is_letters(text,i):	
			word += text[i].upper()
		elif text[i] ==',':
			l_affiliations.append(word)	
			word = ''
		elif text[i] =='.' and text[i+1] =='\n':
			l_affiliations.append(word)
			l_affiliations.append('.\n')
			word = ''
		elif text[i] =='.' and i+2 == len(text):
			l_affiliations.append(word) 
			l_affiliations.append('.\n')
	return  l_affiliations

def levenshtein_distance(str1, str2):
  strLen1 = len(str1)
  strLen2 = len(str2)

  d = [[0 for x in range(strLen1+1)] for y in range(strLen2+1)]
  
  for i in range(strLen1+1):
    d[0][i] = i

  for j in range(strLen2+1):
    d[j][0] = j

  for i in range(1,strLen1+1):
    for j in range(1,strLen2+1):
    
      if str1[i-1] == str2[j-1]:
        substitionCost = 0
      else:
        substitionCost = 1
      d[j][i] = min(d[j-1][i]+1,
          d[j][i-1]+1,
          d[j-1][i-1]+substitionCost)

  return d[strLen2][strLen1]

def keep_records(record):
	file = open('record/record.txt', 'w')
	file.write(record)
	file.close()

def recharge_records():
	file = open ('record/record.txt','r')
	record = file.read()
	file.close()
	return record

def line_ambiguity(idArticle, ambiguity, file):
	record = ''
	record += idArticle + ', '
	record += ambiguity + ', '
	record += file + '\n'
	return record 

def is_unam(unam):
	if unam in ['UNIVNACLAUTONOMAMEXICO','UNAM']:
		return True 
	return False

def is_Science(word1):
	wordFake = ['(.*)INST(.*)CIENCIA[S]?(.*)','F(.*)CIENCIA[S]?(.*)NAT(.*)',
					'F(.*)CIENCIA[S]?(.*)PO(.*)','(.*)CIENCIA[S]?(.*)SOC',
					'(.*)NEURO(.*)CIENCIA[S]?(.*)','(.*)FILO(.*)CIENCIA[S]?(.*)',
					'(.*)POSGRAD(.*)CIENCIA[S]?(.*)','(.*)CONDUCTA(.*)CIENCIA[S]?(.*)',
					'(.*)CIENCIA[S]?(.*)COND','(.*)CIENCIA[S]?(.*)AGRO(.*)',
					'(.*)CIENCIA[S]?(.*)GENO(.*)','F(.*)CIENCIA[S]?(.*)QUI(.*)ING',
					'(.*)ENES(.*)','(.*)F(.*)CIENCIA[S]?(.*)VET(.*)',
					'CLININMUNO(.*)F(.*)CIENCIA[S]?(.*)VET(.*)','(.*)RESFELLOW(.*)F(.*)CIENCIA[S]?',
					'(.*)FES(.*)CUAUTI(.*)','(.*)NANO(.*)CIENCIAS(.*)','(.*)CLINI(.*)CIENCIA(.*)',
					'(.*)INSTFORTALE(.*)','FACMEDPOGRAMA(.*)','(.*)CIENC(.*)POL(.*)']
	for i in range(0,len(wordFake)):
		if re.match(wordFake[i], word1):
			return False
	
	wordScience = ['(.*)F(.*)CIENCIA[S]?(.*)','(.*)ACU(.*)CIENCIA[S]?(.*)']
	for i in range(0,len(wordScience)):
		if re.match(wordScience[i], word1):
			return True	

	wordLevenshtein = ['FCIENCIAS','FACIENCIAS','FACCIENCIAS','FACUCIENCIAS',
						'FACULCIENCIAS','FACULTCIENCIAS','FACULTACIENCIAS',
						'FACULTADCIENCIAS','FACULTADDECIENCIAS', 'FSCIENCE',
						'FASCIENCE', 'FACSCIENCE', 'FACUSCIENCE','FACULSCIENCE', 
						'FACULTSCIENCE','FACULTYSCIENCE']

	for i in range(0,len(wordLevenshtein)):
		if levenshtein_distance(word1,wordLevenshtein[i]) < 3:
			return True
	
	return False

def word_in_paragraph(unam, i, institutions, j, file):
	record = '' 
	record += str(recharge_records())
	k = j + 1
	l = 0  
	while is_unam(institutions[j]) and institutions[k+l] != '.\n':
		if is_Science(institutions[k+l]):
			record += line_ambiguity(unam[i]['ID'],institutions[k+l],file)
			keep_records(record)
			return unam[i]
		l = l + 1
	return None 	

def word_ambiguity(unam, file):
	sciencefaculty = []
	institutions = []
	fscience = [] 
	for i in range(0,len(unam)):
		if 'affiliation' in unam[i]:
			institutions = affiliations(unam[i]['affiliation']) 
			for j in range(0,len(institutions)):
				article = word_in_paragraph(unam,i,institutions,j,file)
				if not article == None:
					fscience.append(article)
					break	
	return fscience 

def read_Bibtex(file):
	with open('unam/'+file) as bibtex_file:
		bib_database = bibtexparser.load(bibtex_file)
	return bib_database.entries 

def write_Bibtex(fscience): 
	db = BibDatabase()
		
	for i in range(0,len(fscience)):
		db.entries+=[fscience[i]]
	writer = BibTexWriter()
	with open('fciencias/fciencias.bib', 'w') as bibfile:
        	bibfile.write(writer.write(db))

def ls(ruta = getcwd()+'/unam'):
    return [arch.name for arch in scandir(ruta) if arch.is_file()]

def set_fscience():
	#Lectura de los archivos bibtex
	files = ls()
	unam = []
	fscience = []
	keep_records('')

	print('Inicio del programa, esto puede tardar algunos minutos')
	for i in range(0,len(files)):
		start_time = time()
		print('Carga del archivo ' + str(files[i]) + 
				' proceso ' + str(i+1) + ' de ' + str(len(files)-1))
		unam = read_Bibtex(files[i])
		fscience += word_ambiguity (unam,str(files[i]))

		elapsed_time = time() - start_time

		print('El tiempo de filtrar ' + str(len(unam)) + ' articulos: %.10f segundos.' % elapsed_time)
		approximate_time = ((len(files)-(i+1)) * elapsed_time)/60
		print('El tiempo de espera aproximado es de ' + str(approximate_time) + ' minutos.')

	print('Se tienen en total ' + str(len(fscience)) + ' articulos de la facultad de ciencias.')

	write_Bibtex(fscience)

start_time = time()
set_fscience()
elapsed_time = time() - start_time
print('El tiempo total de este programa fue de: %.10f minutos.' % (elapsed_time/60))