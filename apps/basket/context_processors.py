from django.contrib import messages
from django.utils.translation import ugettext as _

from basket.models import Basket


def basket(request):
    try:
        basket_id = request.session.get('basket_id')
        basket = Basket.objects.get(pk=basket_id)
    except Basket.DoesNotExist: 
        basket = Basket.objects.create()
        request.session['basket_id'] = basket.pk
        messages.error(request, _('Oops, your session has expired, and basket is now empty'))
    return {
        'basket': basket
    }
