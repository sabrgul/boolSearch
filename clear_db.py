from bool_search import db
from db_loader import Indexes, Document, Word

if __name__ == '__main__':
    db.req_delete(Indexes)
    db.req_delete(Document)
    db.req_delete(Word)
