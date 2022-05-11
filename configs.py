import pymorphy2
import wikipediaapi
from nltk.corpus import stopwords

from db_loader import DBLoader

wiki_wiki = wikipediaapi.Wikipedia('ru')
russian_stopwords = stopwords.words('russian')
punctuation_list = ['−', '—', '«', '»', '==', '//']
morph = pymorphy2.MorphAnalyzer()

db = DBLoader(user='postgres', password='postgres', database='postgres', host='localhost')
results_file = 'files/results.txt'
invert_indexes_file = 'files/invert_indexes.txt'
category = "Категория:Литературные жанры"
tags_pos = ['NOUN', 'ADJF', 'ADJS', 'PRTF', 'PRTS']
bool_query = ('AND', 'OR')
language = "russian"