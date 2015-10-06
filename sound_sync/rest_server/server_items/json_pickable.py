class JSONPickleable:
    """
    Mixin class for every pickable object
    """
    def __init__(self):
        """
        Do nothing
        """
        pass

    def encode_json(self):
        """
        Encode all properties of the object into a JSON string except the ones that start with _
        :return: the JSON string
        """
        return {parameter_name: str(parameter_value) for parameter_name, parameter_value in vars(self).iteritems()
                if not parameter_name.startswith("_")}