from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Ware, Factor
from decimal import Decimal

# Test case for the Warehouse Management System
class WarehouseManagementTestCase(TestCase):
    def setUp(self):
        # Set up the test client and create initial test data
        self.client = APIClient()
        
        # Create two wares with different cost methods: FIFO and Weighted Mean
        self.ware_fifo = Ware.objects.create(name="Widget FIFO", cost_method="fifo")
        self.ware_weighted = Ware.objects.create(name="Widget Weighted", cost_method="weighted_mean")

    # Test the creation of a new Ware
    def test_create_ware(self):
        # Test case: Creating a new ware with a unique name should succeed
        response = self.client.post('/api/wares/', {'name': 'Widget A', 'cost_method': 'fifo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ware.objects.count(), 3)  # There should now be 3 wares
        self.assertEqual(response.data['name'], 'Widget A')
        self.assertEqual(response.data['cost_method'], 'fifo')

        # Test case: Creating a ware with a duplicate name should fail due to the unique constraint
        response_duplicate = self.client.post('/api/wares/', {'name': 'Widget A', 'cost_method': 'fifo'}, format='json')
        self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response_duplicate.data)  # Error should be related to the name field

    # Test input (add stock) transaction for a ware using FIFO cost method
    def test_input_transaction_fifo(self):
        response = self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Ensure that the input transaction was recorded correctly
        self.assertEqual(Factor.objects.filter(ware=self.ware_fifo, type='input').count(), 1)

    # Test input transaction for a ware using Weighted Mean cost method
    def test_input_transaction_weighted(self):
        response = self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Ensure the input transaction was recorded
        self.assertEqual(Factor.objects.filter(ware=self.ware_weighted, type='input').count(), 1)

    # Test output (remove stock) transaction for a ware using FIFO
    def test_output_transaction_fifo(self):
        # First input transactions to add stock
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')

        # Output transaction to remove stock
        response = self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 120
        }, format='json')
        
        # Check that the total cost is correct for FIFO (100 units @ $20 + 20 units @ $22)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_cost'], '2440.00')

    # Test output transaction for a ware using Weighted Mean
    def test_output_transaction_weighted(self):
        # First input transactions to add stock
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')

        # Output transaction to remove stock
        response = self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 120
        }, format='json')
        
        # Calculate the weighted mean: (100 * 20 + 50 * 22) / 150 = 20.67 approx
        # Total cost for 120 units: 120 * 20.67 = 2480.00 approx
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(response.data['total_cost']), 2480.00, places=2)

    # Test insufficient stock when trying to remove more stock than available
    def test_insufficient_stock(self):
        # Attempt to remove stock when there hasn't been any input transactions
        response = self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 10
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Insufficient stock')

    # Test inventory valuation for a ware using FIFO
    def test_inventory_valuation_fifo(self):
        # Input transactions to add stock
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')

        # Output transaction to remove some stock
        self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 120
        }, format='json')

        # Valuation: 30 units left at $22.00 each
        response = self.client.get(f'/api/inventory/valuation/?ware_id={self.ware_fifo.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity_in_stock'], 30)
        self.assertEqual(float(response.data['total_inventory_value']), 660.00)  # 30 * 22.00

    # Test inventory valuation for a ware using Weighted Mean
    def test_inventory_valuation_weighted(self):
        # Input transactions to add stock
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')

        # Output transaction to remove some stock
        self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 120
        }, format='json')

        # Valuation: 30 units left with weighted mean cost
        response = self.client.get(f'/api/inventory/valuation/?ware_id={self.ware_weighted.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity_in_stock'], 30)
        self.assertAlmostEqual(float(response.data['total_inventory_value']), 620.00, places=2)  # Approximate calculation
