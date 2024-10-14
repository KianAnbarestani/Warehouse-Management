# inventory/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from .models import Ware, Factor
from .serializers import (
    WareSerializer,
    FactorInputSerializer,
    FactorOutputSerializer,
    InventoryValuationSerializer,
    FactorOutputResponseSerializer,
)
from collections import deque

class WareCreateView(generics.CreateAPIView):
    queryset = Ware.objects.all()
    serializer_class = WareSerializer

class FactorInputView(APIView):
    def post(self, request):
        serializer = FactorInputSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                ware = serializer.validated_data['ware']
                quantity = serializer.validated_data['quantity']
                purchase_price = serializer.validated_data.get('purchase_price', None)
                total_cost = Decimal(quantity) * Decimal(purchase_price) if purchase_price else Decimal('0.00')

                factor = Factor.objects.create(
                    ware=ware,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    total_cost=total_cost,
                    type='input'
                )
            return Response({
                "factor_id": factor.id,
                "ware_id": factor.ware.id,
                "quantity": factor.quantity,
                "purchase_price": str(factor.purchase_price) if factor.purchase_price else None,
                "created_at": factor.created_at,
                "type": factor.type
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FactorOutputView(APIView):
    def post(self, request):
        serializer = FactorOutputSerializer(data=request.data)
        if serializer.is_valid():
            ware_id = serializer.validated_data['ware_id']
            quantity = serializer.validated_data['quantity']
            ware = get_object_or_404(Ware, id=ware_id)

            with transaction.atomic():
                stock, total_cost = calculate_output_cost(ware, quantity)
                if stock is None:
                    return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)

                factor = Factor.objects.create(
                    ware=ware,
                    quantity=quantity,
                    total_cost=total_cost,
                    type='output'
                )
            # Use the response serializer
            response_serializer = FactorOutputResponseSerializer(factor)
            return Response({
                "factor_id": factor.id,
                "ware_id": factor.ware.id,
                "quantity": factor.quantity,
                "total_cost": str(factor.total_cost),
                "created_at": factor.created_at,
                "type": factor.type
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryValuationView(APIView):
    def get(self, request):
        ware_id = request.query_params.get('ware_id')
        if not ware_id:
            return Response({"error": "ware_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        ware = get_object_or_404(Ware, id=ware_id)
        total_quantity, total_inventory_value = calculate_inventory_valuation(ware)
        
        # Prepare data for serialization
        valuation_data = {
            "ware_id": ware.id,
            "quantity_in_stock": total_quantity,
            "total_inventory_value": total_inventory_value
        }
        
        serializer = InventoryValuationSerializer(valuation_data)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

# Helper functions for cost calculations

def calculate_output_cost(ware, quantity):
    if ware.cost_method == 'fifo':
        factors = Factor.objects.filter(ware=ware, type='input').order_by('created_at')
        return calculate_fifo_cost(factors, quantity)
    elif ware.cost_method == 'weighted_mean':
        return calculate_weighted_mean_cost(ware, quantity)
    else:
        raise ValueError("Invalid cost method")

def calculate_fifo_cost(factors, quantity):
    remaining = quantity
    total_cost = Decimal('0.00')
    fifo_queue = deque(factors)

    while remaining > 0 and fifo_queue:
        factor = fifo_queue.popleft()
        available = factor.quantity
        if available <= 0:
            continue
        take = min(available, remaining)
        total_cost += take * factor.purchase_price
        remaining -= take
        factor.quantity -= take
        factor.save()

    if remaining > 0:
        # Not enough stock
        return None, None
    return quantity - remaining, total_cost

def calculate_weighted_mean_cost(ware, quantity):
    inputs = Factor.objects.filter(ware=ware, type='input')
    total_quantity = sum(f.quantity for f in inputs)
    total_cost = sum(f.quantity * f.purchase_price for f in inputs)

    if total_quantity < quantity:
        return None, None  # Insufficient stock

    average_cost = total_cost / Decimal(total_quantity)
    total_output_cost = average_cost * Decimal(quantity)

    # Do not adjust input factors' quantities
    return quantity, total_output_cost

def calculate_inventory_valuation(ware):
    if ware.cost_method == 'fifo':
        # FIFO valuation
        inputs = Factor.objects.filter(ware=ware, type='input').order_by('created_at')
        total_quantity = sum(f.quantity for f in inputs)
        total_inventory_value = sum(f.quantity * f.purchase_price for f in inputs)
    elif ware.cost_method == 'weighted_mean':
        # Weighted Mean valuation
        inputs = Factor.objects.filter(ware=ware, type='input')
        outputs = Factor.objects.filter(ware=ware, type='output')
        
        total_input_cost = sum(f.total_cost for f in inputs)
        total_output_cost = sum(f.total_cost for f in outputs)
        
        remaining_cost = total_input_cost - total_output_cost
        total_quantity = sum(f.quantity for f in inputs) - sum(f.quantity for f in outputs)
        
        if total_quantity > 0:
            average_cost = remaining_cost / Decimal(total_quantity)
            total_inventory_value = remaining_cost  # Equivalent to average_cost * total_quantity
        else:
            average_cost = Decimal('0.00')
            total_inventory_value = Decimal('0.00')
    else:
        # Handle other cost methods if any
        total_quantity = 0
        total_inventory_value = Decimal('0.00')
    
    return total_quantity, total_inventory_value
