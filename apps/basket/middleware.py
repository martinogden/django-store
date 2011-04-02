from basket.models import Basket


class BasketMiddleware(object):

    def process_request(self, request):
        # Auto create session basket if it doesn't already exist
        if 'basket' not in request.session:
            request.session['basket'] = Basket.objects.create()
