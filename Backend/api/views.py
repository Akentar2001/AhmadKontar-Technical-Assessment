from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.contrib.auth.models import Group
from .models import User, Grocery, Item, DailyIncome
from .serializers import UserSerializer, AdminUserSerializer, GrocerySerializer, ItemSerializer, DailyIncomeSerializer
from .permissions import IsAdminOrIsOwner


# --- User Creation Views ---
class CreateSupplierView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        user = serializer.save()
        try:
            supplier_group = Group.objects.get(name='Suppliers')
            user.groups.add(supplier_group)
        except Group.DoesNotExist: # type: ignore
            pass

class CreateAdminView(generics.CreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        user = serializer.save(is_staff=True)
        try:
            admin_group = Group.objects.get(name='Admins')
            user.groups.add(admin_group)
        except Group.DoesNotExist: # type: ignore
            pass

# --- Main Application ViewSets ---

class GroceryViewSet(viewsets.ModelViewSet):
    serializer_class = GrocerySerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]

    def get_queryset(self):
        # Admin sees all groceries, supplier sees only their assigned grocery
        if self.request.user.is_staff:
            return Grocery.objects.filter(is_deleted=False) # type: ignore
        return Grocery.objects.filter(responsible_person=self.request.user, is_deleted=False) # type: ignore

    def perform_create(self, serializer):
        # Only admins can create groceries
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create groceries.")
        serializer.save()

    def perform_update(self, serializer):
        # Update the updated_at field
        serializer.save()

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]

    def get_queryset(self):
        # Admin sees all items, supplier sees only items from their grocery
        if self.request.user.is_staff:
            return Item.objects.filter(is_deleted=False) # type: ignore
        return Item.objects.filter(grocery__responsible_person=self.request.user, is_deleted=False) # type: ignore

    def perform_create(self, serializer):
        # Suppliers can only add items to their own grocery
        user = self.request.user
        
        # If user is not admin, ensure they're adding to their own grocery
        if not user.is_staff:
            # Get the grocery for this supplier
            try:
                supplier_grocery = Grocery.objects.get(responsible_person=user, is_deleted=False) # type: ignore
            except Grocery.DoesNotExist: # type: ignore
                raise PermissionDenied("You are not assigned to any grocery.")
            
            # If grocery is specified in request, verify it's their grocery
            requested_grocery = serializer.validated_data.get('grocery')
            if requested_grocery and requested_grocery != supplier_grocery:
                raise PermissionDenied("You can only add items to your assigned grocery.")
            
            # Set the grocery to their assigned one if not specified
            if not requested_grocery:
                serializer.validated_data['grocery'] = supplier_grocery
        
        serializer.save()
        
    def perform_update(self, serializer):
        # Update the updated_at field
        serializer.save()
        
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class DailyIncomeViewSet(viewsets.ModelViewSet):
    serializer_class = DailyIncomeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]

    def get_queryset(self):
        # Admin sees all incomes, supplier sees only their grocery's incomes
        if self.request.user.is_staff:
            return DailyIncome.objects.filter(is_deleted=False) # type: ignore
        return DailyIncome.objects.filter(grocery__responsible_person=self.request.user, is_deleted=False) # type: ignore

    def perform_create(self, serializer):
        user = self.request.user
        date = serializer.validated_data['date']
        
        # Admins can specify any grocery, suppliers are restricted to their own
        if user.is_staff:
            # Admin can create income for any grocery
            serializer.save()
        else:
            # Supplier can only create income for their assigned grocery
            try:
                supplier_grocery = Grocery.objects.get(responsible_person=user, is_deleted=False) # type: ignore
            except Grocery.DoesNotExist: # type: ignore
                raise PermissionDenied("You are not assigned to any grocery.")
            
            # Check if income for this date already exists
            if DailyIncome.objects.filter(grocery=supplier_grocery, date=date, is_deleted=False).exists(): # type: ignore
                raise PermissionDenied("Income for this date already exists.")
            
            serializer.save(grocery=supplier_grocery)
            
    def perform_update(self, serializer):
        # Update the updated_at field
        serializer.save()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()