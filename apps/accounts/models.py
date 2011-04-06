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


# Shortcut to User#get_profile()
User.profile = property(lambda u: u.get_profile())


@receiver(post_save, sender=User)
def auto_create_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
