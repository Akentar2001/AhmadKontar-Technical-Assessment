from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroceryViewSet, ItemViewSet, CreateSupplierView, DailyIncomeViewSet

router = DefaultRouter()
router.register(r'groceries', GroceryViewSet, basename='grocery')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'daily-incomes', DailyIncomeViewSet, basename='dailyincome')

urlpatterns = [
    path('', include(router.urls)),
    path('create-supplier/', CreateSupplierView.as_view(), name='create-supplier'),
]