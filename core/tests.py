from django.test import TestCase
from .utils import extract_data_from_line


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
