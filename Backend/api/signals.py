from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grocery
from .graph_models import GroceryNode, SupplierNode

@receiver(post_save, sender=Grocery)
def create_or_update_grocery_node(sender, instance, created, **kwargs):
    """
    This signal creates or updates a GroceryNode and its relationship
    to a SupplierNode whenever a Grocery instance is saved.
    """
    grocery_node = GroceryNode.get_or_create({'name': instance.name})[0] # type: ignore
    
    if instance.responsible_person:
        supplier_info = {
            'username': instance.responsible_person.username,
            'email': instance.responsible_person.email,
        }
        supplier_node = SupplierNode.get_or_create(supplier_info)[0] # type: ignore
        
        if not grocery_node.managed_by.is_connected(supplier_node):
            grocery_node.managed_by.connect(supplier_node)
        if not supplier_node.manages.is_connected(grocery_node):
            supplier_node.manages.connect(grocery_node)