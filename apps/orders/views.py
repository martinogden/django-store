from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.base import RedirectView
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.translation import ugettext as _

from orders.models import Order, InvalidItem
from orders.utils import get_object


SUCCESS_MESSAGE = '%i %ss successfully added to your basket'
FAILURE_MESSAGE = 'There was an error adding the item(s) to your basket'


class OrderMixin(object):
    "Add or remove any item with a price attribute to the basket"

    # Set default message to an error before we check for a successful add
    message = 'error', FAILURE_MESSAGE

    def action(self, request, *args):
        """
        This method should be overriden and an action should be implemented,
            i.e. add_item or remove_item"""
        raise NotImplementedError

    def set_message(self, request):
        "Dynamically set level and content of message"
        try:
            getattr(messages, self.message[0])(request, _(self.message[1]))
        except AttributeError:
            return False

    def verify_get_params(self, request):
        "Check all required params exist in request.REQUEST"
        try:
            [request.REQUEST[param] for param in self.params]
        except (MultiValueDictKeyError, KeyError):
            return False
        else:
            return True

    def get(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER', '/')
        order_id = request.session.get('order_id')
        self.order = Order.objects.get(pk=order_id)

        if self.verify_get_params(request):
            item = get_object(request.REQUEST['ct'], request.REQUEST['pk'])
            if item:
                self.action(request, item)

        self.set_message(request)
        return HttpResponseRedirect(url)


class AddToOrderView(OrderMixin, RedirectView):
    params = ['ct', 'pk', 'q']

    def action(self, request, item):
        qty = int(request.REQUEST['q'])
        try:
            self.order.add(item, qty)
        except InvalidItem:
            return False
        else:
            self.message = 'success', SUCCESS_MESSAGE % (qty, item.__unicode__())
            return True


class RemoveFromOrderView(OrderMixin, RedirectView):
    params = ['ct', 'pk']

    def action(self, request, item):
        if self.order.remove(item):
            self.message = 'info', 'Item Removed %s' % item.__unicode__()
        else:
            self.message = 'error', 'There was a problem removing the item from your basket'
