import pymongo
import os

MONGO_URI = os.environ.get('MONGODB_CONNSTRING') or 'mongodb://user:user@localhost:27017'


class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient(host=MONGO_URI)
        self.db_cursor = self.set_db_cursor('ASET')
        self.collection = self.set_collection('users')

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Mongo, cls).__new__(cls)
        return cls.instance

    def set_db_cursor(self, database_name: str):
        return self.client.get_database(name=database_name)

    def set_collection(self, collection: str):
        return self.db_cursor[collection]

    def get_db_cursor(self):
        return self.db_cursor

    def get_collection(self):
        return self.collection

    def insert(self, document: dict):
        self.collection.insert_one(document)

    def update(self, filtr: dict, field: dict):
        self.collection.find(filtr, field)
