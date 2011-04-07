from django.contrib import messages
from django.utils.translation import ugettext as _

from orders.models import Order


def order(request):
    """
    Get current users order or create a new one if it has expired
    """
    if 'order_id' in request.session:
        try:
            order_id = request.session.get('order_id')
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist: 
            order = Order.objects.create()
            request.session['order_id'] = order.pk
            messages.error(request, _('Oops, your session has expired, your order is now empty'))
        return {
            'order': order
        }
