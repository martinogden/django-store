from django.db import models
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from basket.utils import content_type


class InvalidItem(Exception):
    def __str__(self):
        return _('An item mush have a price attribute to be added to the basket')


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
        return _('%i items(s)' % self.items.count())

    def is_mutable(self):
        try:
            self.order
        except ObjectDoesNotExist:
            return True
        else:
            return self.order.status == 'pending'

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

        item, created = self.items.get_or_create(\
            **{'content_type': content_type(product), 'object_id': product.pk,
                'defaults': {'quantity': quantity}})
        # This *should* use the models.F() NodeExpression, however it throws a 
        #   TypeError occasionally. This field is unlikely to be updated a lot, so
        #   a simple += increment should suffice
        if not created:
            item.quantity += quantity
            item.save()
        return item, created

    def remove(self, product):
        "Remove product from basket"
        try:
            self.items.get(**{'content_type': content_type(product),
                'object_id': product.pk}).delete()
        except ObjectDoesNotExist:
            return False
        else:
            return True

    def total(self):
        "Total cost of all items in basket"
        total = 0
        for item in self.items.all():
            total += item.product.price * item.quantity
        return total


class Item(models.Model):

    basket = models.ForeignKey('basket.Basket', related_name='items')

    content_type = models.ForeignKey('contenttypes.ContentType')
    object_id = models.IntegerField()
    product = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(default=0)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s x %i' % (self.product, self.quantity)

    def save(self, *args, **kwargs):
        super(Item, self).save(*args, **kwargs)
        if self.quantity < 1:
            self.delete()
