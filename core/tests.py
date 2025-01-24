from django.core.cache import cache
from django.test import TestCase
from .utils import extract_data_from_line, set_orders_cache

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import datetime
from .models import Client, Order, ProductOrder, Product


class TestExtractData(TestCase):
    def test_data_length(self):
        line = b'0000000088                             Terra Daniel DDS00000008360000000003     1899.0220210909\n'

        result = extract_data_from_line(line)

        self.assertEqual(len(result.user_id), 10, "user_id should have 10 characters")
        self.assertEqual(len(result.name), 45, "name should have 45 characters (including spaces)")
        self.assertEqual(len(result.order_id), 10, "order_id should have 10 characters")
        self.assertEqual(len(result.product_id), 10, "product_id should have 10 characters")
        self.assertEqual(len(result.product_value), 12, "product_value should have 12 characters (including decimal values)")
        self.assertEqual(len(result.created_at.strip()), 8, "created_at should have 8 characters")


class GetOrdersTest(APITestCase):
    def setUp(self):
        self.client_db = Client.objects.create(id=1, name="Client 1")
        self.order1 = Order.objects.create(
            id=1,
            client=self.client_db,
            created_at=datetime(2024, 1, 1)
        )
        self.order2 = Order.objects.create(
            id=2,
            client=self.client_db,
            created_at=datetime(2024, 1, 5)
        )

        self.product = Product.objects.create(
            id=101
        )

        ProductOrder.objects.create(order=self.order1, product=self.product, value=50.00)
        ProductOrder.objects.create(order=self.order2, product=self.product, value=75.00)

        set_orders_cache()

        self.url = reverse("get_orders")

    def test_get_orders_with_no_filters(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]["orders"]), 2)

    def test_get_orders_with_order_id_filter(self):
        response = self.client.get(self.url, {"order_id": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]["orders"]), 1)
        self.assertEqual(response.data[0]["orders"][0]["order_id"], 1)

    def test_get_orders_with_date_filters(self):
        response = self.client.get(self.url, {"start_date": "2024-01-01", "end_date": "2024-01-03"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]["orders"]), 1)
        self.assertEqual(response.data[0]["orders"][0]["order_id"], 1)

    def test_get_orders_with_invalid_date(self):
        response = self.client.get(self.url, {"start_date": "invalid-date"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_orders_with_no_results(self):
        response = self.client.get(self.url, {"start_date": "2025-02-01", "end_date": "2025-02-25"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        cache.delete('orders_data')
