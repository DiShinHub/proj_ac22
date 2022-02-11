import pymongo
from pymongo import ASCENDING, DESCENDING
from config.config import Config


class Mongo:

    def __init__(self):
        config = Config()
        self.client = config.set_mongo()
        self.db = self.client["upbit"]
        self.col = None
        self.inserted_id = None
        self.doc = None

    def get_col_list(self):
        """ def description : 컬렉션 리스트 리턴

        Returns
        -------
        collection_names : 컬렉션 리스트 (list)
        """
        return self.db.collection_names()

    def set_col(self, col):
        """ def description : 컬렉션 셋팅

        Parameters : 
        col : 컬렉션(str) 

        Returns
        -------
        col : 컬렉션 (obj)
        """
        self.col = self.db[col]
        return self.col

    def is_col(self):
        """ def description : 컬렉션이 정상 셋팅 되었는지 확인

        Returns
        -------
        boolean 
        """
        if self.col:
            if self.col.name in self.get_col_list():
                return True

        return False

    def insert_doc(self, post):
        """ def description : 다큐먼트 삽입

        Parameters : 
        post : json 데이터 (dict) 

        Returns
        -------
        inserted_id : 삽입 된 아이디 (str)
        """
        self.inserted_id = None
        if self.is_col():
            self.inserted_id = self.col.insert_one(post).inserted_id

        return self.inserted_id

    def get_doc_one(self):
        """ def description : 다큐먼트 단일 조회

        Returns
        -------
        doc : 조회 데이터 (dict) 
        """

        self.doc = None
        if self.is_col():
            self.doc = self.col.find_one(sort=[("_id", -1)])

        return self.doc

    def get_doc(self, limit):
        """ def description : 다큐먼트 복수 조회

        Returns
        -------
        doc : 조회 데이터 (list)) 
        """
        results = self.col.find().sort("_id", DESCENDING).limit(limit)

        data_list = []
        for result in results:
            data_list.append(result)

        return data_list
