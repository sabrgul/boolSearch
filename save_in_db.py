from bool_search import save_files_from_wiki, db, get_terms_dict, save_invert_index

if __name__ == '__main__':
    save_files_from_wiki()
    files_count = db.req_count_docs()
    terms_dict = get_terms_dict(files_count)
    save_invert_index(terms_dict, files_count)
