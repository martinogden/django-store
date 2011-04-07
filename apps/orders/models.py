from django.db import models
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from orders.utils import content_type


class InvalidItem(Exception):
    def __str__(self):
        return _('An item must have a price attribute to be added to the order')


class OrderNotMutable(Exception):
    def __str__(self):
        return _('Items cannot be added to a completed order')


STATUS_CHOICES = [
    (-1, 'Cancelled'),
    (0, 'Pending'),
    (1, 'Completed')]

class Order(models.Model):

    user = models.ForeignKey('auth.User', related_name='orders',\
        null=True, blank=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __iter__(self):
        return iter(self.items.all())

    def __len__(self):
        return self.items.count()

    def __unicode__(self):
        return _('%i items(s)' % self.items.count())

    def is_mutable(self):
        return self.status == 0

    def is_empty(self):
        return self.items.count() == 0

    def add(self, product, quantity):
        """
        Add any model to the order which has a 'price' attribute

        If the item exists, increment the quantity accordingly:
            N.B the quantity can be decremented by setting quantity
            to a negative integer
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
        "Remove product from order"
        try:
            self.items.get(**{'content_type': content_type(product),
                'object_id': product.pk}).delete()
        except ObjectDoesNotExist:
            return False
        else:
            return True

    def total(self):
        "Total cost of all items in order"
        total = 0
        for item in self.items.all():
            total += item.product.price * item.quantity
        return total


class Item(models.Model):

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
        super(Item, self).save(*args, **kwargs)
        if self.quantity < 1:
            self.delete()


def is_completed_order(sender, instance, **kwargs):
    if not instance.order.is_mutable():
        raise OrderNotMutable
pre_delete.connect(is_completed_order, sender=Item)
pre_save.connect(is_completed_order, sender=Item)


@receiver(user_logged_in)
def associate_user_with_order(sender, request, user, **kwargs):
    order_id = request.session.get('order_id')
    order = Order.objects.filter(pk=order_id)
    order.update(user=user)
