from decimal import Decimal

from django.test import TestCase
from django.test.client import Client

from basket.models import Basket, InvalidItem
from catalog.models import Product


class BasketTest(TestCase):
    fixtures = ['catalog']

    def setUp(self):
        self.product = Product.objects.all()[0]
        self.basket = Basket.objects.create()
        self.client = Client()

    def test_add_invalid_item_to_basket(self):
        """
        Only a model with a price attribute should be added to the basket

        We'll test this by adding a basket instance (which doesn't have a price attribute)
            to the basket
        """
        self.assertRaises(InvalidItem, self.basket.add, product=self.basket, quantity=1)

    def test_add_to_basket(self):
        self.basket.add(self.product, 1)
        self.assertNotEqual(self.basket.is_empty(), True)

    def test_remove_to_basket(self):
        self.basket.add(self.product, 1)
        self.basket.remove(self.product)
        self.assertEqual(self.basket.is_empty(), True)

    def test_is_empty(self):
        self.assertEqual(self.basket.is_empty(), True)

    def test_basket_total(self):
        self.basket.add(self.product, 1)
        self.assertNotEqual(Decimal('0'), self.basket.total())

    def test_middleware_adds_basket_to_session(self):
        response = self.client.get('/admin/')
        assert 'basket' in self.client.session
