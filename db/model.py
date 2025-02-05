from neomodel import StructuredNode, StringProperty, IntegerProperty, Relationship


class VkUserNode(StructuredNode):
    __label__ = "VkUser"
    uid = IntegerProperty(unique_index=True)
    first_name = StringProperty(fulltext_index=True)
    last_name = StringProperty(fulltext_index=True)

    friends = Relationship("db.model.VkUserNode", "HAS_FRIEND")
    country = Relationship("db.model.CountryNode", "LIVES_IN")
    city = Relationship("db.model.CityNode", "LIVES_IN")

    class Meta:
        unique_identifier = 'uid'


class CountryNode(StructuredNode):
    __label__ = "Country"
    name = StringProperty(unique_index=True)

    class Meta:
        unique_identifier = 'name'


class CityNode(StructuredNode):
    __label__ = "City"
    name = StringProperty(unique_index=True)

    class Meta:
        unique_identifier = 'name'