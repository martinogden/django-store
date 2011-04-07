from decimal import Decimal

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.urlresolvers import reverse

from orders.models import Order, Item, InvalidItem, OrderNotMutable
from orders.utils import content_type
from catalog.models import Product


class OrderTest(TestCase):
    fixtures = ['catalog', 'auth']

    def setUp(self):
        self.product = Product.objects.all()[0]
        self.order = Order.objects.create()
        self.client = Client()

    def test_add_invalid_item_to_order(self):
        """
        Only a model with a price attribute should be added to the order

        We'll test this by adding a order instance (which doesn't have a price attribute)
            to the order
        """
        self.assertRaises(InvalidItem, self.order.add, product=self.order, quantity=1)

    def test_add_to_order(self):
        self.order.add(self.product, 1)
        # order is populated
        self.assertEqual(self.order.items.count(), 1)
        # Item quantity is correct
        self.assertEqual(list(self.order)[0].quantity, 1)

    def test_add_multiple_items_to_order(self):
        self.test_add_to_order()
        self.order.add(Product.objects.get(pk=2), 2)
        self.assertEqual(len(self.order), 2)

    def test_remove_from_order(self):
        self.order.add(self.product, 1)
        self.order.remove(self.product)
        self.assertEqual(self.order.is_empty(), True)

    def test_increment_order_product(self):
        """
        Assert only be 1 item in the order after a duplicate 
            item has been added
        """
        self.order.add(self.product, 1)
        self.assertEqual(list(self.order)[0].quantity, 1)
        # Increment item quantity
        self.order.add(self.product, 1)
        self.assertEqual(list(self.order)[0].quantity, 2)
        self.assertEqual(len(self.order), 1)

    def test_decrement_order_product(self):
        "An item should be removed from the order if it's quantity drops below 1"
        self.order.add(self.product, quantity=-1)
        self.assertEquals(len(self.order), 0)

    def test_is_empty(self):
        self.assertEqual(self.order.is_empty(), True)

    def test_order_total(self):
        self.order.add(self.product, 2)
        self.assertEqual(self.product.price*2, self.order.total())

    def test_order_is_mutable(self):
        self.assertEqual(self.order.is_mutable(), True)

        # populate order
        self.order.add(self.product, 1)

        # Mark order as complete
        self.order.status = 1
        self.order.save()

        # Check order cannot be tampered with
        self.assertEqual(self.order.is_mutable(), False)
        self.assertRaises(OrderNotMutable, self.order.add, product=self.product, quantity=1)
        self.assertRaises(OrderNotMutable, self.order.remove, product=self.product)

        item = self.order.items.all()[0]
        self.assertRaises(OrderNotMutable, item.delete)

    def test_unique_item(self):
        kwargs = dict(product=self.product, quantity=1, order=self.order)
        Item.objects.create(**kwargs)
        self.assertRaises(IntegrityError, Item.objects.create, **kwargs)

    # Test HTTP requests

    def test_order_in_context(self):
        response = self.client.get('/admin/')
        assert 'order' in response.context

    def test_middleware_adds_order_to_session(self):
        response = self.client.get('/admin/')
        assert 'order_id' in self.client.session

    def test_HTTP_add_to_order(self):
        """
        Assert Correct messages level is returned to user and order is
            populated with a single item
        """
        response = self.add_item_to_order()

        self.assertTrue(response.context['messages'])
        assert 'success' in list(response.context['messages'])[0].tags.split()

        # Test order has been populated
        self.assertEqual(len(response.context['order']), 1)
        # Item quantity is correct
        self.assertEqual(list(response.context['order'])[0].quantity, 1)

    def test_HTTP_remove_from_order(self):
        """
        Assert Correct messages level is returned to user and item is
            removed from order
        """
        # Add item to order
        response = self.add_item_to_order()

        ct = content_type(self.product)
        response = self.client.get(reverse('remove_from_order'),
            {'ct': ct.pk, 'pk': self.product.pk}, follow=True)

        self.assertTrue(response.context['messages'])
        assert 'info' in list(response.context['messages'])[0].tags.split()

        # Test order has been populated
        self.assertTrue(response.context['order'].is_empty())

    def test_HTTP_doesnt_add_to_order(self):
        """
        Assert call to add order url with incorrect (empty) params returns an error
        """
        response = self.client.get(reverse('add_to_order'), follow=True)

        self.assertTrue(response.context['messages'])
        assert 'error' in list(response.context['messages'])[0].tags.split()

        # Test order hasn't been populated
        self.assertEqual(len(response.context['order']), 0)

    # Helpers
    def add_item_to_order(self):
        ct = content_type(self.product)
        return self.client.get(reverse('add_to_order'),
            {'ct': ct.pk, 'pk': self.product.pk, 'q': 1}, follow=True)
