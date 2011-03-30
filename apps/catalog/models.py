import datetime
from django.db import models


class Product(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    meta_description = models.TextField(max_length=255, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='products')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_from = models.DateTimeField(auto_now_add=True, editable=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('product_detail', (), {'slug': self.slug})

    def deactivate(self):
        self.is_active = False
        self.deactivated_at = datetime.datetime.now()
        self.save()
