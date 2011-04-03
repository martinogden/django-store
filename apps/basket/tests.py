from decimal import Decimal

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from basket.models import Basket, InvalidItem
from basket.utils import content_type
from catalog.models import Product
from accounts.models import Order


class BasketTest(TestCase):
    fixtures = ['catalog', 'auth']

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
        # basket is populated
        self.assertEqual(self.basket.items.count(), 1)
        # Item quantity is correct
        self.assertEqual(list(self.basket)[0].quantity, 1)

    def test_add_multiple_items_to_basket(self):
        self.test_add_to_basket()
        self.basket.add(Product.objects.get(pk=2), 2)
        self.assertEqual(len(self.basket), 2)

    def test_remove_from_basket(self):
        self.basket.add(self.product, 1)
        self.basket.remove(self.product)
        self.assertEqual(self.basket.is_empty(), True)

    def test_increment_basket_product(self):
        """
        Assert only be 1 item in the basket after a duplicate 
            item has been added
        """
        self.basket.add(self.product, 1)
        self.assertEqual(list(self.basket)[0].quantity, 1)
        # Increment item quantity
        self.basket.add(self.product, 1)
        self.assertEqual(list(self.basket)[0].quantity, 2)
        self.assertEqual(len(self.basket), 1)

    def test_decrement_basket_product(self):
        "An item should be removed from the basket if it's quantity drops below 1"
        self.basket.add(self.product, quantity=-1)
        self.assertEquals(len(self.basket), 0)

    def test_is_empty(self):
        self.assertEqual(self.basket.is_empty(), True)

    def test_basket_total(self):
        self.basket.add(self.product, 1)
        self.assertNotEqual(Decimal('0'), self.basket.total())

    def test_basket_is_mutable(self):
        self.assertEqual(self.basket.is_mutable(), True)

        # Create order
        user = User.objects.get(pk=1)
        order = Order.objects.create(basket=self.basket, user=user)
        self.assertEqual(self.basket.is_mutable(), True)

        # Make order complete
        order.status = 2
        order.save()
        self.assertNotEqual(self.basket.is_mutable(), False)

    # Test HTTP requests

    def test_basket_in_context(self):
        response = self.client.get('/admin/')
        assert 'basket' in response.context

    def test_middleware_adds_basket_to_session(self):
        response = self.client.get('/admin/')
        assert 'basket_id' in self.client.session

    def test_HTTP_add_to_basket(self):
        """
        Assert Correct messages level is returned to user and basket is
            populated with a single item
        """
        response = self.add_item_to_basket()

        self.assertTrue(response.context['messages'])
        assert 'success' in list(response.context['messages'])[0].tags.split()

        # Test basket has been populated
        self.assertEqual(len(response.context['basket']), 1)
        # Item quantity is correct
        self.assertEqual(list(response.context['basket'])[0].quantity, 1)

    def test_HTTP_remove_from_basket(self):
        """
        Assert Correct messages level is returned to user and item is
            removed from basket
        """
        # Add item to basket
        response = self.add_item_to_basket()

        ct = content_type(self.product)
        response = self.client.get(reverse('remove_from_basket'),
            {'ct': ct.pk, 'pk': self.product.pk}, follow=True)

        self.assertTrue(response.context['messages'])
        assert 'info' in list(response.context['messages'])[0].tags.split()

        # Test basket has been populated
        self.assertTrue(response.context['basket'].is_empty())

    def test_HTTP_doesnt_add_to_basket(self):
        """
        Assert call to add basket url with incorrect (empty) params returns an error
        """
        response = self.client.get(reverse('add_to_basket'), follow=True)

        self.assertTrue(response.context['messages'])
        assert 'error' in list(response.context['messages'])[0].tags.split()

        # Test basket hasn't been populated
        self.assertEqual(len(response.context['basket']), 0)

    # Helpers
    def add_item_to_basket(self):
        ct = content_type(self.product)
        return self.client.get(reverse('add_to_basket'),
            {'ct': ct.pk, 'pk': self.product.pk, 'q': 1}, follow=True)
