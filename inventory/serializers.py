from rest_framework import serializers
from .models import Ware, Factor

class WareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ware
        fields = ['id', 'name', 'cost_method']

class FactorInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factor
        fields = ['id', 'ware', 'quantity', 'purchase_price', 'created_at', 'type']
        read_only_fields = ['id', 'created_at', 'type']

class FactorOutputSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class InventoryValuationSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()

class FactorOutputResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factor
        fields = ['id', 'ware', 'quantity', 'total_cost', 'created_at', 'type']
        
class InventoryValuationSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()
    quantity_in_stock = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=10, decimal_places=2)