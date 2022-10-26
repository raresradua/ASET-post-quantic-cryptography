import pymongo


MONGO_URI = 'mongodb://localhost:27017'


class Mongo:
    instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Mongo, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.client = pymongo.MongoClient(host=MONGO_URI)
        self.db_cursor = None
        self.collection = None

    def get_db_cursor(self, database_name: str):
        self.db_cursor = self.client.get_database(name=database_name)

    def get_collection(self, collection: str):
        self.collection = self.db_cursor[collection]

    def insert(self, document: dict):
        self.collection.insert_one(document)

    def update(self, filtr: dict, field: dict):
        self.collection.find(filtr, field)
