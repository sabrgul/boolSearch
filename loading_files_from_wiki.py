import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia('ru')


def loading_files_from_wiki():
    """
    Выгружаем страницы определенной категории из вики в файлы
    и формируем словарь с урлами и id док-тов
    Возвращаем количество файлов и словарь с урлами
    """

    category = "Категория:Литературные жанры"
    indexes_file = 'files/index.txt'
    wiki_page = wiki_wiki.page(category)
    documents_dict = {}
    i = 1
    for p in wiki_page.categorymembers.values():
        if p.namespace == wikipediaapi.Namespace.MAIN:
            file_name = f'{i}.txt'
            with open(f'files/{file_name}', 'w') as f:
                f.write(p.text)
            documents_dict[i] = p.canonicalurl
            i += 1
    with open(indexes_file, 'w') as file:
        file.write(f'{documents_dict}\n')
    return i, documents_dict

