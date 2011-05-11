from django.conf.urls.defaults import patterns, url
from orders.views import OrderView, AddItemView, RemoveItemView


urlpatterns = patterns('',
    url(r'^add/$', AddItemView.as_view(), name='add-item'),
    url(r'^remove/(?P<content_type>\d+)/(?P<object_id>\d+)/$',
        RemoveItemView.as_view(), name='remove-item'),
    url(r'$^', OrderView.as_view(), name='review'),
)
