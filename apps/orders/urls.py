from django.conf.urls.defaults import patterns, url
from orders.views import AddToOrderView, RemoveFromOrderView

from orders.models import Order

urlpatterns = patterns('',
    url(r'^add/$', AddToOrderView.as_view(), name='add_to_order'),
    url(r'^remove/$', RemoveFromOrderView.as_view(), name='remove_from_order'),
)
