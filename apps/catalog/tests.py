from django.test import TestCase
from catalog.models import Product


class CatalogTest(TestCase):
    fixtures = ['catalog']

    def setUp(self):
        self.product = Product.objects.all()[0]

    def test_deactivate(self):
        """
        Test that product deactivates
        """
        self.assertEqual(self.product.is_active, True)
        self.product.deactivate()
        self.assertEqual(self.product.is_active, False)
