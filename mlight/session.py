from collections import deque

import motor.motor_asyncio


class DBSession:
    def __init__(self, mongo_uri, database_name):
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.registered_models = deque()

    @property
    def database(self):
        """ Returns the motor database object. """
        return self.client[self.database_name]

    def register_model(self, model):
        """ Register models to session and also create indexes. """
        if model not in self.registered_models:
            self.registered_models.append(model)

    async def create_indexes(self):
        """ Creates indexes on the registered collections. """
        for collection in self.registered_models:
            await collection.create_indexes()

    def clear_all(self):
        """ Removes all the documents ready to be flushed. """
        for collection in self.registered_models:
            collection.clear_all()

    async def flush_all(self, check_integrity=True):
        """
        Stores the current modified items to the database.
        :param check_integrity: if False skips the mapping check on each document.
        """
        for obj in self.registered_models:
            await obj.flush_all(check_integrity)
