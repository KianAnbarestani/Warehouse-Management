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
    FactorOutputResponseSerializer,  # New Serializer
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
                ware = get_object_or_404(Ware, id=serializer.validated_data['ware'].id)
                quantity = serializer.validated_data['quantity']
                purchase_price = serializer.validated_data['purchase_price']
                total_cost = Decimal(quantity) * Decimal(purchase_price)

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
                "purchase_price": str(factor.purchase_price),  # Ensure string
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
                "ware_id": ware.id,
                "quantity": factor.quantity,
                "total_cost": str(factor.total_cost),  # Convert Decimal to string
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
        stock, total_value = calculate_inventory_valuation(ware)
        
        return Response({
            "ware_id": ware.id,
            "quantity_in_stock": stock,
            "total_inventory_value": str(total_value)  # Convert Decimal to string
        }, status=status.HTTP_200_OK)

# Helper functions for cost calculations

def calculate_output_cost(ware, quantity):
    factors = Factor.objects.filter(ware=ware, type='input').order_by('created_at')
    if ware.cost_method == 'fifo':
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
    total_quantity = sum([f.quantity for f in inputs])
    total_cost = sum([f.quantity * f.purchase_price for f in inputs])

    if total_quantity < quantity:
        return None, None

    average_cost = total_cost / Decimal(total_quantity)
    total_output_cost = average_cost * Decimal(quantity)

    # Update quantities
    remaining = quantity
    for factor in inputs:
        if remaining <= 0:
            break
        available = factor.quantity
        take = min(available, remaining)
        factor.quantity -= take
        factor.save()
        remaining -= take

    return quantity - remaining, total_output_cost

def calculate_inventory_valuation(ware):
    if ware.cost_method == 'fifo':
        # For FIFO, sum the remaining input quantities
        inputs = Factor.objects.filter(ware=ware, type='input').order_by('created_at')
        total_quantity = sum([f.quantity for f in inputs])
        total_value = sum([f.quantity * f.purchase_price for f in inputs])
    elif ware.cost_method == 'weighted_mean':
        # For Weighted Mean, calculate based on remaining inputs
        inputs = Factor.objects.filter(ware=ware, type='input')
        total_quantity = sum([f.quantity for f in inputs])
        total_cost = sum([f.quantity * f.purchase_price for f in inputs])
        if total_quantity > 0:
            average_cost = total_cost / Decimal(total_quantity)
            total_value = average_cost * Decimal(total_quantity)
        else:
            total_value = Decimal('0.00')
    else:
        total_quantity = 0
        total_value = Decimal('0.00')
    
    return total_quantity, total_value
