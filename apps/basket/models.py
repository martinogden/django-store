from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist


class InvalidItem(Exception):
    def __str__(self):
        return 'An item mush have a price attribute to be added to the basket'

# Shortcut to get an items content type
content_type = lambda product: ContentType.objects.get_for_model(product)

class Basket(models.Model):

    user = models.ForeignKey('auth.User', related_name='baskets',\
        null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __iter__(self):
        return iter(self.items.all())

    def __len__(self):
        return self.items.count()

    def __unicode__(self):
        return '%i items(s)' % self.items.count()

    def is_empty(self):
        return self.items.count() is 0

    def add(self, product, quantity):
        """
        Add any model to the basket which has a 'price' attribute

        If the item exists, increment to quantity accordingly:
            N.B the quantity can be decremented by settings quantity < 0
        """
        if not hasattr(product, 'price'):
            raise InvalidItem

        product, created = self.items.get_or_create(\
            **{'content_type': content_type(product), 'object_id': product.pk,
                'defaults': {'quantity': quantity}})
        product.quantity = models.F('quantity') + quantity
        product.save()
        return product, created

    def remove(self, product):
        "Remove product from basket"
        return self.items.get(**{'content_type': content_type(product),
            'object_id': product.pk}).delete()

    def total(self):
        "Total cost of all items in basket"
        total = 0
        for item in self.items.all():
            total += item.product.price * item.quantity
        return total
            

class Item(models.Model):

    basket = models.ForeignKey('basket.Basket', related_name='items')

    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    product = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField()

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s x %i' % (self.product, self.quantity)

