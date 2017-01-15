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
        return {parameter_name: str(parameter_value) for parameter_name, parameter_value in vars(self).items()
                if not parameter_name.startswith("_")}

    @staticmethod
    def fill_with_json(instance, json_dict):
        """
        Fill a non-empty object with the information provided in the dict and set all attributes in the instance
        to their corresponding values in the dict.
        :param instance: A non-zero instance of an arbitrary object
        :param json_dict: A dictionary with keys with the same names as the attributes of the instance
        """
        if instance:
            for parameter_name in vars(instance):
                if parameter_name in json_dict:
                    setattr(instance, parameter_name, json_dict[parameter_name])