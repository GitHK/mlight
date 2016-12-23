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


class QueryDocument(MetaModel):
    session = db_session
    __model__ = 'indexed_document'

    _id = FieldProperty(ObjectId, if_missing=ObjectId)
    name = FieldProperty(str, required=True, if_missing='')
    age = FieldProperty(int, required=True)
    height = FieldProperty(float)


db_session.register_model(QueryDocument)


@with_setup(setup_function, teardown_function)
def test_query_document_get():
    obj = QueryDocument(age=1231231)

    async def run_async():
        await obj.flush()
        query_obj = await QueryDocument.get(obj._id)

        assert obj._id == query_obj._id, '_id field should match'
        assert obj.name == query_obj.name, 'name field should match'
        assert obj.age == query_obj.age, 'age field should match'
        assert obj.height == query_obj.height, 'height field should match'

    loop_runner(run_async)


@with_setup(setup_function, teardown_function)
def test_query_find():
    obj1 = QueryDocument(age=8716868)
    obj2 = QueryDocument(name='saassasa', age=12313, height=123.)

    def check_objects(obj, query_obj):
        assert obj._id == query_obj._id, '_id field should match'
        assert obj.name == query_obj.name, 'name field should match'
        assert obj.age == query_obj.age, 'age field should match'
        assert obj.height == query_obj.height, 'height field should match'

    async def run_async():
        await obj1.flush()
        await obj2.flush()

        results = await QueryDocument.find()

        result1 = results[0]
        result2 = results[1]

        if obj1._id == result1._id:
            check_objects(obj1, result1)
            check_objects(obj2, result2)
        else:
            check_objects(obj1, result2)
            check_objects(obj2, result1)

    loop_runner(run_async)


@with_setup(setup_function, teardown_function)
def test_query_collection_find():
    obj1 = QueryDocument(age=8716868)
    obj2 = QueryDocument(name='saassasa', age=12313, height=123.)

    def check_objects(obj, query_obj):
        assert obj._id == query_obj._id, '_id field should match'
        assert obj.name == query_obj.name, 'name field should match'
        assert obj.age == query_obj.age, 'age field should match'
        assert obj.height == query_obj.height, 'height field should match'

    async def run_async():
        await obj1.flush()
        await obj2.flush()

        cursor = QueryDocument.collection.find()
        results = await QueryDocument.to_mapped_list(cursor)

        result1 = results[0]
        result2 = results[1]

        if obj1._id == result1._id:
            check_objects(obj1, result1)
            check_objects(obj2, result2)
        else:
            check_objects(obj1, result2)
            check_objects(obj2, result1)

    loop_runner(run_async)

    # query a document update it and save it in the session!
