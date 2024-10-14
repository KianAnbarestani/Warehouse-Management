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