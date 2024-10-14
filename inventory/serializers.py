# inventory/serializers.py

from decimal import Decimal
from rest_framework import serializers
from .models import Ware, Factor

class WareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ware
        fields = ['id', 'name', 'cost_method']

class FactorInputSerializer(serializers.ModelSerializer):
    ware_id = serializers.PrimaryKeyRelatedField(
        queryset=Ware.objects.all(),
        source='ware',
        write_only=True
    )
    
    class Meta:
        model = Factor
        fields = ['ware_id', 'quantity', 'purchase_price']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value
    
    def validate_purchase_price(self, value):
        if self.initial_data.get('type') == 'input' and (value is None or value <= Decimal('0.00')):
            raise serializers.ValidationError("Purchase price must be a positive number for input transactions.")
        return value

class FactorOutputSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class InventoryValuationSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()
    quantity_in_stock = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=15, decimal_places=2)

class FactorOutputResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factor
        fields = ['id', 'ware', 'quantity', 'total_cost', 'created_at', 'type']
