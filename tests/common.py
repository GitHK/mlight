""" Setup common utils needed during testing. """
import asyncio
import uuid

from mlight.session import DBSession


def loop_runner(async_function):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_function())


def get_db_session(host='localhost', port=27017, database_name='mlight'):
    # create a new database name each time and use that one at the end drop it in the files
    name = "%s_%s" % (database_name, str(uuid.uuid4()).replace('-', '_'))
    return DBSession('mongodb://%s:%s' % (host, port), name)


def drop_database(db_session):
    async def wrapped():
        await db_session.client.drop_database(db_session.database_name)
        print("Test database dropped!")

    loop_runner(wrapped)


def drop_collection(collection_name, db_session=None):
    async def wrapped():
        session = get_db_session() if db_session is None else db_session

        await session.database[collection_name].drop()
        print("Collection '%s' dropped" % collection_name)

    loop_runner(wrapped)


def drop_all_collections(db_session=None):
    async def wrapped():
        session = get_db_session() if db_session is None else db_session

        for collection in await session.database.collection_names(include_system_collections=False):
            await session.database[collection].drop()
            print("Collection '%s' dropped" % collection)

    loop_runner(wrapped)
