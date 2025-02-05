from neomodel import StructuredNode, StringProperty, IntegerProperty, Relationship

class BaseNode(StructuredNode):
    """
    Base class for all nodes in the database.
    """

    @classmethod
    def initialize_node(cls, data):
        """
        Initialize a Neomodel node, excluding attributes not defined in the model.

        Args:
            cls: The Neomodel class (e.g., User).
            data: The input dictionary.

        Returns:
            An instance of the Neomodel class.
        """
        # Get the model's defined properties
        valid_keys = set(cls.__all_properties__.keys())

        # Filter the input dictionary
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        # Initialize the node
        return cls(**filtered_data)


class VkUserNode(BaseNode):
    __label__ = "VkUser"
    uid = IntegerProperty(unique_index=True)
    first_name = StringProperty(fulltext_index=True)
    last_name = StringProperty(fulltext_index=True)

    friends = Relationship("db.model.VkUserNode", "HAS_FRIEND")
    country = Relationship("db.model.CountryNode", "LIVES_IN")
    city = Relationship("db.model.CityNode", "LIVES_IN")

    class Meta:
        unique_identifier = 'uid'


class CountryNode(BaseNode):
    __label__ = "Country"
    name = StringProperty(unique_index=True)

    class Meta:
        unique_identifier = 'name'


class CityNode(BaseNode):
    __label__ = "City"
    name = StringProperty(unique_index=True)

    class Meta:
        unique_identifier = 'name'