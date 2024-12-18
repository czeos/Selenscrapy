from neomodel import StructuredNode, StringProperty, IntegerProperty, Relationship


class VkUser(StructuredNode):
    uid = IntegerProperty(unique_index=True)
    first_name = StringProperty(fulltext_index=True)
    last_name = StringProperty(fulltext_index=True)

    friends = Relationship("db.model.VkUser", "HAS_FRIEND")

    class Meta:
        unique_identifier = 'uid'
