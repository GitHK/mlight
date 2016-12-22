from pprint import pprint

import pymongo
from bson import ObjectId
from nose import with_setup

from mlight.attributes import FieldProperty
from mlight.meta_model import MetaModel
from tests.common import get_db_session, drop_all_collections, loop_runner, drop_database

db_session = get_db_session()


def setup_module():
    print("Module '%s' setup" % __name__)


def teardown_module():
    drop_all_collections(db_session=db_session)
    drop_database(db_session)
    print("Module '%s' teardown" % __name__)


def setup_function():
    db_session.clear_all()
    print("\nTest setup")


def teardown_function():
    db_session.clear_all()
    drop_all_collections(db_session=db_session)
    print("Test teardown")


@with_setup(setup_function, teardown_function)
def test_index_creation_successful():
    class IndexedDocument(MetaModel):
        session = db_session
        __model__ = 'indexed_document'

        indexes = [
            [('name', pymongo.DESCENDING)],
            [('age', pymongo.ASCENDING)]
        ]

        unique_indexes = [
            [('height', pymongo.DESCENDING)]
        ]

        _id = FieldProperty(ObjectId, if_missing=ObjectId)
        name = FieldProperty(str, required=True, if_missing='')
        age = FieldProperty(int, required=True)
        height = FieldProperty(float)

    db_session.register_model(IndexedDocument)

    async def run_async():
        await IndexedDocument.create_indexes()

        idx_info = await IndexedDocument.collection.index_information()

        index_names = {x.split("_")[0]: x for x in idx_info.keys()}

        # check not unique index
        assert 'name' in index_names
        assert idx_info[index_names['name']]['key'] == [('name', pymongo.DESCENDING)]
        assert idx_info[index_names['name']].get('unique', None) is None

        # check not unique index
        assert 'age' in index_names
        assert idx_info[index_names['age']]['key'] == [('age', pymongo.ASCENDING)]
        assert idx_info[index_names['age']].get('unique', None) is None

        # check unique index
        assert 'height' in index_names
        assert idx_info[index_names['height']]['key'] == [('height', pymongo.DESCENDING)]
        assert idx_info[index_names['height']]['unique'] == True

    loop_runner(run_async)
