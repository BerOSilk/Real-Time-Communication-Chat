import pymongo

import pymongo.collection

connection = mongo = pymongo.MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.')


class Database:

    def __init__(self,database_name: str) -> None:
        self._db = connection[database_name]
    
    def get_db(self):
        return self._db

    def find(self, collection: str, query: dict = None, attributes: dict = None, sort: list = None, limit: int = -1):

        query = query or {}
        attributes = attributes or {}

        col = self._db[collection]
        res = col.find(query,attributes)
        if sort:
            res = res.sort(sort[0],sort[1])
        if limit > -1:
            res = res.limit(limit)
        return res
    
    def insert(self, collection: str, values: list = []):
        col = self._db[collection]
        col.insert_many(values)
    
    def delete_one(self, collection: str, query: dict = {}):
        col = self._db[collection]
        return col.delete_one(query)
    
    def delete_many(self, collection: str, query: dict = {}):
        col = self._db[collection]
        return col.delete_many(query)

    def drop(self, collection: str):
        col = self._db[collection]
        return col.drop()
    
    def update_one(self, collection: str, query: dict = {}, values: dict = {}):
        col = self._db[collection]
        col.update_one(query,values)
    
    def update_many(self, collection: str, query: dict = {}, values: dict = {}):
        col = self._db[collection]
        col.update_one(query,values)