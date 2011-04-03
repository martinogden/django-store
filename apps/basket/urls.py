from django.conf.urls.defaults import patterns, url
from basket.views import AddToBasketView, RemoveFromBasketView

from basket.models import Basket

urlpatterns = patterns('',
    url(r'^add/$', AddToBasketView.as_view(), name='add_to_basket'),
    url(r'^remove/$', RemoveFromBasketView.as_view(), name='remove_from_basket'),
)
