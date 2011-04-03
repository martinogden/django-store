from django.contrib import admin
from catalog.models import Product


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}


admin.site.register(Product, ProductAdmin)