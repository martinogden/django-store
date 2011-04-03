from django.conf.urls.defaults import patterns, url
from django.views.generic.list import ListView

from catalog.views import ProductDetailView
from catalog.models import Product

kwargs = {
    'queryset': Product.objects.all()}

urlpatterns = patterns('',
    url(r'^products/$', ListView.as_view(paginate_by=10, **kwargs), name='product_list'),
    url(r'^product/(?P<pk>\d{1,5})-(?P<slug>[^/]+)/$', ProductDetailView.as_view(**kwargs), name='product_detail')
)
