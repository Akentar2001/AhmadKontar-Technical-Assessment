from typing import Literal


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):

    pass

class Grocery(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_groceries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # type: ignore

    def __str__(self) -> str:
        return str(self.name)

class Item(models.Model):
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=100)
    location_in_grocery = models.CharField(max_length=255, verbose_name="Item Location")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    grocery = models.ForeignKey(Grocery, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # type: ignore

    def __str__(self) -> str:
        return f"{self.name} in {self.grocery.name}"

class DailyIncome(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    grocery = models.ForeignKey(Grocery, on_delete=models.CASCADE, related_name='incomes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # type: ignore

    class Meta:
        unique_together = ('grocery', 'date')

    def __str__(self) -> str:
        return f"Income for {self.grocery.name} on {self.date}"