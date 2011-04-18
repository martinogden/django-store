from django.conf.urls.defaults import patterns, url
from orders.views import OrderView

from orders.models import Order

urlpatterns = patterns('',
    url(r'^add/$', OrderView.as_view(method='add_item'), name='add-item'),
    url(r'^remove/$', OrderView.as_view(method='remove_item'), name='remove-item'),
)
