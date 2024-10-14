from django.urls import path
from .views import (
    WareCreateView,
    FactorInputView,
    FactorOutputView,
    InventoryValuationView,
)

urlpatterns = [
    path('wares/', WareCreateView.as_view(), name='create-ware'),
    path('inventory/input/', FactorInputView.as_view(), name='inventory-input'),
    path('inventory/output/', FactorOutputView.as_view(), name='inventory-output'),
    path('inventory/valuation/', InventoryValuationView.as_view(), name='inventory-valuation'),
]
