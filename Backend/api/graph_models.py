from neomodel.properties import StringProperty, UniqueIdProperty
from neomodel.sync_.core import StructuredNode
from neomodel.sync_.relationship_manager import RelationshipTo

class GroceryNode(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    managed_by = RelationshipTo('SupplierNode', 'MANAGED_BY')

class SupplierNode(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(unique_index=True)
    manages = RelationshipTo('GroceryNode', 'MANAGES')