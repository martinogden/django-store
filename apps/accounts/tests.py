from django.test import TestCase
from django.contrib.auth.models import User

from accounts.models import Order
from basket.models import Basket
from catalog.models import Product


class AccountTest(TestCase):
    fixtures = ['auth', 'catalog']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_userprofile_is_auto_created(self):
        self.user.save()
        self.assertEqual(self.user.profile.user, self.user)

    def test_order_clones_basket(self):
        basket = Basket.objects.create()
        basket.add(Product.objects.get(pk=1), 5)
        order = Order.objects.create(user=User.objects.get(pk=1), basket=basket)
        self.assertEqual(basket.items.count(), order.items.count())
