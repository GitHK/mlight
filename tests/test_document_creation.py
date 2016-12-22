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


class CreatedDocumentModel(MetaModel):
    session = db_session
    __model__ = 'created_document'

    _id = FieldProperty(ObjectId, if_missing=ObjectId)

    name = FieldProperty(str, required=True, if_missing='')
    age = FieldProperty(int, required=True)
    height = FieldProperty(float)


db_session.register_model(CreatedDocumentModel)


@with_setup(setup_function, teardown_function)
def test_flush_on_object():
    async def run_async():
        obj = CreatedDocumentModel(age=30)

        await obj.flush()

        q_obj = await CreatedDocumentModel.get(obj._id)

        assert q_obj is not None, 'Expected a result, something went wrong'
        assert q_obj._id == obj._id, 'ObjectId does not match'
        assert q_obj.name == obj.name, 'name does not match'
        assert q_obj.age == obj.age, 'age does not match'

    loop_runner(run_async)


@with_setup(setup_function, teardown_function)
def test_flush_on_model():
    async def run_async():
        obj = CreatedDocumentModel(age=30, attached=True)

        await CreatedDocumentModel.flush_all()

        q_obj = await CreatedDocumentModel.get(obj._id)

        assert q_obj is not None, 'Expected a result, something went wrong'
        assert q_obj._id == obj._id, 'ObjectId does not match'
        assert q_obj.name == obj.name, 'name does not match'
        assert q_obj.age == obj.age, 'age does not match'

    loop_runner(run_async)


@with_setup(setup_function, teardown_function)
def test_flush_on_session():
    async def run_async():
        obj = CreatedDocumentModel(age=30, attached=True)

        await db_session.flush_all()

        q_obj = await CreatedDocumentModel.get(obj._id)

        assert q_obj is not None, 'Expected a result, something went wrong'
        assert q_obj._id == obj._id, 'ObjectId does not match'
        assert q_obj.name == obj.name, 'name does not match'
        assert q_obj.age == obj.age, 'age does not match'

    loop_runner(run_async)


@with_setup(setup_function, teardown_function)
def test_flush_with_no_integrity_check():
    async def run_async():
        obj = CreatedDocumentModel(age=30, attached=True)

        await obj.flush(check_integrity=False)

        q_obj = await CreatedDocumentModel.get(obj._id)

        assert q_obj is not None, 'Expected a result, something went wrong'
        assert q_obj._id == obj._id, 'ObjectId does not match'
        assert q_obj.name == obj.name, 'name does not match'
        assert q_obj.age == obj.age, 'age does not match'

    loop_runner(run_async)
