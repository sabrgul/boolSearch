import wikipediaapi
from string import punctuation

import nltk
from nltk import word_tokenize

from configs import (
    wiki_wiki, category, db, russian_stopwords,
    punctuation_list, language, morph, tags_pos, bool_query,
    results_file
)
from db_loader import Document, Word, Indexes

nltk.download('punkt')
nltk.download('stopwords')


def save_files_from_wiki():
    """Сохраняем страницы определенной категории и их url в БД"""
    wiki_page = wiki_wiki.page(category)
    doc_id = 1
    documents = []
    for p in wiki_page.categorymembers.values():
        if p.namespace == wikipediaapi.Namespace.MAIN:
            documents += [Document(id=doc_id, text=p.text, url=p.canonicalurl)]
            doc_id += 1
    db.req_insert_documents(documents)


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
        if word_morph_parse.tag.POS in tags_pos:
            words += [word_morph_parse.normal_form]
    return words


def get_terms_dict(files_count) -> dict:
    """Формируем словарь со списком термов каждого документа"""
    terms = {}
    for doc_id in range(1, files_count):
        doc_text = db.req_select_document(id_=doc_id).text
        tokenize_text = word_tokenize(doc_text, language=language)  # делаем токенизацию
        words_list_without_stopwords = get_list_without_stopwords(tokenize_text)
        terms[doc_id] = get_terms_list(words_list_without_stopwords)
    return terms


def get_search_terms_list(text: str) -> list[str]:
    """Проводим анализ поискового запроса и формируем термы из запросивших слов для дальнейшего поиска"""
    tokens = text.split()
    tokens = get_list_without_stopwords(tokens)
    terms_ = get_terms_list(tokens)
    return [term for term in terms_ if term]


def get_sets_list(analyzed_query: list) -> list[set]:
    """Формируем множества с индексами документов, в которых есть слово из запроса"""
    return [set(db.req_filter_indexes(token)) for token in analyzed_query]


def save_invert_index(terms_dict: dict, files_count: int):
    """Формируем инвертированный индекс и сохраняем в БД"""
    doc_ids_dict = {}  # словарь с номерами документов
    count_in_docs_dict = {}  # словарь с частотой использования слова в документах
    for i in range(1, files_count):
        terms = terms_dict[i]
        for word in terms:
            if word == '':
                continue
            if word not in doc_ids_dict:
                doc_ids_dict[word] = set()
                count_in_docs_dict[word] = 1
            else:
                count_in_docs_dict[word] += 1
            doc_ids_dict[word].add(i)

    # сортируем по частоте использования слов в документах
    sorted_count_in_docs_list = sorted(count_in_docs_dict.items(), key=lambda d: d[1], reverse=True)
    sorted_alphabet_words = sorted(sorted_count_in_docs_list, key=lambda x: x[0])  # сортируем по aлфавиту
    indexes_list = []
    for word in sorted_alphabet_words:
        words = [Word(name=word[0], count=word[1])]
        db.req_insert_word(words)
        # сортируем список номеров документа, в которое входит данное слово
        sort_doc_ids = sorted(doc_ids_dict[word[0]])
        word_id = db.req_select_word_id(word[0])
        for i in range(len(sort_doc_ids)):
            indexes_list += [Indexes(word_id=word_id, doc_id=sort_doc_ids[i])]
    db.req_insert_indexes(indexes_list)


def bool_search(query: str, search_type='AND') -> list[str]:
    """Проводим булев поиск"""
    documents = []
    if search_type not in bool_query:
        return []

    search_terms_list = get_search_terms_list(query)

    results = get_sets_list(search_terms_list)
    if len(results) > 0:
        if search_type == 'AND':
            documents = [db.req_select_document(doc_id).url for doc_id in set.intersection(*results)]
        if search_type == 'OR':
            documents = [db.req_select_document(doc_id).url for doc_id in set.union(*results)]
    return documents


def run_bool_search():
    """Запускаем булев поиск"""
    search_term = str(input("Введите слова для поиска "))
    with open(results_file, 'w') as res_file:
        find_urls = bool_search(search_term)
        for url in find_urls:
            res_file.write(f'{url}\n')
