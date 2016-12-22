class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class DataDict(dict):
    """
    callback is invoked whenever update on the object is issued.
    attach_enabled is stored here, and will not figure as one of the paramters when flushing.
    """
    __slots__ = ["callback", "attach_enabled"]

    def __init__(self, *args, **kwargs):
        self.callback = None
        self.attach_enabled = False
        dict.__init__(self, *args, **kwargs)

    def set_callback(self, callback):
        self.callback = callback

    def update(self, E=None, **F):
        if self.callback is not None:
            self.callback()
        super(DataDict, self).update(E, **F)
