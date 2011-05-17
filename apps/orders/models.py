from django.db import models, IntegrityError
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.contrib.auth.signals import user_logged_in

from orders.utils import content_type


class Order(models.Model):

    user = models.ForeignKey('auth.User', related_name='orders',\
        null=True, blank=True)

    STATUS_CHOICES = [(-1, 'Cancelled'), (0, 'Pending'), (1, 'Completed')]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __iter__(self):
        return iter(self.items.all())

    def __len__(self):
        return sum([i['quantity'] for i in self.items.values('quantity')])

    def __unicode__(self):
        return _('%i items(s)' % self.items.count())

    def is_mutable(self):
        return self.status < 1

    def is_empty(self):
        return bool(self.items.count())

    def add(self, product, quantity=1):
        """
        Add any model to the order which has a 'price' attribute.
        Quantity can be decremented by setting it to a negative integer"""

        kwargs = self.__item_kwargs(product)
        try:
            # If item exists, increment the quantity.
            item = self.items.get(**kwargs)
        except ObjectDoesNotExist:
            return self.items.create(**dict({'quantity': quantity}, **kwargs))
        else:
            item.quantity = models.F('quantity') + quantity
            return item.save()

    def remove(self, product):
        "Remove product from order"
        self.items.filter(**self.__item_kwargs(product)).delete()

    def total(self):
        "Total cost of all items in order"
        return sum([i.product.price*i.quantity for i in self.items.all()])

    def __item_kwargs(self, product):
        "Default arguments to get or create an item"
        return {'content_type': content_type(product), 'object_id': product.pk}


class Item(models.Model):

    class Meta:
        unique_together = ('content_type', 'order', 'object_id')

    order = models.ForeignKey('orders.Order', related_name='items')

    content_type = models.ForeignKey('contenttypes.ContentType')
    object_id = models.IntegerField()
    product = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(default=0)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s x %i' % (self.product, self.quantity)

    def save(self, *args, **kwargs):
        if not hasattr(self.product, 'price'):
            raise InvalidItem
        super(Item, self).save(*args, **kwargs)
        if self.pk and self.quantity < 1:
            self.delete()


class InvalidItem(Exception):

    def __str__(self):
        return _('An item must have a price attribute')


class OrderNotMutable(Exception):

    def __str__(self):
        return _('Items cannot be added to a completed order')


def is_completed_order(sender, instance, **kwargs):
    if not instance.order.is_mutable():
        raise OrderNotMutable
models.signals.pre_delete.connect(is_completed_order, sender=Item)
models.signals.pre_save.connect(is_completed_order, sender=Item)


def associate_user_with_order(sender, request, user, **kwargs):
    order_id = request.session.get('order_id')
    order = Order.objects.filter(pk=order_id)
    order.update(user=user)
user_logged_in.connect(associate_user_with_order)
