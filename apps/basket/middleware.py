from basket.models import Basket


class BasketMiddleware(object):

    def process_request(self, request):
        # Auto create session basket if it doesn't already exist
        if 'basket_id' not in request.session:
            basket = Basket.objects.create()
            request.session['basket_id'] = basket.pk
