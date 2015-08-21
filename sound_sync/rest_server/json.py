__author__ = 'nils'


class JSONPickleable:
    def __init__(self):
        pass

    def encode_json(self):
        return {parameter_name: str(parameter_value) for parameter_name, parameter_value in vars(self).iteritems()}