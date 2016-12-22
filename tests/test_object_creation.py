from bson import ObjectId
from nose import with_setup

from mlight.attributes import FieldProperty
from mlight.meta_model import MetaModel
from tests.common import get_db_session, drop_all_collections, drop_database

db_session = None

MODEL_NAME = 'share'


def setup_module():
    global db_session
    db_session = get_db_session()
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
    print("Test teardown")


@with_setup(setup_function, teardown_function)
def test_missing_model():
    class ShareModel1(MetaModel):
        pass

    try:
        ShareModel1()
        assert False, 'test failed'
    except ValueError as e:
        assert type(e) is ValueError, 'error type mismatch'
        assert str(e) == ShareModel1.__messages__['provide_valid_model'], 'error message does not match'


@with_setup(setup_function, teardown_function)
def test_missing_db_session():
    class ShareModel2(MetaModel):
        __model__ = MODEL_NAME

    try:
        ShareModel2()
        assert False, 'test failed'
    except ValueError as e:
        assert type(e) is ValueError, 'error type mismatch'
        assert str(e) == ShareModel2.__messages__['provide_valid_session'], 'error message does not match'


@with_setup(setup_function, teardown_function)
def test_missing_object_id_field():
    class ShareModel3(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

    try:
        ShareModel3()
        assert False, 'test failed'
    except AttributeError as e:
        assert type(e) is AttributeError, 'error type mismatch'
        assert str(e) == ShareModel3.__messages__['missing_id_field'] % ObjectId, 'error message does not match'


@with_setup(setup_function, teardown_function)
def test_missing_object_id_default_value():
    class ShareModel4(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId)

    try:
        ShareModel4()
        assert False, 'test failed'
    except AttributeError as e:
        assert type(e) is AttributeError, 'error type mismatch'
        assert str(e) == ShareModel4.__messages__['missing_id_field'] % ObjectId, 'error message does not match'


@with_setup(setup_function, teardown_function)
def test_successful_creation_of_detached_object():
    class ShareModel5(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel5)

    obj = ShareModel5()

    assert type(obj) is ShareModel5
    assert obj not in ShareModel5.to_flush, 'object should NOT be in to_flush'


@with_setup(setup_function, teardown_function)
def test_successful_creation_of_attached_object():
    class ShareModel6(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel6)

    obj = ShareModel6(attached=True)

    assert type(obj) is ShareModel6
    assert obj in ShareModel6.to_flush, 'object should be in to_flush'


@with_setup(setup_function, teardown_function)
def test_successful_creation_unattached_and_attach_later():
    class ShareModel7(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel7)

    obj = ShareModel7()
    obj.attach()

    assert type(obj) is ShareModel7
    assert obj in ShareModel7.to_flush, 'object should be in to_flush'


@with_setup(setup_function, teardown_function)
def test_successful_creation_attached_and_detached():
    class ShareModel8(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel8)

    obj = ShareModel8(attached=True)
    obj.detach()

    assert type(obj) is ShareModel8
    assert (obj in ShareModel8.to_flush) is False, 'object should NOT be in to_flush'


@with_setup(setup_function, teardown_function)
def test_successful_creation_atacch_detach_repeated():
    class ShareModel9(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel9)

    obj = ShareModel9()
    for x in range(10):
        obj.attach()
        obj.detach()

    assert type(obj) is ShareModel9
    assert (obj in ShareModel9.to_flush) is False, 'object should NOT be in to_flush'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_attached_multiple_times():
    class ShareModel10(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel10)

    obj = ShareModel10()
    obj.attach()
    obj.attach()
    obj.attach()
    obj.attach()
    obj.attach()
    obj.attach()
    obj.attach()

    assert type(obj) is ShareModel10
    assert len(ShareModel10.to_flush) == 1, 'expected 1 item'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_attached_and_detach_multiple_times():
    class ShareModel11(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel11)

    obj = ShareModel11(attached=True)
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()

    assert type(obj) is ShareModel11
    assert len(ShareModel11.to_flush) == 0, 'expected 0 items'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_detached_and_detach_multiple_times():
    class ShareModel12(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

    db_session.register_model(ShareModel12)

    obj = ShareModel12()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()
    obj.detach()

    assert type(obj) is ShareModel12
    assert len(ShareModel12.to_flush) == 0, 'expected 0 items'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_with_no_arguments_field_property():
    class ShareModel13(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str)

    db_session.register_model(ShareModel13)

    obj = ShareModel13()

    assert 'name' not in obj.__dict__, 'name field is not mandatory'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_with_mandatory_field_property_name():
    VALUE = 'asdsajsdajasd'

    class ShareModel14(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str, required=True)

    db_session.register_model(ShareModel14)

    obj = ShareModel14(name=VALUE)

    assert type(obj.name) is str, 'type should be matching'
    assert obj.name is VALUE, 'values do not match'
    assert 'name' in obj.__dict__, 'name field is not mandatory'


@with_setup(setup_function, teardown_function)
def test_failiure_creation_object_with_mandatory_field_property_():
    class ShareModel15(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str, required=True)

    db_session.register_model(ShareModel15)

    try:
        ShareModel15()
        assert False, 'test failed'
    except AttributeError as e:
        assert str(e) == ShareModel15.__messages__['missing_attribute'] % 'name'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_with_if_missing_field_property():
    VALUE = 'ciaoso'

    class ShareModel16(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str, if_missing=VALUE)

    db_session.register_model(ShareModel16)

    obj = ShareModel16()

    assert type(obj.name) is str, 'type should be matching'
    assert obj.name is VALUE, 'values do not match'
    assert 'name' in obj.__dict__, 'name field is not mandatory'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_with_if_missing_and_required_field_property():
    VALUE = 'ciaoso'

    class ShareModel17(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str, required=True, if_missing=VALUE)

    db_session.register_model(ShareModel17)

    obj = ShareModel17()

    assert type(obj.name) is str, 'type should be matching'
    assert obj.name is VALUE, 'values do not match'
    assert 'name' in obj.__dict__, 'name field is not mandatory'


@with_setup(setup_function, teardown_function)
def test_successful_creation_object_ignoring_extra_fields():
    NAME_VALUE = 'ajkdsajkhdasjkhadshjk'

    class ShareModel18(MetaModel):
        __model__ = MODEL_NAME
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str, required=True)

    db_session.register_model(ShareModel18)

    obj = ShareModel18(name=NAME_VALUE, other_field='not_present')

    assert type(obj.name) is str, 'type should be matching'
    assert obj.name is NAME_VALUE, 'values do not match'
    assert 'other_field' not in obj.__dict__, 'unexpected field'
    assert 'name' in obj.__dict__, 'name field is not mandatory'
    assert len(obj.__dict__) == 2, 'expected only 2 field'
