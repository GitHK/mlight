.. mlight documentation master file, created by
   sphinx-quickstart on Fri Dec 23 15:20:47 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mlight's documentation!
==================================

Light ORM like layer on top of motor. Inspired by ming.

Usage
=====

To use it obtain an instance of the `DBSession`:

.. code-block:: python

    db_session = DBSession('mongodb://localhost:27017', 'test_db')

Define a mapping to a collection:

.. code-block:: python

    class User(MetaModel):
        __model__ = 'users'
        session = db_session

        _id = FieldProperty(ObjectId, if_missing=ObjectId)

        name = FieldProperty(str, required=True)
        is_admin = FieldProperty(bool, if_missing=False)



Register the object to the `DBSesson`, this enables the session to keep track of
modified object and to save the canghes only when needed.

.. code-block:: python

    db_session.register_model(User)

Object creation can be done in 2 different ways:

- attached to the session, and the DBSession will keep track of changes and will save
    the object when `flush` or `flush_all` is called

.. code-block:: python

    obj_attached = User(name='First User', attached=True)

- detached from the session

.. code-block:: python

    obj_detached = User(name='First User')


Once all changes on the objects are done you can save the obejct n three different ways:

- calling `flush` on the object and will only save the current object

.. code-block:: python

    await obj_attached.flush()

- calling `flush_all` on the collection and will save all the objects of the specified collections that were modified

.. code-block:: python

    await User.flush_all()

- calling `flush_all` on the `DBSession` and will save all the objects in all the collections previoisly
    registered

.. code-block:: python

    await db_session.flush_all()


Query a collection
==================

Retrieve an object from a collection by id

.. code-block:: python

    user = await User.get(obj._id)


Retrieve one or more objects from a collection using find, please note that it will only accept the same arguments
as motor's/pymongo's find.

.. code-block:: python

    users = await User.find()


Raw query using motor's driver and then mapping to objects. Please note that `to_mapped_list` finally consumes the cursor.

.. code-block:: python

        cursor = User.collection.find()
        users = await User.to_mapped_list(cursor)



Index creation
==============

Please note that indexes are never removed. If removing an index from the declared list, they will never be removed
from mongo. Manual removal in that case is suggested.

.. code-block:: python

    class User(MetaModel):
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


Aiohttp example
===============

TODO :/

.. toctree::
   :maxdepth: 4

   mlight



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
