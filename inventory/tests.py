from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Ware, Factor
from decimal import Decimal

class WarehouseManagementTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create Wares
        self.ware_fifo = Ware.objects.create(name="Widget FIFO", cost_method="fifo")
        self.ware_weighted = Ware.objects.create(name="Widget Weighted", cost_method="weighted_mean")

    def test_create_ware(self):
        response = self.client.post('/api/wares/', {'name': 'Widget A', 'cost_method': 'fifo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ware.objects.count(), 3)
        self.assertEqual(response.data['name'], 'Widget A')
        self.assertEqual(response.data['cost_method'], 'fifo')

    def test_input_transaction_fifo(self):
        response = self.client.post('/api/inventory/input/', {
            'ware': self.ware_fifo.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Factor.objects.filter(ware=self.ware_fifo, type='input').count(), 1)

    def test_input_transaction_weighted(self):
        response = self.client.post('/api/inventory/input/', {
            'ware': self.ware_weighted.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Factor.objects.filter(ware=self.ware_weighted, type='input').count(), 1)

    def test_output_transaction_fifo(self):
        # Input transactions
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_fifo.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_fifo.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')
        # Output transaction
        response = self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 120
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_cost'], '2440.00')

    def test_output_transaction_weighted(self):
        # Input transactions
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_weighted.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_weighted.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')
        # Output transaction
        response = self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 120
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Weighted mean cost: (100*20 + 50*22) / 150 = 20.666...
        # Total cost for 120: 20.666... * 120 = 2480.00
        self.assertAlmostEqual(float(response.data['total_cost']), 2480.00, places=2)

    def test_insufficient_stock(self):
        response = self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 10
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Insufficient stock')

    def test_inventory_valuation_fifo(self):
        # Input transactions
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_fifo.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_fifo.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')
        # Output transaction
        self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_fifo.id,
            'quantity': 120
        }, format='json')
        # Valuation
        response = self.client.get(f'/api/inventory/valuation/?ware_id={self.ware_fifo.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity_in_stock'], 30)
        self.assertEqual(float(response.data['total_inventory_value']), 660.00)  # 30 * 22.00

    def test_inventory_valuation_weighted(self):
    # Input transactions
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_weighted.id,
            'quantity': 100,
            'purchase_price': '20.00'
        }, format='json')
        self.client.post('/api/inventory/input/', {
            'ware': self.ware_weighted.id,
            'quantity': 50,
            'purchase_price': '22.00'
        }, format='json')
        # Output transaction
        self.client.post('/api/inventory/output/', {
            'ware_id': self.ware_weighted.id,
            'quantity': 120
        }, format='json')
        # Valuation
        response = self.client.get(f'/api/inventory/valuation/?ware_id={self.ware_weighted.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity_in_stock'], 30)
        self.assertAlmostEqual(float(response.data['total_inventory_value']), 620.00, places=2)
