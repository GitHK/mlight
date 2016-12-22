class FieldProperty:
    def __init__(self, data_type, required=False, if_missing=None):
        """

        :param data_type:
        :param required:
        :param if_missing: callable or default value
        """
        self.data_type = data_type
        self.required = required
        self.if_missing = if_missing
