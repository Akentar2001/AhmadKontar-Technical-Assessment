from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Grocery, Item, DailyIncome

class CustomUserAdmin(UserAdmin):
    model = User

admin.site.register(User, CustomUserAdmin)
admin.site.register(Grocery)
admin.site.register(Item)
admin.site.register(DailyIncome)