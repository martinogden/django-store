import logging
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.translation import ugettext as _

from orders.models import Order, InvalidItem
from orders.utils import get_object


class OrderView(TemplateView):
    "Add or remove any item with a price attribute to the order"

    order_method_names = ['add_item', 'remove_item']
    method = None
 
    def add_item(self, request, *args, **kwargs):
        qty = int(request.POST.get('q', 1))
        try:
            self.order.add(self.item, qty)
        except InvalidItem:
            messages.error(request, _('%i %ss successfully added to your basket' % (qty, self.item)))
        else:
            messages.success(request, _('There was an error adding the item(s) to your basket'))
        return HttpResponseRedirect(self.url)

    def remove_item(self, request, *args, **kwargs):
        try:
            self.order.remove(self.item)
        except:
            messages.error(request, _('There was a problem removing the item from your basket'))
        else:
            messages.info(request, _('%s Removed' % self.item))
        return HttpResponseRedirect(self.url)

    def dispatch(self, request, *args, **kwargs):
        self.order = self.__get_order(request)
        self.url = request.META.get('HTTP_REFERER', '/products/')
    
        try:
            self.item = get_object(request.REQUEST['ct'], request.REQUEST['pk'])
        except KeyError:
            messages.error(request, _('Invalid parameters'))
            return HttpResponseRedirect(self.url)
            
        if self.method in self.order_method_names:
            handler = getattr(self, self.method)
            return handler(request, *args, **kwargs)
        return super(OrderView, self).dispatch(request, *args, **kwargs)

    def __get_order(self, request):
        "Get user's order from session"
        order_id = request.session.get('order_id', None)
        order, created = Order.objects.get_or_create(pk=order_id)
        if created:
            request.session['order_id'] = order.pk
        return order