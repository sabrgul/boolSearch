from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, delete, Text, column

from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    url = Column(String)

    def __repr__(self):
        return f"<Document(id='{self.id}', url= '{self.url}', text='{self.text}')>"


class Word(Base):
    __tablename__ = 'word'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    count = Column(Integer)

    def __repr__(self):
        return f"<Word(name= '{self.name}', count='{self.count}')>"


class Indexes(Base):
    __tablename__ = 'indexes'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('word.id'))
    doc_id = Column(Integer, ForeignKey('document.id'))
    word = relationship("Word", backref='word')

    def __repr__(self):
        return f"<Indexes(word_id= '{self.word_id}', doc_id='{self.word_id}')>"


class DBLoader:
    def __init__(self, user='postgres', password='postgres', database='postgres', host='localhost'):
        self.engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
        self.conn = self.engine.connect()
        self.session = sessionmaker(bind=self.engine)
        self.session = self.session()

    def close(self):
        self.conn.close()

    def req_insert_documents(self, docs: list["Document"]):
        self.session.bulk_save_objects(docs)
        self.session.commit()

    def req_insert_word(self, words: list["Word"]):
        self.session.bulk_save_objects(words)
        self.session.commit()

    def req_insert_indexes(self, indexes: list["Indexes"]):
        self.session.bulk_save_objects(indexes)
        self.session.commit()

    def req_select_document(self, id_):
        return self.session.query(Document).get(id_)

    def req_select_word_id(self, name):
        return self.session.query(Word).filter_by(name=name).one().id

    def req_filter_indexes(self, name):
        return self.session.query(Indexes).join(Indexes.word).filter(Word.name == name) \
            .values(column('doc_id'))

    def req_count_docs(self):
        return self.session.query(Document).count()

    def req_delete(self, table):
        delete_docs = delete(table).execution_options(synchronize_session="fetch")
        self.session.execute(delete_docs)
        self.session.commit()
