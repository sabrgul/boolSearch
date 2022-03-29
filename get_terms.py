from string import punctuation

import nltk
import pymorphy2
from nltk import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')
russian_stopwords = stopwords.words('russian')
punctuation_list = ['−', '—', '«', '»', '==', '//']
morph = pymorphy2.MorphAnalyzer()


def get_list_without_stopwords(tokenize_text: list[str]) -> list[str]:
    """Убираем стоп-слова и символы пунктуации, устанавливаем слова в нижний регистр"""
    return [
        word.lower() for word in tokenize_text
        if word not in russian_stopwords
        and word not in punctuation
        and word not in punctuation_list
    ]


def get_terms_list(text: list[str]) -> list[str]:
    """Отбираем термы, проводим лемматизацию"""
    words = []
    for word in text:
        word_morph_parse = morph.parse(word)[0]
        if word_morph_parse.tag.POS in ['NOUN', 'ADJF', 'ADJS', 'PRTF', 'PRTS']:
            words += [word_morph_parse.normal_form]
    return words


def get_terms_dict(files_count=193) -> dict:
    terms = {}
    for i in range(1, files_count + 1):
        with open(f'files/{i}.txt', 'r') as doc:
            doc_text = doc.read()
            tokenize_text = word_tokenize(doc_text, language="russian")  # делаем токенизацию
            words_list_without_stopwords = get_list_without_stopwords(tokenize_text)
            terms[i] = get_terms_list(words_list_without_stopwords)
    return terms
