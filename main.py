from get_terms import get_terms_dict, get_list_without_stopwords, get_terms_list
from loading_files_from_wiki import loading_files_from_wiki


def analyze(text):
    tokens = text.split()
    tokens = get_list_without_stopwords(tokens)
    terms_ = get_terms_list(tokens)
    return [term for term in terms_ if term]


def get_sets_list(analyzed_query, index_):
    return [set(index_.get(token, '')) for token in analyzed_query]


def get_invert_index_dict(terms_dict, files_count):
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
    answer_list = sorted(count_in_docs_dict.items(), key=lambda d: d[1], reverse=True)
    answer_sorted = sorted(answer_list, key=lambda x: x[0])  # сортируем по aлфавиту
    invert_index = {}
    with open('files/invert_indexes.txt', 'w') as f:
        for word in answer_sorted:
            f.write("%s\t%d\t" % (word[0], word[1]))
            sort_doc_ids = sorted(
                doc_ids_dict[word[0]])  # сортируем список номеров документа, в которое входит данное слово
            invert_index[word[0]] = []
            for i in range(len(sort_doc_ids)):
                f.write(f'{sort_doc_ids[i]}')
                invert_index[word[0]] += [
                    sort_doc_ids[i]]  # добавляем номер док-та по отсортированному списку в словарь
                if i != len(sort_doc_ids) - 1:  # если не конец списка документа
                    f.write(" ")
            f.write('\n')
        f.close()
    return invert_index


def search(query, index_, documents_dict_, search_type='AND'):
    documents = []
    if search_type not in ('AND', 'OR'):
        return []

    analyzed_query = analyze(query)

    results = get_sets_list(analyzed_query, index_)
    if search_type == 'AND':
        documents = [documents_dict_[doc_id] for doc_id in set.intersection(*results)]
    if search_type == 'OR':
        documents = [documents_dict_[doc_id] for doc_id in set.union(*results)]

    return documents


def run_bool_search():
    files_count, documents_dict = loading_files_from_wiki()
    terms_dict = get_terms_dict()
    invert_index_dict = get_invert_index_dict(terms_dict, files_count)
    search_term = str(input("Введите слова для поиска "))
    with open('files/results.txt', 'w') as res_file:
        find_urls = search(search_term, invert_index_dict, documents_dict)
        for url in find_urls:
            res_file.write(f'{url}\n')


run_bool_search()