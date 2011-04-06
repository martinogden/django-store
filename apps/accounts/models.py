from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):

    user = models.OneToOneField('auth.User', related_name='profile')


class Address(models.Model):

    name = models.CharField(max_length=255)
    user = models.OneToOneField('auth.User', blank=True, related_name="address")
    company_name = models.CharField(max_length=255, null=True, blank=True)
    line_1 = models.CharField(max_length=255, verbose_name='Address Line 1')
    line_2 = models.CharField(max_length=255, verbose_name='Address Line 2',\
        null=True, blank=True)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=10)
    telephone = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


STATUS_CHOICES = [
    (1, 'pending'),
    (2, 'complete'),
    (0, 'cancelled')]

class Order(models.Model):
    uuid = models.CharField(max_length=40, primary_key=True, editable=False)

    user = models.ForeignKey('auth.User', related_name='orders')
    basket = models.OneToOneField('basket.Basket', unique=True,\
        related_name='order')
    items = models.ManyToManyField('basket.Item', related_name='+')

    status = models.CharField(max_length=25, choices=STATUS_CHOICES,\
        default=STATUS_CHOICES[0][1])

    def clean_fields(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        return super(Order, self).clean_fields(*args, **kwargs)


# Shortcut to User#get_profile()
User.profile = property(lambda u: u.get_profile())

@receiver(post_save, sender=Order)
def clone_order_basket(sender, instance, **kwargs):
    """
    When an order is created, the items from the associated order 
        should be associated directly with the order"""
    instance.items.add(*instance.basket.items.all())

@receiver(post_save, sender=User)
def auto_create_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender='basket.Basket')
def keep_order_synced_with_basket(sender, instance, **kwargs):
    if instance.order:
        instance.order.save()
