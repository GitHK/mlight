from collections import deque

from bson import ObjectId
from weakreflist.weakreflist import WeakList

from mlight.attributes import FieldProperty
from mlight.session import DBSession
from mlight.utils import classproperty, DataDict


class MetaModel:
    """
    Used to define the model of the class that will be instantiated to create  a mapping
    with the document in the database.

    """

    # error messages
    __messages__ = dict(
        err_missing_attribute="Error: unexpected missing attribute '%s'",
        err_unexpected_attribute="Error: attribute '%s' type is %s, expected %s",
        provide_valid_model="Must provide a model name",
        provide_valid_session="Must provide a valid session",
        missing_attribute="Missing attribute: '%s'",
        types_do_not_match="Types do not match for field '%s': provided %s, expected %s",
        missing_id_field="Missing '_id' field of type %s"
    )

    # collection name to be mapped on the database
    __model__ = None

    # Store the current database session needed to operate
    session = None

    # define keys with pymongo syntax
    indexes = []

    # define unique keys with pymongo syntax
    unique_indexes = []

    to_flush = WeakList()

    @classmethod
    async def flush_all(cls, check_integrity=True):
        """ Called by the ORM to sync the object to the database. """
        for obj in cls.to_flush:
            await obj.flush(check_integrity)
            cls.to_flush.remove(obj)

    async def flush(self, check_integrity=True):
        """
        Update the single document by writing its properties to the database.
        Disable check_integrity if you need additional performance, at your own risk!
        """
        if check_integrity:
            field_properties = self.field_properties
            for key, value in self.__dict__.items():
                if key not in field_properties:
                    raise AttributeError(self.__messages__['err_missing_attribute'] % key)

                attribute_type = type(value)
                if attribute_type is not field_properties[key].data_type:
                    raise TypeError(self.__messages__['err_unexpected_attribute'] % (
                        key, attribute_type, field_properties[key].data_type))

        await self.collection.update_one({'_id': self._id}, {'$set': self.__dict__}, upsert=True)
        self.clear()

    @classmethod
    def clear_all(cls):
        """ Remove all objects from the flushing list. """
        for obj in cls.to_flush:
            cls.to_flush.remove(obj)

    def clear(self):
        """ Remove object from the flushing list. """
        self.__class__.to_flush.remove(self)

    @classmethod
    async def create_indexes(cls):
        """
        Register when the session starts to create indexes.
        Note: indexes are never dropped only added, if indexes need to be
        removed this should be done manually.
        """
        if len(cls.indexes) > 0:
            for index in cls.indexes:
                await cls.collection.create_index(index)
        if len(cls.unique_indexes) > 0:
            for index in cls.unique_indexes:
                await cls.collection.create_index(index, unique=True)

    @property
    def field_properties(self):
        return {key: value
                for key, value in self.__class__.__dict__.items()
                if type(value) is FieldProperty}

    def __init__(self, attached=False, **kwargs):
        """
         Create an instance of the object.
        :param attached: when True the object is automatically added to the to_flush list.
        :param kwargs:
        """

        # check model name integrity
        if self.__class__.__model__ is None or type(self.__class__.__model__) is str and len(
                self.__class__.__model__) == 0:
            raise ValueError(self.__messages__['provide_valid_model'])

        if type(self.__class__.session) is not DBSession:
            raise ValueError(self.__messages__['provide_valid_session'])

        final_values = dict()

        field_properties = self.field_properties

        for fp_key, fp_value in self.field_properties.items():
            # if some values are missing set them to their defaults
            if fp_value.if_missing is not None and fp_key not in kwargs:
                kwargs[fp_key] = fp_value.if_missing() if callable(fp_value.if_missing) else fp_value.if_missing

            # check if attributes are missing
            if fp_value.required and fp_key not in kwargs:
                raise AttributeError(self.__messages__['missing_attribute'] % fp_key)

        for key, value in kwargs.items():
            if key in field_properties:
                # validate the data type of each field
                value_type = type(value)
                if field_properties[key].data_type is not value_type:
                    raise TypeError(self.__messages__['types_do_not_match'] % (
                        key, value_type, field_properties[key].data_type))
                final_values[key] = value

        # check for _id of type(ObjectId)
        if '_id' not in final_values and type(kwargs.get('_id', None)) is not ObjectId:
            raise AttributeError(self.__messages__['missing_id_field'] % ObjectId)

        # notifying dict!
        self.__dict__ = DataDict()
        # save final values when all checks pass
        self.__dict__.update(final_values)

        if attached:
            self.attach()

        # set callback to update object
        self.__dict__.set_callback(self.data_set_changed)

        self.__dict__.attach_enabled = True

    def data_set_changed(self):
        """ If an update should be issued. mak the object to be flushed. """
        if self not in self.__class__.to_flush and hasattr(self.__dict__, 'attach_enabled'):
            self.attach()

    def attach(self):
        """ Add the current object to the to_flush list. """
        if self not in self.__class__.to_flush:
            self.__class__.to_flush.append(self)

    def detach(self):
        """ Remove the current object from the to_flush list. """
        if self in self.__class__.to_flush:
            self.__class__.to_flush.remove(self)

    def __setattr__(self, key, value):
        self.data_set_changed()
        super(MetaModel, self).__setattr__(key, value)

    def __delattr__(self, item):
        self.data_set_changed()
        super(MetaModel, self).__delattr__(item)

    def __str__(self):
        return "<%s, %s>" % (self.__class__.__name__, self.__dict__)

    @classproperty
    def collection(cls):
        """
        :return: the motor collection object
        """
        return cls.session.database[cls.__model__]

    @classmethod
    async def get(cls, _id, attached=False):
        """
         Returnes a mapped class instance of the found object.

        :param attached: when True the object is automatically added to the to_flush list.
        :param _id: ObjectId of the element in the collection.
        :return:
        """
        result = await cls.collection.find_one({'_id': _id})
        return None if result is None else cls(**result, attached=attached)

    @classmethod
    async def to_mapped_list(cls, cursor, attached=False):
        """
        Maps each entry in the cursor to a mapped class instance.

        :param attached: when True the object is automatically added to the to_flush list.
        :param cursor:
        :return: list of database mapped objects
        """
        results = deque()
        while await cursor.fetch_next:
            results.append(cls(**cursor.next_object(), attached=attached))
        return results

    @classmethod
    async def find(cls, *args, attached=False):
        """
        Executes a find on the collection and returns a list of mapped class instances.

        :param args: list of parameters sent to the collection.find
        :return: list of database mapped objects
        """
        cursor = cls.collection.find(*args)
        return await cls.to_mapped_list(cursor, attached=attached)
