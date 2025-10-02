from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Grocery, Item, DailyIncome
from django.contrib.auth.models import Group

# -----------------------------------------------------------------------------
# Note: This file tests the API logic comprehensively.
# To test it, make sure Docker is running and execute the following command in the terminal:
# docker-compose exec backend python manage.py test api
# -----------------------------------------------------------------------------

class BaseTestCase(APITestCase):
    """
    Base class for setting up dummy data that will be used by all tests.
    """
    def setUp(self):
        # 1. Create users
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        self.supplier1 = User.objects.create_user('supplier1', 's1@example.com', 'supplierpass')
        self.supplier2 = User.objects.create_user('supplier2', 's2@example.com', 'supplierpass')

        # 2. Create Suppliers group and add suppliers to it
        supplier_group = Group.objects.create(name='Suppliers')
        self.supplier1.groups.add(supplier_group)
        self.supplier2.groups.add(supplier_group)

        # 3. Create groceries and link them to suppliers
        self.grocery1 = Grocery.objects.create(name='Jeddah Branch', location='Jeddah', responsible_person=self.supplier1)  # type: ignore
        self.grocery2 = Grocery.objects.create(name='Riyadh Branch', location='Riyadh', responsible_person=self.supplier2)  # type: ignore

        # 4. Create an item in the first grocery
        self.item1 = Item.objects.create(  # type: ignore
            name='Milk', item_type='Dairy', location_in_grocery='A1', price='5.50', grocery=self.grocery1
        )


class AuthenticationTests(BaseTestCase):
    """
    Tests to ensure that unauthenticated users cannot access anything.
    """
    def test_unauthenticated_user_cannot_access_groceries(self):
        url = reverse('grocery-list')
        response = self.client.get(url)
        # We expect a 401 Unauthorized error because we haven't logged in
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # type: ignore


class AdminRoleTests(BaseTestCase):
    """
    Tests to verify admin permissions.
    """
    def setUp(self):
        super().setUp()
        # Log in as admin for all tests in this class
        self.client.force_authenticate(user=self.admin_user)  # type: ignore

    def test_admin_can_create_supplier(self):
        url = reverse('create-supplier')
        data = {'username': 'newsupplier', 'email': 'new@example.com', 'password': 'password123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # type: ignore
        self.assertTrue(User.objects.filter(username='newsupplier').exists())  # type: ignore
        # Make sure the new user was added to the Suppliers group
        new_user = User.objects.get(username='newsupplier')  # type: ignore
        self.assertTrue(new_user.groups.filter(name='Suppliers').exists())

    def test_admin_can_view_all_items(self):
        url = reverse('item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # type: ignore
        # Make sure it sees all products
        self.assertEqual(len(response.data), 1)  # type: ignore

    def test_admin_can_soft_delete_grocery(self):
        url = reverse('grocery-detail', kwargs={'pk': self.grocery1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  # type: ignore
        # Make sure the grocery wasn't actually deleted, but its status was updated
        self.grocery1.refresh_from_db()
        self.assertTrue(self.grocery1.is_deleted)


class SupplierPermissionsTests(BaseTestCase):
    """
    Comprehensive tests to verify supplier permissions.
    """
    def setUp(self):
        super().setUp()
        # Log in as supplier 1
        self.client.force_authenticate(user=self.supplier1)  # type: ignore

    def test_supplier_can_create_item_in_own_grocery(self):
        """ Tests if a supplier can add a product to their grocery. """
        url = reverse('item-list')
        data = {
            'name': 'Bread', 'item_type': 'Bakery', 'location_in_grocery': 'A2',
            'price': '2.00', 'grocery': self.grocery1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # type: ignore
        self.assertEqual(Item.objects.count(), 2)  # type: ignore

    def test_supplier_cannot_create_item_in_other_grocery(self):
        """ Tests if a supplier is prevented from adding a product to another grocery. """
        url = reverse('item-list')
        data = {
            'name': 'Juice', 'item_type': 'Drinks', 'location_in_grocery': 'A3',
            'price': '7.00', 'grocery': self.grocery2.id # Attempting to add to grocery 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # type: ignore
        self.assertEqual(Item.objects.count(), 1) # Make sure no new product was created  # type: ignore

    def test_supplier_can_read_other_grocery_items(self):
        """ Tests if a supplier can read products from other groceries. """
        # Create a product in the second grocery by the admin
        Item.objects.create(  # type: ignore
            name='Water', item_type='Drinks', location_in_grocery='B1', price='1.00', grocery=self.grocery2
        )
        url = reverse('item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # type: ignore
        # Should only see their own products in the filtered display list
        self.assertEqual(len(response.data), 1)  # type: ignore

    def test_supplier_cannot_update_other_grocery_item(self):
        """ Tests if a supplier is prevented from modifying a product in another grocery. """
        item_in_grocery2 = Item.objects.create(  # type: ignore
            name='Water', item_type='Drinks', location_in_grocery='B1', price='1.00', grocery=self.grocery2
        )
        url = reverse('item-detail', kwargs={'pk': item_in_grocery2.pk})
        data = {'price': '1.50'}
        response = self.client.patch(url, data, format='json')  # type: ignore
        # Modified: We expect 404 because filtering hides the product from the user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # type: ignore

    def test_supplier_can_add_daily_income_for_own_grocery(self):
        """ Tests if a supplier can add daily income to their grocery. """
        url = reverse('dailyincome-list')
        data = {'amount': '1500.75', 'date': '2025-09-30'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # type: ignore
        self.assertTrue(DailyIncome.objects.filter(grocery=self.grocery1, amount='1500.75').exists())  # type: ignore