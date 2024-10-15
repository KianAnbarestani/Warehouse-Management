from decimal import Decimal
from rest_framework import serializers
from .models import Ware, Factor

# Serializer for the Ware model
# This handles the creation and listing of Ware objects with their ID, name, and cost method
class WareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ware
        fields = ['id', 'name', 'cost_method']


# Serializer for input transactions (adding stock to the inventory)
# This serializer takes the ware ID, quantity, and purchase price for stock input
class FactorInputSerializer(serializers.ModelSerializer):
    # This field allows referencing Ware by its ID when performing the transaction
    # It maps the 'ware_id' from the input to the 'ware' field in the model
    ware_id = serializers.PrimaryKeyRelatedField(
        queryset=Ware.objects.all(),
        source='ware',  # Maps 'ware_id' to 'ware' in the model
        write_only=True  # This field is only used when writing data (i.e., during POST requests)
    )

    class Meta:
        model = Factor
        fields = ['ware_id', 'quantity', 'purchase_price']

    # Validates that the quantity is a positive integer
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    # Validates that the purchase price is provided and is a positive value for input transactions
    def validate_purchase_price(self, value):
        # Only enforce this rule for input transactions
        if self.context.get('request').method == 'POST':
            if self.initial_data.get('type') == 'input' and (value is None or value <= Decimal('0.00')):
                raise serializers.ValidationError("Purchase price must be a positive number for input transactions.")
        return value


# Serializer for output transactions (removing stock from the inventory)
# This serializer only requires the ware ID and quantity for stock output
class FactorOutputSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()  # ID of the ware from which stock is being removed
    quantity = serializers.IntegerField()  # Quantity of ware to be removed

    # You can add a validation function here to check if the quantity is available in stock


# Serializer for inventory valuation
# This returns the current stock level and the total value of the inventory for a given ware
class InventoryValuationSerializer(serializers.Serializer):
    ware_id = serializers.IntegerField()  # ID of the ware
    quantity_in_stock = serializers.IntegerField()  # Current quantity of ware in stock
    total_inventory_value = serializers.DecimalField(max_digits=15, decimal_places=2)  # Total value of ware in stock


# Serializer for output transaction responses
# This serializer structures the response after an output transaction is processed
class FactorOutputResponseSerializer(serializers.ModelSerializer):
    factor_id = serializers.IntegerField(source='id')  # Renaming 'id' field to 'factor_id' in the response
    ware_id = serializers.IntegerField(source='ware.id')  # Accessing the ware's ID from the foreign key

    class Meta:
        model = Factor
        fields = ['factor_id', 'ware_id', 'quantity', 'total_cost', 'created_at', 'type']
